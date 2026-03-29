# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 22:47:45 2020

@author: mark.shovman

"""

import base64
import math
import os

from IPython.display import display, IFrame

from bs4 import BeautifulSoup

from ._base import Artist, Renderer

__all__ = ['Scene', 'Frame', 'Axes', 'ImagePlane']


def _compute_layout(n):
    """Return list of (position_str, rotation_str) for n frames arranged in an arc."""
    if n == 0:
        return []
    if n == 1:
        return [('0 1 -1.5', '0 0 0')]
    radius = 1.5
    spread_deg = min(180.0, (n - 1) * 45.0)
    result = []
    for i in range(n):
        angle_deg = -spread_deg / 2 + i * spread_deg / (n - 1)
        angle_rad = math.radians(angle_deg)
        x = round(radius * math.sin(angle_rad), 4)
        z = round(-radius * math.cos(angle_rad), 4)
        rot_y = round(-angle_deg, 1)
        result.append((f'{x} 1 {z}', f'0 {rot_y} 0'))
    return result


class Scene(Artist):
    __html_template_fname = "_scene_template.html"

    def __init__(self, name=None):
        super(Scene, self).__init__()

        try:
            self_path = os.path.dirname(__file__)
        except NameError:
            self_path = ''

        with open(os.path.join(self_path, Scene.__html_template_fname)) as fp:
            self.soup = BeautifulSoup(fp, features="html.parser")

        if name is not None:
            if type(name) is str:
                self.soup.title.string = name
            elif type(name) is int:
                self.soup.title.string = f'Figure {name}'
            else:
                self.soup.title.string = str(name)

        self._a_entity = self.soup.find_all(id='content')[0]
        self._frames = []
        self._add_frame()

    def _add_frame(self):
        """Create a new Frame, append it, and update the spatial layout."""
        idx = len(self._frames)
        frame = Frame(parent=self, index=idx)
        self._kids.append(frame)
        self._frames.append(frame)
        self._current_frame = frame
        self._relayout()
        return frame

    def _relayout(self):
        """Reposition all frames based on current frame count."""
        positions = _compute_layout(len(self._frames))
        for frame, (pos, rot) in zip(self._frames, positions):
            frame.set_position(pos, rot)

    def add_frame(self):
        """Add a new Frame to the scene, update layout, and return it."""
        return self._add_frame()

    def gcf(self):
        return self._current_frame

    def show(self):
        super(Scene, self).show()

        html_bytes = str(self.soup).encode('utf-8')
        data_uri = 'data:text/html;base64,' + base64.b64encode(html_bytes).decode('ascii')
        display(IFrame(src=data_uri, width=700, height=600))

    def _repr_html_(self):
        return str(self.soup)

class Frame(Artist):
    def __init__(self, parent, index=0):
        super(Frame, self).__init__(parent)
        a_parent = self._parent.get_a_entity()
        self._index = index
        self._a_entity = self.soup.new_tag("a-entity", id=f'frame-{index}',
                                                             position="0 1 -1.5",
                                                             scale="1 1 1",
                                                             shadow='cast:false; receive:false')
        self._a_entity['frame-grab'] = ''
        self._a_entity['grabbable'] = ''

        # Invisible 1×1×1 box centred at 0.5 0.5 0.5 (matching framebounds / normalised data
        # volume) so cannon.js physics-collider on the controllers can detect the frame entity.
        grab_surface = self.soup.new_tag("a-entity",
                                         id=f'frame-grab-surface-{index}',
                                         geometry="primitive: box; width: 1; height: 1; depth: 1",
                                         material="visible: false",
                                         position="0.5 0.5 0.5",
                                         shadow='cast:false; receive:false')
        grab_surface['static-body'] = ''
        self._a_entity.append(grab_surface)

        a_parent.append(self._a_entity)

        axes = Axes(parent=self, index=index)
        self._kids.append(axes)
        self._current_axes = axes

    def set_position(self, position, rotation="0 0 0"):
        """Update the A-Frame position and rotation of this frame entity."""
        self._a_entity['position'] = position
        self._a_entity['rotation'] = rotation

    def gca(self):
        return self._current_axes


class Axes(Artist):
    def __init__(self, parent, index=0):
        super(Axes, self).__init__(parent)
        self._a_entity = self._parent.get_a_entity()  # reuse Frame's entity; no new wrapper

        self._a_entity.append(self.soup.new_tag("a-entity", id=f'framebounds-{index}',
                                                geometry="primitive: box",
                                                position="0.5 0.5 0.5",
                                                material="color: blue; side:back; transparent:true; opacity:0.2; flatShading: true",
                                                shadow='cast:false; receive:false',
                                                mixin='frame_mix'))

        self._a_entity.append(self.soup.new_tag("a-entity", id=f'axes-{index}',
                                                line__0="start: 0, 0, 0; end: 1 0 0; color: red",
                                                line__1="start: 0, 0, 0; end: 0 1 0; color: green",
                                                line__2="start: 0, 0, 0; end: 0 0 1; color: blue",
                                                shadow='cast:false; receive:false'))

        self._raw_data = []  # list of (x, y, z, color, size, marker, event) tuples

    def register_data(self, x, y, z, color, size, marker, event=None):
        self._raw_data.append((x, y, z, color, size, marker, event))

    def show(self):
        if self._raw_data:
            import numpy as np

            def _bounds(idx):
                arrays = [d[idx] for d in self._raw_data]
                return min(a.min() for a in arrays), max(a.max() for a in arrays)

            def _norm(arr, lo, hi):
                if hi == lo:
                    return np.full_like(arr, 0.5, dtype=float)
                return (arr - lo) / (hi - lo)

            x_min, x_max = _bounds(0)
            y_min, y_max = _bounds(1)
            z_min, z_max = _bounds(2)

            for x, y, z, color, size, marker, event in self._raw_data:
                ms = MarkerSet(parent=self,
                               x=_norm(x, x_min, x_max),
                               y=_norm(y, y_min, y_max),
                               z=_norm(z, z_min, z_max),
                               color=color,
                               size=size,
                               marker=marker,
                               event=event)
                self._kids.append(ms)

            self._raw_data = []  # prevent double-render if show() called again

        super(Axes, self).show()


_MARKER_TAGS = {
    'sphere':       'a-sphere',
    'box':          'a-box',
    'cone':         'a-cone',
    'cylinder':     'a-cylinder',
    'dodecahedron': 'a-dodecahedron',
    'octahedron':   'a-octahedron',
    'tetrahedron':  'a-tetrahedron',
    'torus':        'a-torus',
}

class MarkerSet(Artist):
    def __init__(self, parent, x, y, z, color="#EF2D5E", size=0.01, marker='sphere',
                 event=None):
        import numpy as np

        super(MarkerSet, self).__init__(parent)
        a_parent = self._parent.get_a_entity()
        self._a_entity = self.soup.new_tag("a-entity", id='markerset',
                                           shadow='cast:false; receive:false')
        a_parent.append(self._a_entity)

        n = len(x)
        tag = _MARKER_TAGS.get(marker, marker)  # accept friendly name or raw a-frame tag
        colors = [color] * n if isinstance(color, str) else list(color)
        sizes  = [size]  * n if np.isscalar(size)  else list(size)

        # Resolve annotation texts once so we can index per-point below.
        if event is not None and event._annotation is not None:
            ann_texts, _, _ = event._annotation
            if isinstance(ann_texts, str):
                ann_texts = [ann_texts] * n
            else:
                ann_texts = list(ann_texts)
        else:
            ann_texts = None

        event_attrs = event.to_aframe_attrs() if event is not None else {}

        for i, (px, py, pz, pc, ps) in enumerate(zip(x, y, z, colors, sizes)):
            marker_tag = self.soup.new_tag(tag,
                                           position=f'{px} {py} {pz}',
                                           radius=str(ps),
                                           color=pc,
                                           shadow='cast:true; receive:false',
                                           **event_attrs)
            if ann_texts is not None:
                label = event.make_annotation_tag(self.soup, ann_texts[i])
                if label is not None:
                    marker_tag.append(label)
            self._a_entity.append(marker_tag)


class ImagePlane(Artist):
    """Artist that places a 2-D image on a rectangle in 3-D world space.

    Delegates HTML generation to :meth:`Renderer.draw_image`.

    Parameters
    ----------
    parent : Artist
        Parent artist (typically an :class:`Axes`).
    im : numpy.ndarray or PIL.Image.Image
        Pixel data.  Arrays must have shape ``(H, W, 3)`` or ``(H, W, 4)``
        with dtype ``uint8`` or float in ``[0, 1]``.
    x, y, z : float
        World-space centre position in the frame's normalised ``[0, 1]``
        coordinate space.
    width : float or None
        Width of the image plane in A-Frame world units.
    height : float or None
        Height of the image plane in A-Frame world units.
    rotation : str or tuple/list of three numbers
        A-Frame ``"rx ry rz"`` rotation in degrees (default ``"0 0 0"``).
    """

    def __init__(self, parent, im, x=0.5, y=0.5, z=0.0,
                 width=None, height=None, rotation="0 0 0"):
        super().__init__(parent)
        a_parent = self._parent.get_a_entity()
        self._a_entity = Renderer.draw_image(
            self.soup, im,
            x=x, y=y, z=z,
            width=width, height=height,
            rotation=rotation,
        )
        a_parent.append(self._a_entity)