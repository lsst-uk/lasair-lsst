"""Unit tests for the DeltaRA/DeltaDec offset scatter plot in lasair/apps/object/utils.py."""
import json
import math
import os
import sys
import unittest
from unittest import mock

import context  # noqa: F401  PATCHES sys.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../webserver')))

from lasair.apps.object.utils import (
    ARCSEC_PER_DEGREE,
    LIGHTCURVE_AXIS_TICKS,
    SCATTER_HEIGHT,
    SCATTER_LEGEND_Y,
    SCATTER_MARGIN_BOTTOM,
    SCATTER_MARGIN_BOTTOM_NO_NOTE,
    SCATTER_RANGE_ARCSEC,
    UNKNOWN_BAND_COLOR,
    bandColors,
    bands,
    bandSymbols,
    build_offset_scatter_figure,
    compute_source_offsets,
    make_offset_band_traces,
    object_offset_scatter,
    object_offset_scatter_or_none,
    split_offsets_by_range,
)

ARCSEC = 1.0 / ARCSEC_PER_DEGREE
# FALLBACK HEIGHT; THE OBJECT PAGE RESIZES THE FIGURE TO THE CARD WIDTH
EXPECTED_SCATTER_HEIGHT = 360
# LINE HEIGHT OF THE 11 PX NOTE TEXT UNDER THE PLOT
NOTE_LINE_HEIGHT_PX = 15


def make_source(ra, decl, band='g', diaSourceId=1000, mjd=60000.5):
    return {
        'diaSourceId': diaSourceId,
        'ra': ra,
        'decl': decl,
        'band': band,
        'midpointMjdTai': mjd,
    }


def make_object_data(ra, decl, sources, forcedSources=None):
    return {
        'diaObjectId': '123',
        'objectData': {'ra': ra, 'decl': decl},
        'diaSources': sources,
        'diaForcedSources': forcedSources or [],
    }


def plotted_points(fig):
    """Return (x, y) pairs for every band trace in the figure."""
    points = []
    for trace in fig.data:
        if trace.showlegend:
            points.extend(zip(trace.x, trace.y))
    return points


class TestComputeSourceOffsets(unittest.TestCase):

    def test_dec_offset_of_one_arcsec_gives_y_of_one(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0 + ARCSEC)]

        # ACT
        offsets = compute_source_offsets(10.0, 20.0, sources)

        # ASSERT
        self.assertAlmostEqual(offsets[0]['dRa'], 0.0, places=6)
        self.assertAlmostEqual(offsets[0]['dDec'], 1.0, places=6)

    def test_ra_offset_is_scaled_by_cos_of_object_dec(self):
        # ARRANGE
        sources = [make_source(10.0 + 2 * ARCSEC, 60.0)]

        # ACT
        offsets = compute_source_offsets(10.0, 60.0, sources)

        # ASSERT
        self.assertAlmostEqual(offsets[0]['dRa'], 1.0, places=4)

    def test_ra_wrap_forward_across_zero_gives_small_positive_offset(self):
        # ARRANGE
        sources = [make_source(0.0001, 60.0)]

        # ACT
        offsets = compute_source_offsets(359.9999, 60.0, sources)

        # ASSERT
        expected = 0.0002 * 3600.0 * math.cos(math.radians(60.0))
        self.assertAlmostEqual(offsets[0]['dRa'], expected, places=4)

    def test_ra_wrap_backward_across_zero_gives_small_negative_offset(self):
        # ARRANGE
        sources = [make_source(359.9999, 60.0)]

        # ACT
        offsets = compute_source_offsets(0.0001, 60.0, sources)

        # ASSERT
        expected = -0.0002 * 3600.0 * math.cos(math.radians(60.0))
        self.assertAlmostEqual(offsets[0]['dRa'], expected, places=4)

    def test_carries_id_mjd_and_band_through(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0, band='r', diaSourceId=777, mjd=60123.25)]

        # ACT
        offsets = compute_source_offsets(10.0, 20.0, sources)

        # ASSERT
        self.assertEqual(offsets[0]['diaSourceId'], 777)
        self.assertEqual(offsets[0]['mjd'], 60123.25)
        self.assertEqual(offsets[0]['band'], 'r')

    def test_skips_sources_without_a_position(self):
        # ARRANGE
        sources = [make_source(None, None), make_source(10.0, 20.0)]

        # ACT
        offsets = compute_source_offsets(10.0, 20.0, sources)

        # ASSERT
        self.assertEqual(len(offsets), 1)


