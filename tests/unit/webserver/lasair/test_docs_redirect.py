"""Unit tests for the old /api and /contact routes that now redirect to the documentation."""
import sys
import unittest
from pathlib import Path

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'webserver'))

DEVELOP_DOCS = 'https://lasair-lsst.readthedocs.io/en/develop'
MAIN_DOCS = 'https://lasair-lsst.readthedocs.io/en/main'


def configure_django():
    from django.conf import settings

    # EACH TEST FILE MUST RUN IN ITS OWN PROCESS (AS JENKINS DOES) BECAUSE THEY CONFIGURE DJANGO DIFFERENTLY
    if not settings.configured:
        settings.configure(DEBUG=False, SECRET_KEY='test', DEV_DOCS=True, LASAIR_GRAFANA_URL='')


configure_django()

from django.test import RequestFactory, override_settings

from lasair.docs_redirect import DocsRedirectView


def redirect_for(docsPage):
    request = RequestFactory().get('/old-page')
    return DocsRedirectView.as_view(docsPage=docsPage)(request)


class DocsRedirectViewTest(unittest.TestCase):

    @override_settings(DEV_DOCS=True)
    def test_redirects_to_the_develop_docs_when_dev_docs_is_on(self):
        # ACT
        response = redirect_for('core_functions/rest-api.html')

        # ASSERT
        self.assertEqual(response.url, f'{DEVELOP_DOCS}/core_functions/rest-api.html')

    @override_settings(DEV_DOCS=False)
    def test_redirects_to_the_main_docs_when_dev_docs_is_off(self):
        # ACT
        response = redirect_for('more_info/contact.html')

        # ASSERT
        self.assertEqual(response.url, f'{MAIN_DOCS}/more_info/contact.html')

    def test_redirect_is_temporary(self):
        # ACT
        response = redirect_for('more_info/contact.html')

        # ASSERT
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
