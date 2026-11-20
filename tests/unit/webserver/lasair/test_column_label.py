"""Unit tests for the column header labels and tooltips of the shared results table."""
import unittest

import context  # noqa: F401  PATCHES sys.path

from templatetags.customtags import column_label, column_tooltip

# THE DATATABLE JS SORTS BY THESE HEADINGS, SO NO LABEL MAY TAKE ONE OF THESE NAMES
JS_SORT_HEADINGS = ("objectId", "Created")


class ColumnLabelTest(unittest.TestCase):
    """Tests for the column_label template filter."""

    def test_labels_ra_with_its_unit(self):
        # ACT
        label = column_label('ra')

        # ASSERT
        self.assertEqual(label, 'RA (deg)')

    def test_labels_decl_as_dec_with_its_unit(self):
        # ACT
        label = column_label('decl')

        # ASSERT
        self.assertEqual(label, 'Dec (deg)')

    def test_labels_band_flux_with_the_band_and_unit(self):
        # ACT
        labels = [column_label(f'{band}_psfFlux') for band in 'ugrizy']

        # ASSERT
        self.assertEqual(labels, [
            'u flux (nJy)', 'g flux (nJy)', 'r flux (nJy)',
            'i flux (nJy)', 'z flux (nJy)', 'y flux (nJy)'])

    def test_labels_latest_flux_with_its_unit(self):
        # ACT
        label = column_label('latest_psfFlux')

        # ASSERT
        self.assertEqual(label, 'Latest flux (nJy)')

    def test_labels_cone_id(self):
        # ACT
        label = column_label('cone_id')

        # ASSERT
        self.assertEqual(label, 'Cone ID')

    def test_labels_utc_as_alert_time(self):
        # ACT
        label = column_label('UTC')

        # ASSERT
        self.assertEqual(label, 'Alert time (UTC)')

    def test_keeps_the_dia_object_id_name(self):
        # ACT
        label = column_label('diaObjectId')

        # ASSERT
        self.assertEqual(label, 'diaObjectId')

    def test_returns_an_unknown_key_unchanged(self):
        # ARRANGE
        userAlias = 'my favourite column'

        # ACT
        label = column_label(userAlias)

        # ASSERT
        self.assertEqual(label, userAlias)

    def test_returns_already_readable_headings_unchanged(self):
        # ACT
        labels = [column_label(k) for k in (
            'Catalogue ID', 'separation (arcsec)', 'last detected (days ago)')]

        # ASSERT
        self.assertEqual(labels, [
            'Catalogue ID', 'separation (arcsec)', 'last detected (days ago)'])

    def test_never_labels_a_column_with_a_heading_the_datatable_js_sorts_by(self):
        # ARRANGE
        knownKeys = ['ra', 'decl', 'cone_id', 'UTC', 'latest_psfFlux', 'classdict',
                     'objectId', 'Created'] + [f'{b}_psfFlux' for b in 'ugrizy']

        # ACT
        labels = [column_label(k) for k in knownKeys if k not in JS_SORT_HEADINGS]

        # ASSERT
        self.assertFalse(set(labels) & set(JS_SORT_HEADINGS))

    def test_leaves_the_js_sort_headings_unlabelled(self):
        # ACT
        labels = [column_label(k) for k in JS_SORT_HEADINGS]

        # ASSERT
        self.assertEqual(labels, list(JS_SORT_HEADINGS))


class ColumnTooltipTest(unittest.TestCase):
    """Tests for the column_tooltip template filter."""

    def test_puts_the_column_name_before_the_description(self):
        # ARRANGE
        schema = {'ra': 'Mean RA of this object'}

        # ACT
        tooltip = column_tooltip(schema, 'ra')

        # ASSERT
        self.assertEqual(tooltip, 'ra: Mean RA of this object')

    def test_shows_just_the_column_name_when_the_key_has_no_description(self):
        # ACT
        tooltip = column_tooltip({'ra': 'Mean RA'}, 'my_alias')

        # ASSERT
        self.assertEqual(tooltip, 'my_alias')

    def test_shows_just_the_column_name_when_the_description_is_empty(self):
        # ACT
        tooltip = column_tooltip({'ra': ''}, 'ra')

        # ASSERT
        self.assertEqual(tooltip, 'ra')

    def test_shows_just_the_column_name_when_there_is_no_schema(self):
        # ACT
        tooltip = column_tooltip('', 'ra')

        # ASSERT
        self.assertEqual(tooltip, 'ra')


if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
