"""View tests for regenerating the API token from the profile page (users.views.regenerate_token)."""
import sys
import types
import unittest
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

import context  # noqa: F401  PATCHES sys.path

WEBSERVER_ROOT = Path(__file__).resolve().parents[4] / 'webserver'
REGENERATE_URL = '/profile/token/regenerate/'
PROFILE_URL = '/profile/'
LOGIN_URL = '/login/'
CSRF_URL = '/csrf/'
SUCCESS_MESSAGE = (
    'Your API token has been regenerated. The old token no longer works. '
    'Update any scripts that use it.')


def configure_django():
    """Configure Django with an in-memory database and import the real view module."""
    import django
    from django.conf import settings
    from django.http import HttpResponse
    from django.middleware.csrf import get_token
    from django.urls import path

    # EACH TEST FILE MUST RUN IN ITS OWN PROCESS (AS JENKINS DOES) BECAUSE THEY CONFIGURE DJANGO DIFFERENTLY
    if settings.configured:
        return
    # users.views IMPORTS users.forms, WHICH PULLS IN Profile (Pillow, static files), reCAPTCHA AND CRISPY
    sys.modules['users.forms'] = types.SimpleNamespace(
        UserRegisterForm=None, ProfileUpdateForm=None, UserUpdateForm=None)
    sys.path.insert(0, str(WEBSERVER_ROOT))
    urlModule = types.ModuleType('regenerate_token_urls')
    urlModule.urlpatterns = []
    sys.modules['regenerate_token_urls'] = urlModule
    settings.configure(
        DEBUG=False,
        SECRET_KEY='test',
        ROOT_URLCONF='regenerate_token_urls',
        ALLOWED_HOSTS=['testserver'],
        LOGIN_URL=LOGIN_URL,
        MEDIA_URL='/media/',
        MEDIA_ROOT='/tmp/lasair-test-media',
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
        INSTALLED_APPS=[
            'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
            'django.contrib.messages', 'rest_framework.authtoken'],
        MIDDLEWARE=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware'],
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {'context_processors': []},
        }])
    django.setup()
    from users import views
    urlModule.urlpatterns = [
        path('profile/', lambda request: HttpResponse('profile'), name='profile'),
        path('login/', lambda request: HttpResponse('login'), name='login'),
        path('csrf/', lambda request: HttpResponse(get_token(request)), name='csrf'),
        path('profile/token/regenerate/', views.regenerate_token, name='regenerate_token'),
    ]


class RegenerateTokenTestCase(TestCase):
    """Shared fixtures: two users with tokens and a client that enforces CSRF checks."""

    @classmethod
    def setUpClass(cls):
        configure_django()
        call_command('migrate', verbosity=0, interactive=False)
        super().setUpClass()

    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.test import Client
        from rest_framework.authtoken.models import Token
        self.tokenModel = Token
        self.user = get_user_model().objects.create_user(username='ada', password='pw')
        self.otherUser = get_user_model().objects.create_user(username='bob', password='pw')
        self.oldKey = Token.objects.create(user=self.user).key
        self.otherKey = Token.objects.create(user=self.otherUser).key
        self.client = Client(enforce_csrf_checks=True)

    def _login(self):
        self.client.force_login(self.user)

    def _post_with_csrf(self):
        """POST to the regenerate URL with a CSRF token fetched the way the browser gets it."""
        csrfToken = self.client.get(CSRF_URL).content.decode()
        return self.client.post(REGENERATE_URL, {'csrfmiddlewaretoken': csrfToken})