class TestSplitOffsetsByRange(unittest.TestCase):

    def test_separates_points_beyond_limit_on_either_axis(self):
        # ARRANGE
        limit = SCATTER_RANGE_ARCSEC
        inside = [{'dRa': 0.0, 'dDec': 0.0}, {'dRa': limit, 'dDec': -limit}]
        outside = [{'dRa': limit + 0.1, 'dDec': 0.0}, {'dRa': 0.0, 'dDec': -(limit + 0.1)}]

        # ACT
        inRange, outsideRange = split_offsets_by_range(inside[:1] + outside + inside[1:])

        # ASSERT
        self.assertEqual(inRange, inside)
        self.assertEqual(outsideRange, outside)

    def test_returns_two_empty_lists_for_empty_input(self):
        # ARRANGE
        offsets = []

        # ACT
        result = split_offsets_by_range(offsets)

        # ASSERT
        self.assertEqual(result, ([], []))


class TestMakeOffsetBandTraces(unittest.TestCase):

    def test_makes_one_legend_trace_per_present_band(self):
        # ARRANGE
        offsets = [
            {'diaSourceId': 1, 'mjd': 1.0, 'band': 'r', 'dRa': 0.0, 'dDec': 0.0},
            {'diaSourceId': 2, 'mjd': 2.0, 'band': 'r', 'dRa': 1.0, 'dDec': 1.0},
        ]

        # ACT
        traces = make_offset_band_traces(offsets)

        # ASSERT
        self.assertEqual([trace.name for trace in traces], ['r-band'])
        self.assertEqual(len(traces[0].x), 2)


