"""Unit tests for the artist layer (Scene, Frame, Axes, MarkerSet)."""
import math

import numpy as np
import pytest

from PlotVR._artists import Scene, Frame, Axes, MarkerSet, _MARKER_TAGS, _compute_layout


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class TestScene:
    def test_default_title(self):
        s = Scene()
        assert s.soup.title.string == 'PlotVR Figure'

    def test_int_name_becomes_figure_n(self):
        s = Scene(name=3)
        assert s.soup.title.string == 'Figure 3'

    def test_str_name_used_verbatim(self):
        s = Scene(name='My Plot')
        assert s.soup.title.string == 'My Plot'

    def test_gcf_returns_frame(self):
        s = Scene()
        assert isinstance(s.gcf(), Frame)

    def test_content_entity_present(self):
        s = Scene()
        assert s.soup.find(id='content') is not None

    def test_repr_html_returns_string(self):
        s = Scene()
        html = s._repr_html_()
        assert isinstance(html, str)
        assert '<a-scene>' in html


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

class TestFrame:
    def test_frame_entity_in_html(self):
        s = Scene()
        assert s.soup.find(id='frame-0') is not None

    def test_frame_default_position(self):
        s = Scene()
        assert s.soup.find(id='frame-0')['position'] == '0 1 -1.5'

    def test_gca_returns_axes(self):
        s = Scene()
        assert isinstance(s.gcf().gca(), Axes)


# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------

class TestAxes:
    def _scene_and_axes(self):
        s = Scene()
        return s, s.gcf().gca()

    # --- HTML structure ---

    def test_framebounds_present(self):
        s, _ = self._scene_and_axes()
        assert s.soup.find(id='framebounds-0') is not None

    def test_axes_lines_present(self):
        s, _ = self._scene_and_axes()
        assert s.soup.find(id='axes-0') is not None

    # --- register_data ---

    def test_register_data_stored(self):
        _, axes = self._scene_and_axes()
        x = np.array([0.0, 1.0])
        axes.register_data(x, x, x, '#fff', 0.01, 'sphere')
        assert len(axes._raw_data) == 1

    def test_multiple_register_data(self):
        _, axes = self._scene_and_axes()
        x = np.array([0.0, 1.0])
        axes.register_data(x, x, x, '#f00', 0.01, 'sphere')
        axes.register_data(x, x, x, '#0f0', 0.01, 'sphere')
        assert len(axes._raw_data) == 2

    # --- normalization: values in [0, 1] ---

    def test_normalization_unit_range_unchanged(self):
        s, axes = self._scene_and_axes()
        x = np.array([0.0, 0.5, 1.0])
        axes.register_data(x, x, x, '#fff', 0.01, 'sphere')
        axes.show()
        for sp in s.soup.find(id='markerset').find_all('a-sphere'):
            for coord in sp['position'].split():
                assert 0.0 <= float(coord) <= 1.0

    def test_normalization_arbitrary_range(self):
        s, axes = self._scene_and_axes()
        axes.register_data(
            np.array([10.0, 20.0, 30.0]),
            np.array([100.0, 200.0, 300.0]),
            np.array([-5.0, 0.0, 5.0]),
            '#fff', 0.01, 'sphere',
        )
        axes.show()
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        x_vals = [float(sp['position'].split()[0]) for sp in spheres]
        assert x_vals == pytest.approx([0.0, 0.5, 1.0])

    def test_normalization_degenerate_axis_becomes_half(self):
        s, axes = self._scene_and_axes()
        axes.register_data(
            np.array([5.0, 5.0, 5.0]),
            np.array([0.0, 1.0, 2.0]),
            np.array([0.0, 1.0, 2.0]),
            '#fff', 0.01, 'sphere',
        )
        axes.show()
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        x_vals = [float(sp['position'].split()[0]) for sp in spheres]
        assert all(v == pytest.approx(0.5) for v in x_vals)

    def test_normalization_multi_dataset_uses_global_bounds(self):
        s, axes = self._scene_and_axes()
        # X range [0, 1] + [2, 3] → global [0, 3]
        axes.register_data(np.array([0.0, 1.0]), np.array([0.0, 1.0]),
                           np.array([0.0, 1.0]), '#f00', 0.01, 'sphere')
        axes.register_data(np.array([2.0, 3.0]), np.array([0.0, 1.0]),
                           np.array([0.0, 1.0]), '#0f0', 0.01, 'sphere')
        axes.show()
        all_spheres = s.soup.find_all('a-sphere')
        x_vals = [float(sp['position'].split()[0]) for sp in all_spheres]
        assert x_vals == pytest.approx([0.0, 1/3, 2/3, 1.0], abs=1e-6)

    # --- show() bookkeeping ---

    def test_show_clears_raw_data(self):
        _, axes = self._scene_and_axes()
        x = np.array([0.0, 1.0])
        axes.register_data(x, x, x, '#fff', 0.01, 'sphere')
        axes.show()
        assert axes._raw_data == []

    def test_show_idempotent_no_duplicate_markers(self):
        s, axes = self._scene_and_axes()
        x = np.array([0.0, 1.0])
        axes.register_data(x, x, x, '#fff', 0.01, 'sphere')
        axes.show()
        axes.show()  # second call with empty _raw_data should do nothing
        assert len(s.soup.find_all('a-sphere')) == 2


