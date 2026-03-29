# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 22:47:45 2020

@author: mark.shovman

"""

import os
import tempfile
import webbrowser

from IPython.display import display, HTML, IFrame

from bs4 import BeautifulSoup

from ._base import Artist, Renderer

__all__ = ['Scene', 'Frame', 'Axes', 'ImagePlane']

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

        frame = Frame(parent=self)
        self._kids.append(frame)
        self._current_frame = frame

    def gcf(self):
        return self._current_frame

    def show(self):
        super(Scene, self).show()

        fname = f'./PlotVR_{self.soup.title.string}.html'
        # with tempfile.NamedTemporaryFile('w', delete=False, prefix='PlotVR_', suffix='.html') as f:
        with open(fname, 'w') as f:
            f.write(str(self.soup))
            display(IFrame(src=fname, width=700, height=600))
            # webbrowser.open('file://' + os.path.realpath(f.name), new=0)

    def _repr_html_(self):
        """

        TODO: return an html representation, for use in Jupyter
        https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display

        Returns
        -------
        None.

        """

        return str(self.soup)

class Frame(Artist):
    def __init__(self, parent):
        super(Frame, self).__init__(parent)
        a_parent = self._parent.get_a_entity()
        self._a_entity = self.soup.new_tag("a-entity", id='frame',
                                                             position="0 1 -1.5",
                                                             scale="1 1 1",
                                                             shadow='cast:false; receive:false')
        a_parent.append(self._a_entity)

        axes = Axes(parent=self)
        self._kids.append(axes)
        self._current_axes = axes

    def gca(self):
        return self._current_axes


class Axes(Artist):
    def __init__(self, parent):
        super(Axes, self).__init__(parent)
        self._a_entity = self._parent.get_a_entity()  # reuse Frame's entity; no new wrapper

        self._a_entity.append(self.soup.new_tag("a-entity", id='framebounds',
                                                geometry="primitive: box",
                                                position="0.5 0.5 0.5",
                                                material="color: blue; side:back; transparent:true; opacity:0.2; flatShading: true",
                                                shadow='cast:false; receive:false',
                                                mixin='frame_mix'))

        self._a_entity.append(self.soup.new_tag("a-entity", id='axes',
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