"""Unit tests for the scripting API (pvr.figure / pvr.scatter / pvr.show)."""
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

class TestShowFunction:
    def test_show_writes_html_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch('PlotVR._artists.display'):
            x = np.array([0.0, 1.0])
            PlotVR.scatter(x, x, x)
            PlotVR.show()
        assert (tmp_path / 'PlotVR_Figure 1.html').exists()

    def test_show_html_contains_spheres(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch('PlotVR._artists.display'):
            x = np.array([0.0, 0.5, 1.0])
            PlotVR.scatter(x, x, x)
            PlotVR.show()
        html = (tmp_path / 'PlotVR_Figure 1.html').read_text()
        assert 'a-sphere' in html

    def test_show_multiple_scenes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch('PlotVR._artists.display'):
            x = np.array([0.0, 1.0])
            PlotVR.figure(num=1)
            PlotVR.scatter(x, x, x)
            PlotVR.figure(num=2)
            PlotVR.scatter(x, x, x)
            PlotVR.show()
        assert (tmp_path / 'PlotVR_Figure 1.html').exists()
        assert (tmp_path / 'PlotVR_Figure 2.html').exists()

    def test_show_normalized_coordinates_in_html(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch('PlotVR._artists.display'):
            PlotVR.scatter(
                np.array([10.0, 20.0]),
                np.array([100.0, 200.0]),
                np.array([-5.0, 5.0]),
            )
            PlotVR.show()
        html = (tmp_path / 'PlotVR_Figure 1.html').read_text()
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
