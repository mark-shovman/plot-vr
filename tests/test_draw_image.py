"""Tests for Renderer.draw_image and ImagePlane artist (issue #17)."""
import base64
import io

import numpy as np
import pytest
from PIL import Image as PILImage

from PlotVR._artists import ImagePlane, Scene
from PlotVR._base import Renderer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solid_rgb(h, w, color=(255, 0, 0), dtype=np.uint8):
    """Return an (H, W, 3) array filled with *color*."""
    arr = np.zeros((h, w, 3), dtype=dtype)
    arr[:] = color
    return arr


def _decode_src(tag):
    """Decode the PNG data URI in *tag*['src'] and return a PIL Image."""
    header, b64data = tag['src'].split(',', 1)
    assert header == 'data:image/png;base64'
    return PILImage.open(io.BytesIO(base64.b64decode(b64data)))


def _fresh_soup():
    scene = Scene()
    return scene.soup


# ---------------------------------------------------------------------------
# Renderer.draw_image — input handling
# ---------------------------------------------------------------------------

class TestRendererDrawImageInputs:
    def test_accepts_uint8_ndarray(self):
        soup = _fresh_soup()
        arr = _solid_rgb(4, 8)
        tag = Renderer.draw_image(soup, arr)
        assert tag.name == 'a-image'

    def test_accepts_float_ndarray(self):
        soup = _fresh_soup()
        arr = _solid_rgb(4, 8, color=(1.0, 0.0, 0.0), dtype=float)
        tag = Renderer.draw_image(soup, arr)
        img = _decode_src(tag)
        px = np.array(img)[0, 0]
        assert px[0] == 255
        assert px[1] == 0

    def test_accepts_pil_image(self):
        soup = _fresh_soup()
        pil = PILImage.fromarray(_solid_rgb(4, 8))
        tag = Renderer.draw_image(soup, pil)
        assert tag.name == 'a-image'

    def test_accepts_rgba_ndarray(self):
        soup = _fresh_soup()
        arr = np.zeros((4, 8, 4), dtype=np.uint8)
        arr[:, :, :3] = (0, 255, 0)
        arr[:, :, 3] = 200
        tag = Renderer.draw_image(soup, arr)
        img = _decode_src(tag)
        assert img.mode == 'RGBA'

    def test_rejects_invalid_type(self):
        soup = _fresh_soup()
        with pytest.raises(TypeError):
            Renderer.draw_image(soup, "not_an_image")


# ---------------------------------------------------------------------------
# Renderer.draw_image — position and rotation attributes
# ---------------------------------------------------------------------------

class TestRendererDrawImageAttributes:
    def _tag(self, **kwargs):
        return Renderer.draw_image(_fresh_soup(), _solid_rgb(4, 8), **kwargs)

    def test_default_position(self):
        tag = self._tag()
        assert tag['position'] == '0.5 0.5 0.0'

    def test_custom_position(self):
        tag = self._tag(x=0.1, y=0.2, z=0.3)
        assert tag['position'] == '0.1 0.2 0.3'

    def test_default_rotation(self):
        tag = self._tag()
        assert tag['rotation'] == '0 0 0'

    def test_custom_rotation_string(self):
        tag = self._tag(rotation="45 0 0")
        assert tag['rotation'] == '45 0 0'

    def test_custom_rotation_tuple(self):
        tag = self._tag(rotation=(0, 90, 0))
        assert tag['rotation'] == '0 90 0'

    def test_custom_rotation_list(self):
        tag = self._tag(rotation=[0, 0, 180])
        assert tag['rotation'] == '0 0 180'


# ---------------------------------------------------------------------------
# Renderer.draw_image — aspect ratio and dimensions
# ---------------------------------------------------------------------------

class TestRendererDrawImageDimensions:
    def _tag(self, h, w, **kwargs):
        arr = _solid_rgb(h, w)
        return Renderer.draw_image(_fresh_soup(), arr, **kwargs)

    def test_default_width_is_one(self):
        tag = self._tag(4, 4)
        assert float(tag['width']) == pytest.approx(1.0)

    def test_default_height_preserves_square_aspect(self):
        tag = self._tag(4, 4)
        assert float(tag['height']) == pytest.approx(1.0)

    def test_default_height_preserves_landscape_aspect(self):
        # 8 wide × 4 tall → aspect 2.0; default width=1 → height=0.5
        tag = self._tag(4, 8)
        assert float(tag['height']) == pytest.approx(0.5)

    def test_default_height_preserves_portrait_aspect(self):
        # 4 wide × 8 tall → aspect 0.5; default width=1 → height=2
        tag = self._tag(8, 4)
        assert float(tag['height']) == pytest.approx(2.0)

    def test_explicit_width_derives_height(self):
        # 4×8 landscape, aspect=2; width=2 → height=1
        tag = self._tag(4, 8, width=2.0)
        assert float(tag['width']) == pytest.approx(2.0)
        assert float(tag['height']) == pytest.approx(1.0)

    def test_explicit_height_derives_width(self):
        # 4×8 landscape, aspect=2; height=1 → width=2
        tag = self._tag(4, 8, height=1.0)
        assert float(tag['height']) == pytest.approx(1.0)
        assert float(tag['width']) == pytest.approx(2.0)

    def test_explicit_width_and_height_no_override(self):
        tag = self._tag(4, 8, width=3.0, height=7.0)
        assert float(tag['width']) == pytest.approx(3.0)
        assert float(tag['height']) == pytest.approx(7.0)