class TestRegenerateToken(RegenerateTokenTestCase):

    def test_post_replaces_the_key_and_the_old_key_no_longer_exists(self):
        # ARRANGE
        self._login()

        # ACT
        self._post_with_csrf()
        newKey = self.tokenModel.objects.get(user=self.user).key

        # ASSERT
        self.assertNotEqual(self.oldKey, newKey)
        self.assertFalse(self.tokenModel.objects.filter(key=self.oldKey).exists())

    def test_user_keeps_exactly_one_token_after_regenerating(self):
        # ARRANGE
        self._login()

        # ACT
        self._post_with_csrf()

        # ASSERT
        self.assertEqual(1, self.tokenModel.objects.filter(user=self.user).count())

    def test_other_users_token_is_untouched(self):
        # ARRANGE
        self._login()

        # ACT
        self._post_with_csrf()

        # ASSERT
        self.assertEqual(self.otherKey, self.tokenModel.objects.get(user=self.otherUser).key)

    def test_post_redirects_to_profile_with_success_message(self):
        # ARRANGE
        self._login()

        # ACT
        response = self._post_with_csrf()
        messageTexts = [str(message) for message in response.wsgi_request._messages]

        # ASSERT
        self.assertEqual(302, response.status_code)
        self.assertEqual(PROFILE_URL, response['Location'])
        self.assertEqual([SUCCESS_MESSAGE], messageTexts)

    def test_message_does_not_contain_the_new_key(self):
        # ARRANGE
        self._login()

        # ACT
        response = self._post_with_csrf()
        newKey = self.tokenModel.objects.get(user=self.user).key
        messageTexts = [str(message) for message in response.wsgi_request._messages]

        # ASSERT
        self.assertFalse(any(newKey in text for text in messageTexts))

    def test_get_returns_405_and_changes_nothing(self):
        # ARRANGE
        self._login()

        # ACT
        response = self.client.get(REGENERATE_URL)

        # ASSERT
        self.assertEqual(405, response.status_code)
        self.assertEqual(self.oldKey, self.tokenModel.objects.get(user=self.user).key)

    def test_post_without_csrf_token_is_forbidden_and_changes_nothing(self):
        # ARRANGE
        self._login()

        # ACT
        response = self.client.post(REGENERATE_URL)

        # ASSERT
        self.assertEqual(403, response.status_code)
        self.assertEqual(self.oldKey, self.tokenModel.objects.get(user=self.user).key)

    def test_anonymous_post_redirects_to_login_and_changes_nothing(self):
        # ARRANGE
        keysBefore = sorted(self.tokenModel.objects.values_list('key', flat=True))

        # ACT
        response = self._post_with_csrf()
        keysAfter = sorted(self.tokenModel.objects.values_list('key', flat=True))

        # ASSERT
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].startswith(LOGIN_URL))
        self.assertEqual(keysBefore, keysAfter)

    def test_url_resolves_to_the_view_in_the_real_users_urlconf(self):
        # ARRANGE
        from django.urls import resolve
        from users import views

        # ACT
        match = resolve(REGENERATE_URL, urlconf='users.urls')

        # ASSERT
        self.assertIs(views.regenerate_token, match.func)
        self.assertEqual('regenerate_token', match.url_name)


class TestOldTokenStopsWorking(RegenerateTokenTestCase):
    """After regeneration the API authentication classes reject the old key and accept the new one."""

    def _regenerate(self):
        self._login()
        self._post_with_csrf()
        return self.tokenModel.objects.get(user=self.user).key

    def _query_request(self, key):
        from rest_framework.request import Request
        from rest_framework.test import APIRequestFactory
        return Request(APIRequestFactory().get('/api/query/', {'token': key}))

    def test_token_authentication_rejects_the_old_key(self):
        # ARRANGE
        from rest_framework.authentication import TokenAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        self._regenerate()

        # ACT / ASSERT
        with self.assertRaises(AuthenticationFailed):
            TokenAuthentication().authenticate_credentials(self.oldKey)

    def test_token_authentication_accepts_the_new_key(self):
        # ARRANGE
        from rest_framework.authentication import TokenAuthentication
        newKey = self._regenerate()

        # ACT
        user, token = TokenAuthentication().authenticate_credentials(newKey)

        # ASSERT
        self.assertEqual(self.user, user)
        self.assertEqual(newKey, token.key)

    def test_query_authentication_rejects_the_old_key(self):
        # ARRANGE
        from lasairapi.query_auth import QueryAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        self._regenerate()

        # ACT / ASSERT
        with self.assertRaises(AuthenticationFailed):
            QueryAuthentication().authenticate(self._query_request(self.oldKey))

    def test_query_authentication_accepts_the_new_key(self):
        # ARRANGE
        from lasairapi.query_auth import QueryAuthentication
        newKey = self._regenerate()

        # ACT
        user, token = QueryAuthentication().authenticate(self._query_request(newKey))

        # ASSERT
        self.assertEqual(self.user, user)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
