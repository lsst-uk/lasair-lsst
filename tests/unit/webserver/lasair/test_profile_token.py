"""Render tests for the API token card on the profile page (users/profile.html)."""
import json
import os
import re
import sys
import tempfile
import types
import unittest
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

import context  # noqa: F401  PATCHES sys.path

WEBSERVER_ROOT = Path(__file__).resolve().parents[4] / 'webserver'
TEMPLATES_ROOT = WEBSERVER_ROOT / 'users' / 'templates'
SITE_TEMPLATES_ROOT = WEBSERVER_ROOT / 'lasair' / 'templates'
TOKEN = 'a1b2c3d4e5f60718293a4b5c6d7e8f9012345678'
MASK = '•' * 40
STUB_BASE = (
    '{% block title %}{% endblock %}{% block stylesheets %}{% endblock %}'
    '{% block content %}{% endblock %}{% block javascripts %}{% endblock %}')


def configure_django():
    """Configure a minimal Django that can render the profile template on its own."""
    import django
    from django.conf import settings
    from django.urls import path

    if settings.configured:
        return
    baseDir = tempfile.mkdtemp()
    os.makedirs(os.path.join(baseDir, 'layouts'))
    with open(os.path.join(baseDir, 'layouts', 'base.html'), 'w') as handle:
        handle.write(STUB_BASE)
    urlModule = types.ModuleType('profile_token_urls')
    urlModule.urlpatterns = []
    sys.modules['profile_token_urls'] = urlModule
    settings.configure(
        DEBUG=False,
        SECRET_KEY='test',
        ROOT_URLCONF='profile_token_urls',
        INSTALLED_APPS=['crispy_forms', 'crispy_bootstrap5', 'widget_tweaks'],
        CRISPY_ALLOWED_TEMPLATE_PACKS='bootstrap5',
        CRISPY_TEMPLATE_PACK='bootstrap5',
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            # THE STUB BASE IN baseDir MUST WIN OVER THE REAL layouts/base.html
            'DIRS': [baseDir, str(TEMPLATES_ROOT), str(SITE_TEMPLATES_ROOT)],
            'APP_DIRS': True,
            'OPTIONS': {'context_processors': []},
        }])
    django.setup()
    urlModule.urlpatterns = [path('hidden/', lambda request: None, name='hidden_objects')]


class TagCollector(HTMLParser):
    """Collect every start tag that has an id, keyed by that id, plus the text inside it."""

    def __init__(self):
        super().__init__()
        self.tags = {}
        self.text = {}
        self._open = []

    def handle_starttag(self, tag, attrs):
        attrMap = dict(attrs)
        if 'id' in attrMap:
            self.tags[attrMap['id']] = (tag, attrMap)
            self.text[attrMap['id']] = ''
            self._open.append(attrMap['id'])

    def handle_endtag(self, tag):
        if self._open and self.tags[self._open[-1]][0] == tag:
            self._open.pop()

    def handle_data(self, data):
        for tagId in self._open:
            self.text[tagId] += data


def render_profile(token):
    """Render the profile page for a logged-in user holding the given token and return the HTML."""
    from django import forms
    from django.template.loader import render_to_string
    from django.test import RequestFactory

    class UserForm(forms.Form):
        first_name = forms.CharField()
        last_name = forms.CharField()
        email = forms.EmailField()
        username = forms.CharField()

    class ProfileForm(forms.Form):
        image = forms.ImageField(required=False)

    request = RequestFactory().get('/profile/')
    request.user = SimpleNamespace(
        first_name='Ada', last_name='Lovelace', username='ada',
        email='ada@example.com', profile=SimpleNamespace(image_b64=''))
    templateContext = {'u_form': UserForm(), 'p_form': ProfileForm(), 'token': token}
    return render_to_string('users/profile.html', templateContext, request=request)


class RenderedPage:
    """The profile HTML plus an index of its tags by id and the markup outside script elements."""

    def __init__(self, html):
        self.html = html
        self.visibleHtml = re.sub(r'<script\b.*?</script>', '', html, flags=re.DOTALL)
        collector = TagCollector()
        collector.feed(html)
        self.tags = collector.tags
        self.text = collector.text


class TestProfileTokenCard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configure_django()

    def test_raw_token_absent_from_markup_outside_script_elements(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))

        # ASSERT
        self.assertNotIn(token, page.visibleHtml)

    def test_token_display_shows_fixed_length_mask(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))

        # ASSERT
        self.assertEqual(MASK, page.text['api-token-display'].strip())

    def test_reveal_button_is_accessible_toggle_button(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))
        tag, attrs = page.tags['api-token-toggle']

        # ASSERT
        self.assertEqual('button', tag)
        self.assertEqual('button', attrs['type'])
        self.assertEqual('false', attrs['aria-pressed'])

    def test_reveal_button_has_one_fixed_label(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))
        attrs = page.tags['api-token-toggle'][1]

        # ASSERT
        self.assertEqual('Show API token', attrs['aria-label'])
        self.assertNotIn('Hide API token', page.html)

    def test_copy_button_is_accessible_button_separate_from_reveal(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))
        tag, attrs = page.tags['api-token-copy']

        # ASSERT
        self.assertEqual('button', tag)
        self.assertEqual('button', attrs['type'])
        self.assertTrue(attrs['aria-label'].strip())
        self.assertNotEqual(
            page.tags['api-token-toggle'][1]['aria-label'], attrs['aria-label'])

    def test_buttons_are_hidden_until_the_script_enables_them(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))

        # ASSERT
        for buttonId in ('api-token-toggle', 'api-token-copy'):
            self.assertIn('d-none', page.tags[buttonId][1]['class'].split())

    def test_copy_feedback_region_is_a_live_status(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))
        attrs = page.tags['api-token-copy-status'][1]

        # ASSERT
        self.assertEqual('status', attrs['role'])
        self.assertEqual('', page.text['api-token-copy-status'].strip())

    def test_token_available_only_through_json_script_element(self):
        # ARRANGE
        token = TOKEN

        # ACT
        page = RenderedPage(render_profile(token))
        tag, attrs = page.tags['api-token']
        match = re.search(
            r'<script id="api-token" type="application/json">(.*?)</script>',
            page.html, flags=re.DOTALL)

        # ASSERT
        self.assertEqual('script', tag)
        self.assertEqual('application/json', attrs['type'])
        self.assertEqual(token, json.loads(match.group(1)))
        self.assertEqual(1, page.html.count(token))


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