# ---------------------------------------------------------------------------
# Renderer.draw_image — pixel fidelity
# ---------------------------------------------------------------------------

class TestRendererDrawImagePixelFidelity:
    def test_pixel_values_round_trip(self):
        arr = np.array([[[100, 150, 200]]], dtype=np.uint8)
        tag = Renderer.draw_image(_fresh_soup(), arr)
        img = _decode_src(tag)
        px = np.array(img.convert('RGB'))[0, 0]
        assert list(px) == [100, 150, 200]

    def test_float_image_clipped_and_scaled(self):
        # Values outside [0,1] must be clipped
        arr = np.array([[[2.0, -1.0, 0.5]]])
        tag = Renderer.draw_image(_fresh_soup(), arr)
        img = _decode_src(tag)
        px = np.array(img.convert('RGB'))[0, 0]
        assert px[0] == 255   # clipped to 1.0 → 255
        assert px[1] == 0     # clipped to 0.0 → 0
        assert px[2] == pytest.approx(127, abs=1)


# ---------------------------------------------------------------------------
# ImagePlane artist
# ---------------------------------------------------------------------------

class TestImagePlane:
    def _scene_and_plane(self, **kwargs):
        s = Scene()
        axes = s.gcf().gca()
        arr = _solid_rgb(4, 8)
        plane = ImagePlane(parent=axes, im=arr, **kwargs)
        return s, plane

    def test_a_image_tag_in_html(self):
        s, _ = self._scene_and_plane()
        assert s.soup.find('a-image') is not None

    def test_plane_is_child_of_frame_entity(self):
        s, _ = self._scene_and_plane()
        frame = s.soup.find(id='frame')
        assert frame.find('a-image') is not None

    def test_default_position(self):
        s, _ = self._scene_and_plane()
        tag = s.soup.find('a-image')
        assert tag['position'] == '0.5 0.5 0.0'

    def test_custom_position(self):
        s, _ = self._scene_and_plane(x=0.1, y=0.9, z=0.3)
        tag = s.soup.find('a-image')
        assert tag['position'] == '0.1 0.9 0.3'

    def test_custom_rotation(self):
        s, _ = self._scene_and_plane(rotation="90 0 0")
        tag = s.soup.find('a-image')
        assert tag['rotation'] == '90 0 0'

    def test_explicit_width_and_height(self):
        s, _ = self._scene_and_plane(width=2.0, height=1.0)
        tag = s.soup.find('a-image')
        assert float(tag['width']) == pytest.approx(2.0)
        assert float(tag['height']) == pytest.approx(1.0)

    def test_src_is_png_data_uri(self):
        s, _ = self._scene_and_plane()
        tag = s.soup.find('a-image')
        assert tag['src'].startswith('data:image/png;base64,')

    def test_multiple_planes(self):
        s = Scene()
        axes = s.gcf().gca()
        arr = _solid_rgb(4, 4)
        ImagePlane(parent=axes, im=arr, x=0.2, y=0.2)
        ImagePlane(parent=axes, im=arr, x=0.8, y=0.8)
        assert len(s.soup.find_all('a-image')) == 2


# ---------------------------------------------------------------------------
# Scripting-layer pvr.image()
# ---------------------------------------------------------------------------

class TestPvrImage:
    def test_image_creates_a_image_tag(self):
        import PlotVR as pvr
        arr = _solid_rgb(4, 8)
        scene = pvr.figure()          # returns Scene; also sets __current_scene
        pvr.image(arr)
        assert scene.soup.find('a-image') is not None

    def test_image_auto_creates_figure(self):
        import PlotVR as pvr
        arr = _solid_rgb(4, 4)
        # No prior figure() call — image() should auto-create one
        pvr.image(arr)
        # show() iterates __all_scenes; at least one scene must contain a-image
        import PlotVR._plotvr as m
        scenes = list(m.__dict__.get('_PlotVR__all_scenes',
                                     m.__dict__.get('__all_scenes', {})).values())
        assert any(s.soup.find('a-image') for s in scenes)

    def test_image_position_forwarded(self):
        import PlotVR as pvr
        arr = _solid_rgb(4, 4)
        scene = pvr.figure()
        pvr.image(arr, x=0.1, y=0.2, z=0.3)
        tag = scene.soup.find('a-image')
        assert tag['position'] == '0.1 0.2 0.3'

    def test_image_rotation_forwarded(self):
        import PlotVR as pvr
        arr = _solid_rgb(4, 4)
        scene = pvr.figure()
        pvr.image(arr, rotation="45 0 0")
        tag = scene.soup.find('a-image')
        assert tag['rotation'] == '45 0 0'
