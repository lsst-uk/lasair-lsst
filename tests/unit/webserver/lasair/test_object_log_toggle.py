"""Unit tests for the styling of the Log scale toggle on the light curve in lasair/apps/object/utils.py."""
import os
import sys
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../webserver')))

from plotly.basedatatypes import BaseFigure

from lasair.apps.object.utils import object_difference_lightcurve
from test_object_lightcurve import make_object_data

IDLE_TEXT = '#374151'
IDLE_BORDER = '#9ca3af'


def make_data_with_forced_sources():
    objectData = make_object_data()
    objectData['diaForcedSources'] = [
        {'midpointMjdTai': 60000.5, 'psfFlux': 280.0, 'psfFluxErr': 30.0, 'band': 'g'},
        {'midpointMjdTai': 60004.5, 'psfFlux': 240.0, 'psfFluxErr': 30.0, 'band': 'r'},
    ]
    return objectData


def build_figure(forced):
    # RETURN THE FIGURE ITSELF IN PLACE OF ITS HTML, SO THE TEST CAN READ THE LAYOUT
    with mock.patch.object(BaseFigure, 'to_html', lambda self, **kwargs: self):
        fig, _ = object_difference_lightcurve(make_data_with_forced_sources(), forced=forced)
    return fig


class LogToggleStyleTest(unittest.TestCase):

    def test_idle_toggle_has_dark_text_white_fill_and_a_visible_border(self):
        for forced in (False, True):
            with self.subTest(forced=forced):
                # ACT
                menu = build_figure(forced).layout.updatemenus[0]

                # ASSERT
                self.assertEqual(menu.font.color.lower(), IDLE_TEXT)
                self.assertEqual(menu.bgcolor.lower(), '#ffffff')
                self.assertEqual(menu.bordercolor.lower(), IDLE_BORDER)
                self.assertGreaterEqual(menu.borderwidth, 1)

    def test_toggle_starts_off_because_the_axes_start_linear(self):
        # ACT
        menu = build_figure(False).layout.updatemenus[0]

        # ASSERT
        self.assertEqual(menu.active, -1)
        self.assertFalse(menu.showactive)

    def test_first_click_switches_to_log_and_shows_a_distinct_active_style(self):
        # ARRANGE
        button = build_figure(False).layout.updatemenus[0].buttons[0]

        # ACT
        turnOn = button.args[0]

        # ASSERT
        self.assertEqual(turnOn['yaxis.type'], 'log')
        self.assertEqual(turnOn['yaxis2.type'], 'log')
        self.assertNotEqual(turnOn['updatemenus[0].bgcolor'].lower(), '#ffffff')
        self.assertNotEqual(turnOn['updatemenus[0].font.color'].lower(), IDLE_TEXT)

    def test_second_click_returns_to_linear_and_restores_the_idle_style(self):
        # ARRANGE
        button = build_figure(False).layout.updatemenus[0].buttons[0]

        # ACT
        turnOff = button.args2[0]

        # ASSERT
        self.assertEqual(turnOff['yaxis.type'], 'linear')
        self.assertEqual(turnOff['yaxis2.type'], 'linear')
        self.assertEqual(turnOff['updatemenus[0].bgcolor'].lower(), '#ffffff')
        self.assertEqual(turnOff['updatemenus[0].font.color'].lower(), IDLE_TEXT)
        self.assertEqual(turnOff['updatemenus[0].bordercolor'].lower(), IDLE_BORDER)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