class TestBuildOffsetScatterFigure(unittest.TestCase):

    def test_plots_source_at_offset_position(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0 + ARCSEC)])

        # ACT
        fig, outsideCount = build_offset_scatter_figure(objectData)

        # ASSERT
        (x, y), = plotted_points(fig)
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertAlmostEqual(y, 1.0, places=6)
        self.assertEqual(outsideCount, 0)

    def test_forced_photometry_is_not_plotted(self):
        # ARRANGE
        forced = [make_source(10.0 + ARCSEC, 20.0, diaSourceId=5), make_source(10.0, 20.0 + ARCSEC, diaSourceId=6)]
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)], forcedSources=forced)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(len(plotted_points(fig)), 1)

    def test_band_traces_use_light_curve_colours_and_legend(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0, band=band, diaSourceId=i) for i, band in enumerate(bands)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        bandTraces = [trace for trace in fig.data if trace.showlegend]
        self.assertEqual([trace.name for trace in bandTraces], [band + '-band' for band in bands])
        self.assertEqual([trace.marker.color for trace in bandTraces], bandColors)
        self.assertEqual([trace.marker.symbol for trace in bandTraces], bandSymbols)
        self.assertTrue(fig.layout.showlegend)

    def test_axes_are_fixed_and_equal_aspect(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        limit = SCATTER_RANGE_ARCSEC
        # RA RUNS EAST TO THE LEFT, SO THE X AXIS IS DISPLAYED REVERSED
        self.assertEqual(tuple(fig.layout.xaxis.range), (limit, -limit))
        self.assertEqual(tuple(fig.layout.yaxis.range), (-limit, limit))
        self.assertEqual(fig.layout.yaxis.scaleanchor, 'x')
        self.assertEqual(fig.layout.yaxis.scaleratio, 1)

    def test_axis_titles_give_units_in_round_brackets(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(fig.layout.xaxis.title.text, 'ΔRA × cos(Dec) (arcsec)')
        self.assertEqual(fig.layout.yaxis.title.text, 'ΔDec (arcsec)')

    def test_axis_ticks_match_the_light_curve(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        for axis in (fig.layout.xaxis, fig.layout.yaxis):
            self.assertEqual(axis.ticks, LIGHTCURVE_AXIS_TICKS['ticks'])
            self.assertEqual(axis.ticklen, LIGHTCURVE_AXIS_TICKS['ticklen'])
            self.assertEqual(axis.tickwidth, LIGHTCURVE_AXIS_TICKS['tickwidth'])
            self.assertEqual(axis.tickfont.size, LIGHTCURVE_AXIS_TICKS['tickfont_size'])
            self.assertEqual(axis.title.font.size, LIGHTCURVE_AXIS_TICKS['title_font_size'])

    def test_light_curve_tick_values_are_the_ones_the_light_curve_uses(self):
        # ASSERT
        self.assertEqual(LIGHTCURVE_AXIS_TICKS['ticks'], 'inside')
        self.assertEqual(LIGHTCURVE_AXIS_TICKS['tickfont_size'], 14)
        self.assertEqual(LIGHTCURVE_AXIS_TICKS['title_font_size'], 14)

    def test_figure_has_a_fallback_height(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(SCATTER_HEIGHT, EXPECTED_SCATTER_HEIGHT)
        self.assertEqual(fig.layout.height, EXPECTED_SCATTER_HEIGHT)

    def test_axes_shrink_the_plot_area_instead_of_widening_the_range(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(fig.layout.xaxis.constrain, 'domain')
        self.assertEqual(fig.layout.yaxis.constrain, 'domain')

    def test_marks_object_position_at_origin(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0 + ARCSEC)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        markers = [trace for trace in fig.data if not trace.showlegend]
        self.assertEqual([(tuple(m.x), tuple(m.y)) for m in markers], [((0,), (0,))])

    def test_hover_shows_id_mjd_band_and_offset(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0, band='g', diaSourceId=987654321012345678, mjd=60001.5)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        trace = [t for t in fig.data if t.showlegend][0]
        for label in ('diaSourceId', 'MJD', 'Band', 'ΔRA', 'ΔDec'):
            self.assertIn(label, trace.hovertemplate)
        self.assertEqual(trace.customdata[0][0], '987654321012345678')

    def test_out_of_range_points_are_counted_not_plotted(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0), make_source(10.0, 20.0 + 10 * ARCSEC, diaSourceId=2)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, outsideCount = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(outsideCount, 1)
        self.assertEqual(len(plotted_points(fig)), 1)

    def test_note_is_singular_for_one_outside_detection(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0 + 10 * ARCSEC)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual([a.text for a in fig.layout.annotations], ['1 detection outside plot range'])

    def test_note_is_plural_for_several_outside_detections(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0 + 10 * ARCSEC, diaSourceId=i) for i in range(3)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual([a.text for a in fig.layout.annotations], ['3 detections outside plot range'])

    def test_no_note_when_all_detections_in_range(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(len(fig.layout.annotations), 0)

    def test_note_counts_detections_without_a_position(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0), make_source(None, None, diaSourceId=2), make_source(None, 20.0, diaSourceId=3)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual([a.text for a in fig.layout.annotations], ['2 detections without a position'])
        self.assertEqual(len(plotted_points(fig)), 1)

    def test_note_lists_both_counts_when_both_apply(self):
        # ARRANGE
        sources = [make_source(None, None), make_source(10.0, 20.0 + 10 * ARCSEC, diaSourceId=2)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(
            [a.text for a in fig.layout.annotations],
            ['1 detection outside plot range<br>1 detection without a position'])

    def test_note_has_room_below_the_axis_title(self):
        # ARRANGE
        sources = [make_source(None, None), make_source(10.0, 20.0 + 10 * ARCSEC, diaSourceId=2)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        note = fig.layout.annotations[0]
        self.assertEqual(note.yref, 'paper')
        self.assertEqual(note.y, 0)
        self.assertLess(note.yshift, 0)
        # ROOM FOR TWO LINES OF THE 11 PX NOTE TEXT
        self.assertGreaterEqual(fig.layout.margin.b, -note.yshift + 2 * NOTE_LINE_HEIGHT_PX)
        self.assertEqual(fig.layout.margin.b, SCATTER_MARGIN_BOTTOM)

    def test_bottom_margin_only_fits_the_axis_title_when_there_is_no_note(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(len(fig.layout.annotations), 0)
        self.assertEqual(fig.layout.margin.b, SCATTER_MARGIN_BOTTOM_NO_NOTE)

    def test_note_is_centered_under_the_plot_area(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(None, None)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        note = fig.layout.annotations[0]
        self.assertEqual((note.xref, note.x, note.xanchor), ('paper', 0.5, 'center'))

    def test_legend_sits_above_the_plot_so_it_cannot_cover_points(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        legend = fig.layout.legend
        self.assertEqual((legend.orientation, legend.x, legend.xanchor), ('h', 0.5, 'center'))
        self.assertEqual(legend.yanchor, 'bottom')
        self.assertEqual(legend.y, SCATTER_LEGEND_Y)
        self.assertGreater(SCATTER_LEGEND_Y, 1.0)

    def test_plots_empty_axes_with_note_when_no_detection_has_a_position(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(None, None)])

        # ACT
        fig, outsideCount = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual(plotted_points(fig), [])
        self.assertEqual([a.text for a in fig.layout.annotations], ['1 detection without a position'])
        self.assertEqual(outsideCount, 0)

    def test_returns_no_figure_when_object_has_no_diasources(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [])

        # ACT
        fig, outsideCount = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertIsNone(fig)
        self.assertEqual(outsideCount, 0)


class TestRobustness(unittest.TestCase):

    def test_missing_keys_do_not_raise_and_plot_as_unknown_band(self):
        # ARRANGE
        sources = [{'ra': 10.0, 'decl': 20.0}]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, outsideCount = build_offset_scatter_figure(objectData)

        # ASSERT
        trace = [t for t in fig.data if t.showlegend][0]
        self.assertEqual(trace.name, 'unknown-band')
        self.assertEqual(trace.marker.color, UNKNOWN_BAND_COLOR)
        self.assertEqual(outsideCount, 0)

    def test_none_band_is_plotted_as_unknown_alongside_known_bands(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0, band=None, diaSourceId=1), make_source(10.0, 20.0, band='g', diaSourceId=2)]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, _ = build_offset_scatter_figure(objectData)

        # ASSERT
        names = [t.name for t in fig.data if t.showlegend]
        self.assertEqual(names, ['g-band', 'unknown-band'])

    def test_unknown_band_uses_a_circle(self):
        # ARRANGE
        offsets = [{'diaSourceId': 1, 'mjd': 60000.5, 'band': 'unknown', 'dRa': 0.0, 'dDec': 0.0}]

        # ACT
        traces = make_offset_band_traces(offsets)

        # ASSERT
        self.assertEqual(traces[0].marker.symbol, 'circle')

    def test_band_outside_the_rubin_bands_is_plotted_as_unknown(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0, band='<b>x</b>', diaSourceId=1), make_source(10.0, 20.0, band='q', diaSourceId=2)]

        # ACT
        offsets = compute_source_offsets(10.0, 20.0, sources)

        # ASSERT
        self.assertEqual([o['band'] for o in offsets], ['unknown', 'unknown'])

    def test_non_numeric_mjd_becomes_none(self):
        # ARRANGE
        sources = [make_source(10.0, 20.0, mjd='not-a-date')]

        # ACT
        offsets = compute_source_offsets(10.0, 20.0, sources)

        # ASSERT
        self.assertIsNone(offsets[0]['mjd'])

    def test_non_finite_or_non_numeric_positions_count_as_without_a_position(self):
        # ARRANGE
        sources = [
            make_source(float('nan'), 20.0, diaSourceId=1),
            make_source(10.0, float('inf'), diaSourceId=2),
            make_source('abc', 20.0, diaSourceId=3),
            make_source(10.0, 20.0, diaSourceId=4),
        ]
        objectData = make_object_data(10.0, 20.0, sources)

        # ACT
        fig, outsideCount = build_offset_scatter_figure(objectData)

        # ASSERT
        self.assertEqual([a.text for a in fig.layout.annotations], ['3 detections without a position'])
        self.assertEqual(outsideCount, 0)
        self.assertEqual(len(plotted_points(fig)), 1)

    def test_object_position_that_is_unusable_gives_no_figure(self):
        for badValue in (None, float('nan'), float('inf'), 'abc'):
            with self.subTest(badValue=badValue):
                # ARRANGE
                objectData = make_object_data(badValue, 20.0, [make_source(10.0, 20.0)])

                # ACT
                fig, outsideCount = build_offset_scatter_figure(objectData)

                # ASSERT
                self.assertIsNone(fig)
                self.assertEqual(outsideCount, 0)
                self.assertIsNone(object_offset_scatter(objectData))

    def test_object_with_missing_position_keys_gives_no_figure(self):
        # ARRANGE
        objectData = {'diaObjectId': '1', 'objectData': {}, 'diaSources': [make_source(10.0, 20.0)]}

        # ACT
        figureSpec = object_offset_scatter(objectData)

        # ASSERT
        self.assertIsNone(figureSpec)

    def test_guard_returns_none_and_logs_when_plotting_raises(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        with mock.patch('lasair.apps.object.utils.build_offset_scatter_figure', side_effect=RuntimeError('boom')):
            with self.assertLogs('lasair.apps.object.utils', level='ERROR'):
                figureSpec = object_offset_scatter_or_none(objectData)

        # ASSERT
        self.assertIsNone(figureSpec)

    def test_guard_returns_figure_when_plotting_works(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        figureSpec = object_offset_scatter_or_none(objectData)

        # ASSERT
        self.assertIn('data', figureSpec)


class TestObjectOffsetScatter(unittest.TestCase):

    def test_returns_json_serialisable_figure_with_data_and_layout(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        figureSpec = object_offset_scatter(objectData)

        # ASSERT
        self.assertEqual(set(figureSpec), {'data', 'layout'})
        roundTrip = json.loads(json.dumps(figureSpec))
        self.assertEqual(roundTrip['layout']['height'], EXPECTED_SCATTER_HEIGHT)

    def test_figure_carries_no_html_or_script(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [make_source(10.0, 20.0)])

        # ACT
        figureSpec = object_offset_scatter(objectData)

        # ASSERT
        self.assertNotIn('<script', json.dumps(figureSpec))

    def test_returns_none_for_object_without_diasources(self):
        # ARRANGE
        objectData = make_object_data(10.0, 20.0, [])

        # ACT
        figureSpec = object_offset_scatter(objectData)

        # ASSERT
        self.assertIsNone(figureSpec)


if __name__ == '__main__':
    import xmlrunner
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
