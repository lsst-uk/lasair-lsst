"""Unit tests for the page_title template filter that builds every browser tab title."""
import unittest

import context  # noqa: F401  PATCHES sys.path

from django.template import Context, Engine
from templatetags.customtags import page_title

# A MINIMAL ENGINE THAT LOADS customtags THE SAME WAY THE BASE LAYOUTS DO
ENGINE = Engine(libraries={'customtags': 'templatetags.customtags'})
TITLE_TEMPLATE = '{% load customtags %}<title>{% filter page_title %}{{ name }}{% endfilter %}</title>'


class PageTitleTest(unittest.TestCase):
    """Tests for the page_title template filter."""

    def test_adds_the_site_name_after_the_page_title(self):
        # ACT
        title = page_title('Schema Browser')

        # ASSERT
        self.assertEqual(title, 'Schema Browser · Lasair')

    def test_returns_only_the_site_name_when_the_title_is_empty(self):
        # ACT
        title = page_title('')

        # ASSERT
        self.assertEqual(title, 'Lasair')

    def test_treats_a_whitespace_only_title_as_empty(self):
        # ACT
        title = page_title('\n    \n')

        # ASSERT
        self.assertEqual(title, 'Lasair')

    def test_collapses_the_whitespace_of_an_indented_title_block(self):
        # ACT
        title = page_title('\n    Watchlist:\n    Demo watchlist\n')

        # ASSERT
        self.assertEqual(title, 'Watchlist: Demo watchlist · Lasair')

    def test_keeps_a_user_chosen_name_escaped_when_rendered(self):
        # ARRANGE
        template = ENGINE.from_string(TITLE_TEMPLATE)

        # ACT
        html = template.render(Context({'name': '<script>alert(1)</script>'}))

        # ASSERT
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt; · Lasair', html)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