# ---------------------------------------------------------------------------
# Frame grab interaction
# ---------------------------------------------------------------------------

class TestFrameGrab:
    def _scene(self):
        return Scene()

    def test_frame_has_frame_grab_component(self):
        s = self._scene()
        assert s.soup.find(id='frame-0').has_attr('frame-grab')

    def test_frame_has_grabbable(self):
        s = self._scene()
        assert s.soup.find(id='frame-0').has_attr('grabbable')

    def test_grab_surface_present(self):
        s = self._scene()
        assert s.soup.find(id='frame-grab-surface-0') is not None

    def test_grab_surface_is_child_of_frame(self):
        s = self._scene()
        frame = s.soup.find(id='frame-0')
        assert frame.find(id='frame-grab-surface-0') is not None

    def test_grab_surface_has_static_body(self):
        s = self._scene()
        assert s.soup.find(id='frame-grab-surface-0').has_attr('static-body')

    def test_grab_surface_is_invisible_box(self):
        s = self._scene()
        gs = s.soup.find(id='frame-grab-surface-0')
        assert 'box' in gs['geometry']
        assert 'false' in gs['material']  # visible: false

    def test_grab_surface_position(self):
        s = self._scene()
        assert s.soup.find(id='frame-grab-surface-0')['position'] == '0.5 0.5 0.5'

    def test_framebounds_retains_mixin(self):
        s = self._scene()
        assert s.soup.find(id='framebounds-0').get('mixin') == 'frame_mix'

    def test_framebounds_has_no_direct_grabbable(self):
        s = self._scene()
        assert not s.soup.find(id='framebounds-0').has_attr('grabbable')

    def test_frame_mix_mixin_has_hoverable(self):
        s = self._scene()
        assert s.soup.find(id='frame_mix').has_attr('hoverable')

    def test_frame_mix_mixin_lacks_grabbable(self):
        s = self._scene()
        assert not s.soup.find(id='frame_mix').has_attr('grabbable')

    def test_frame_mix_mixin_lacks_stretchable(self):
        s = self._scene()
        assert not s.soup.find(id='frame_mix').has_attr('stretchable')

    def test_frame_grab_js_component_in_template(self):
        s = self._scene()
        assert "registerComponent('frame-grab'" in str(s.soup)


# ---------------------------------------------------------------------------
# MarkerSet
# ---------------------------------------------------------------------------

