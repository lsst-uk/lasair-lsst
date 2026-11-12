"""Unit tests for the top-axis layout of the light curve in lasair/apps/object/utils.py."""
import os
import sys
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../webserver')))

from plotly.basedatatypes import BaseFigure

from lasair.apps.object.utils import LIGHTCURVE_LEGEND_Y_STANDARD, object_difference_lightcurve


def make_object_data():
    sources = [
        {'diaSourceId': 1, 'midpointMjdTai': 60000.5, 'mjd': 60000.5, 'psfFlux': 300.0, 'psfFluxErr': 30.0, 'band': 'g'},
        {'diaSourceId': 2, 'midpointMjdTai': 60004.5, 'mjd': 60004.5, 'psfFlux': 250.0, 'psfFluxErr': 30.0, 'band': 'r'},
        {'diaSourceId': 3, 'midpointMjdTai': 60010.5, 'mjd': 60010.5, 'psfFlux': 150.0, 'psfFluxErr': 30.0, 'band': 'i'},
    ]
    return {'diaObjectId': '123', 'diaSources': sources, 'diaForcedSources': []}


def build_standard_figure():
    # RETURN THE FIGURE ITSELF IN PLACE OF ITS HTML, SO THE TEST CAN READ THE LAYOUT
    with mock.patch.object(BaseFigure, 'to_html', lambda self, **kwargs: self):
        fig, _ = object_difference_lightcurve(make_object_data(), forced=False)
    return fig


class LightcurveTopAxisTest(unittest.TestCase):

    def test_utc_title_is_the_top_axis_title_not_an_annotation(self):
        # ACT
        fig = build_standard_figure()

        # ASSERT
        self.assertEqual(fig.layout.xaxis2.title.text, 'UTC Time')
        self.assertNotIn('UTC Time', [a.text for a in fig.layout.annotations])

    def test_standard_legend_sits_above_the_top_axis(self):
        # ACT
        fig = build_standard_figure()

        # ASSERT
        self.assertEqual(fig.layout.legend.yanchor, 'bottom')
        self.assertEqual(fig.layout.legend.y, LIGHTCURVE_LEGEND_Y_STANDARD)
        self.assertGreater(fig.layout.legend.y, 1.0)

    def test_date_ticks_are_a_plain_list_for_the_page_script(self):
        # ACT
        fig = build_standard_figure()

        # ASSERT
        self.assertIsInstance(fig.to_plotly_json()['layout']['xaxis']['tickvals'], list)
        self.assertEqual(len(fig.layout.xaxis2.tickvals), len(fig.layout.xaxis2.ticktext))


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
