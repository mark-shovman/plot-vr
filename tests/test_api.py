"""Unit tests for the scripting API (pvr.figure / pvr.scatter / pvr.show)."""
import base64
import importlib
from unittest.mock import patch

import numpy as np
import pytest

import PlotVR
from PlotVR._artists import Scene, Frame, Axes


# ---------------------------------------------------------------------------
# scene()
# ---------------------------------------------------------------------------

class TestFigureFunction:
    def test_creates_scene_1_by_default(self):
        s = PlotVR.figure()
        assert isinstance(s, Scene)

    def test_auto_increments_scene_number(self):
        s1 = PlotVR.figure()
        s2 = PlotVR.figure()
        assert s1 is not s2

    def test_named_scene_by_int(self):
        s = PlotVR.figure(num=5)
        assert s.soup.title.string == 'Figure 5'

    def test_named_scene_by_string(self):
        s = PlotVR.figure(num='Scatter')
        assert s.soup.title.string == 'Scatter'

    def test_returns_same_scene_on_second_call(self):
        s1 = PlotVR.figure(num=1)
        s2 = PlotVR.figure(num=1)
        assert s1 is s2

    def test_switching_scenes(self):
        s1 = PlotVR.figure(num=1)
        s2 = PlotVR.figure(num=2)
        assert s1 is not s2


# ---------------------------------------------------------------------------
# plot()
# ---------------------------------------------------------------------------

class TestScatterFunction:
    def test_plot_auto_creates_scene(self):
        x = np.array([0.0, 1.0])
        PlotVR.scatter(x, x, x)
        # If no exception, scene was auto-created

    def test_plot_registers_data_in_axes(self):
        x = np.array([0.0, 1.0])
        PlotVR.scatter(x, x, x, color='#f00')
        axes = PlotVR.figure(num=1).gcf().gca()
        assert len(axes._raw_data) == 1
        assert axes._raw_data[0][3] == '#f00'  # color stored

    def test_plot_default_parameters(self):
        x = np.array([0.0, 1.0])
        PlotVR.scatter(x, x, x)
        axes = PlotVR.figure(num=1).gcf().gca()
        _, _, _, color, size, marker, _ = axes._raw_data[0]
        assert color == '#FFFFFF'
        assert size == 0.01
        assert marker == 'sphere'

    def test_plot_custom_size(self):
        x = np.array([0.0, 1.0])
        PlotVR.scatter(x, x, x, size=0.05)
        axes = PlotVR.figure(num=1).gcf().gca()
        assert axes._raw_data[0][4] == 0.05

    def test_plot_custom_marker(self):
        x = np.array([0.0, 1.0])
        PlotVR.scatter(x, x, x, marker='box')
        axes = PlotVR.figure(num=1).gcf().gca()
        assert axes._raw_data[0][5] == 'box'

    def test_multiple_plots_accumulate(self):
        x = np.array([0.0, 1.0])
        PlotVR.scatter(x, x, x, color='#f00')
        PlotVR.scatter(x, x, x, color='#0f0')
        axes = PlotVR.figure(num=1).gcf().gca()
        assert len(axes._raw_data) == 2

    def test_plot_uses_current_scene(self):
        x = np.array([0.0, 1.0])
        s1 = PlotVR.figure(num=1)
        s2 = PlotVR.figure(num=2)
        # current scene is now 2
        PlotVR.scatter(x, x, x)
        assert len(s2.gcf().gca()._raw_data) == 1
        assert len(s1.gcf().gca()._raw_data) == 0


# ---------------------------------------------------------------------------
# show()
# ---------------------------------------------------------------------------

def _decode_iframe_html(mock_iframe):
    """Extract and decode the HTML from a data URI passed to a mocked IFrame."""
    data_uri = mock_iframe.call_args[1]['src']
    encoded = data_uri.split(',', 1)[1]
    return base64.b64decode(encoded).decode('utf-8')


class TestShowFunction:
    def test_show_displays_iframe_with_data_uri(self):
        with patch('PlotVR._artists.display') as mock_display, \
             patch('PlotVR._artists.IFrame') as mock_iframe:
            x = np.array([0.0, 1.0])
            PlotVR.scatter(x, x, x)
            PlotVR.show()
        mock_display.assert_called_once()
        src = mock_iframe.call_args[1]['src']
        assert src.startswith('data:text/html;base64,')

    def test_show_html_contains_spheres(self):
        with patch('PlotVR._artists.display'), \
             patch('PlotVR._artists.IFrame') as mock_iframe:
            x = np.array([0.0, 0.5, 1.0])
            PlotVR.scatter(x, x, x)
            PlotVR.show()
        html = _decode_iframe_html(mock_iframe)
        assert 'a-sphere' in html

    def test_show_multiple_scenes(self):
        with patch('PlotVR._artists.display') as mock_display, \
             patch('PlotVR._artists.IFrame'):
            x = np.array([0.0, 1.0])
            PlotVR.figure(num=1)
            PlotVR.scatter(x, x, x)
            PlotVR.figure(num=2)
            PlotVR.scatter(x, x, x)
            PlotVR.show()
        assert mock_display.call_count == 2

    def test_show_normalized_coordinates_in_html(self):
        with patch('PlotVR._artists.display'), \
             patch('PlotVR._artists.IFrame') as mock_iframe:
            PlotVR.scatter(
                np.array([10.0, 20.0]),
                np.array([100.0, 200.0]),
                np.array([-5.0, 5.0]),
            )
            PlotVR.show()
        html = _decode_iframe_html(mock_iframe)
        # First point should normalize to 0 0 0
        assert 'position="0.0 0.0 0.0"' in html
        # Second point should normalize to 1 1 1
        assert 'position="1.0 1.0 1.0"' in html


# ---------------------------------------------------------------------------
# Accessor methods
# ---------------------------------------------------------------------------

class TestAccessors:
    def test_gcf_returns_frame(self):
        s = PlotVR.figure()
        assert isinstance(s.gcf(), Frame)

    def test_gca_returns_axes(self):
        s = PlotVR.figure()
        assert isinstance(s.gcf().gca(), Axes)