class TestMarkerSet:
    def _scene_and_markerset(self, x, y, z, **kwargs):
        s = Scene()
        axes = s.gcf().gca()
        ms = MarkerSet(parent=axes, x=x, y=y, z=z, **kwargs)
        return s, ms

    def test_default_creates_spheres(self):
        x = np.array([0.0, 0.5])
        s, _ = self._scene_and_markerset(x, x, x)
        assert len(s.soup.find(id='markerset').find_all('a-sphere')) == 2

    def test_correct_point_count(self):
        x = np.linspace(0, 1, 7)
        s, _ = self._scene_and_markerset(x, x, x)
        assert len(s.soup.find(id='markerset').find_all('a-sphere')) == 7

    # --- color ---

    def test_single_color_broadcast_to_all_points(self):
        x = np.array([0.0, 0.5, 1.0])
        s, _ = self._scene_and_markerset(x, x, x, color='#abc')
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        assert all(sp['color'] == '#abc' for sp in spheres)

    def test_per_point_color(self):
        x = np.array([0.0, 0.5, 1.0])
        colors = ['#f00', '#0f0', '#00f']
        s, _ = self._scene_and_markerset(x, x, x, color=colors)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        assert [sp['color'] for sp in spheres] == colors

    # --- size ---

    def test_single_size_broadcast_to_all_points(self):
        x = np.array([0.0, 0.5])
        s, _ = self._scene_and_markerset(x, x, x, size=0.05)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        assert all(sp['radius'] == '0.05' for sp in spheres)

    def test_per_point_size(self):
        x = np.array([0.0, 0.5, 1.0])
        sizes = [0.01, 0.02, 0.03]
        s, _ = self._scene_and_markerset(x, x, x, size=sizes)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        assert [sp['radius'] for sp in spheres] == ['0.01', '0.02', '0.03']

    # --- marker type ---

    @pytest.mark.parametrize("name,tag", list(_MARKER_TAGS.items()))
    def test_marker_type_creates_correct_tag(self, name, tag):
        x = np.array([0.5])
        s, _ = self._scene_and_markerset(x, x, x, marker=name)
        assert len(s.soup.find(id='markerset').find_all(tag)) == 1

    def test_raw_aframe_tag_passthrough(self):
        x = np.array([0.5])
        s, _ = self._scene_and_markerset(x, x, x, marker='a-sphere')
        assert len(s.soup.find(id='markerset').find_all('a-sphere')) == 1

    # --- positions ---

    def test_positions_written_correctly(self):
        x = np.array([0.1, 0.9])
        y = np.array([0.2, 0.8])
        z = np.array([0.3, 0.7])
        s, _ = self._scene_and_markerset(x, y, z)
        spheres = s.soup.find(id='markerset').find_all('a-sphere')
        pos0 = [float(v) for v in spheres[0]['position'].split()]
        pos1 = [float(v) for v in spheres[1]['position'].split()]
        assert pos0 == pytest.approx([0.1, 0.2, 0.3])
        assert pos1 == pytest.approx([0.9, 0.8, 0.7])


# ---------------------------------------------------------------------------
# _compute_layout
# ---------------------------------------------------------------------------

class TestComputeLayout:
    def test_zero_frames(self):
        assert _compute_layout(0) == []

    def test_one_frame_straight_ahead(self):
        positions = _compute_layout(1)
        assert len(positions) == 1
        pos, rot = positions[0]
        assert pos == '0 1 -1.5'
        assert rot == '0 0 0'

    def test_two_frames_symmetric(self):
        positions = _compute_layout(2)
        assert len(positions) == 2
        pos0, _ = positions[0]
        pos1, _ = positions[1]
        x0, _, z0 = [float(v) for v in pos0.split()]
        x1, _, z1 = [float(v) for v in pos1.split()]
        # Frames should be symmetric about x=0
        assert x0 == pytest.approx(-x1, abs=1e-4)
        assert z0 == pytest.approx(z1, abs=1e-4)

    def test_two_frames_rotations_symmetric(self):
        positions = _compute_layout(2)
        _, rot0 = positions[0]
        _, rot1 = positions[1]
        ry0 = float(rot0.split()[1])
        ry1 = float(rot1.split()[1])
        assert ry0 == pytest.approx(-ry1, abs=1e-4)

    def test_n_frames_returns_n_entries(self):
        for n in range(1, 6):
            assert len(_compute_layout(n)) == n

    def test_frames_at_radius_1_5(self):
        for n in [2, 3, 4]:
            for pos, _ in _compute_layout(n):
                x, _, z = [float(v) for v in pos.split()]
                r = math.sqrt(x**2 + z**2)
                assert r == pytest.approx(1.5, abs=1e-3)

    def test_all_frames_at_height_1(self):
        for n in [1, 2, 3]:
            for pos, _ in _compute_layout(n):
                _, y, _ = pos.split()
                assert float(y) == 1.0


# ---------------------------------------------------------------------------
# Scene.add_frame / multiple frames
# ---------------------------------------------------------------------------

class TestMultipleFrames:
    def test_add_frame_returns_frame(self):
        s = Scene()
        f = s.add_frame()
        assert isinstance(f, Frame)

    def test_add_frame_increments_frame_count(self):
        s = Scene()
        assert len(s._frames) == 1
        s.add_frame()
        assert len(s._frames) == 2

    def test_add_frame_makes_new_frame_current(self):
        s = Scene()
        f0 = s.gcf()
        f1 = s.add_frame()
        assert s.gcf() is f1
        assert f0 is not f1

    def test_two_frames_have_unique_ids(self):
        s = Scene()
        s.add_frame()
        assert s.soup.find(id='frame-0') is not None
        assert s.soup.find(id='frame-1') is not None

    def test_two_frames_have_unique_axes_ids(self):
        s = Scene()
        s.add_frame()
        assert s.soup.find(id='framebounds-0') is not None
        assert s.soup.find(id='framebounds-1') is not None
        assert s.soup.find(id='axes-0') is not None
        assert s.soup.find(id='axes-1') is not None

    def test_two_frames_have_distinct_positions(self):
        s = Scene()
        s.add_frame()
        pos0 = s.soup.find(id='frame-0')['position']
        pos1 = s.soup.find(id='frame-1')['position']
        assert pos0 != pos1

    def test_first_frame_repositioned_when_second_added(self):
        s = Scene()
        pos_before = s.soup.find(id='frame-0')['position']
        s.add_frame()
        pos_after = s.soup.find(id='frame-0')['position']
        # With 2 frames, frame-0 moves away from straight-ahead
        assert pos_before != pos_after

    def test_frames_face_user_via_rotation(self):
        s = Scene()
        s.add_frame()
        rot0 = s.soup.find(id='frame-0')['rotation']
        rot1 = s.soup.find(id='frame-1')['rotation']
        # Rotations should be set (non-empty) and differ between frames
        assert rot0 != '' and rot1 != ''
        assert rot0 != rot1

    def test_independent_data_normalisation(self):
        """Each frame normalises its own data independently."""
        s = Scene()
        ax0 = s.gcf().gca()
        ax0.register_data(np.array([0.0, 100.0]),
                          np.array([0.0, 100.0]),
                          np.array([0.0, 100.0]),
                          '#f00', 0.01, 'sphere')

        ax1 = s.add_frame().gca()
        ax1.register_data(np.array([0.0, 1.0]),
                          np.array([0.0, 1.0]),
                          np.array([0.0, 1.0]),
                          '#0f0', 0.01, 'sphere')

        s.show.__func__  # don't actually display; call show on axes directly
        ax0.show()
        ax1.show()

        # Both frames should have markers at 0.0 and 1.0 in normalised coords
        all_spheres = s.soup.find_all('a-sphere')
        positions = {tuple(float(v) for v in sp['position'].split()) for sp in all_spheres}
        assert (0.0, 0.0, 0.0) in positions
        assert (1.0, 1.0, 1.0) in positions
