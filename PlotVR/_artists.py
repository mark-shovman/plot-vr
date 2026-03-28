# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 22:47:45 2020

@author: mark.shovman

"""

import os
import tempfile
import webbrowser

from IPython.core.display import display, HTML
from IPython.display import IFrame

from bs4 import BeautifulSoup

from ._base import Artist

__all__ = ['Scene', 'Frame', 'Axes']

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

        self._raw_data = []  # list of (x, y, z, color) tuples

    def register_data(self, x, y, z, color):
        self._raw_data.append((x, y, z, color))

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

            for x, y, z, color in self._raw_data:
                ms = MarkerSet(parent=self,
                               x=_norm(x, x_min, x_max),
                               y=_norm(y, y_min, y_max),
                               z=_norm(z, z_min, z_max),
                               color=color)
                self._kids.append(ms)

            self._raw_data = []  # prevent double-render if show() called again

        super(Axes, self).show()


class MarkerSet(Artist):
    def __init__(self, parent, x, y, z, color="#EF2D5E"):

        super(MarkerSet, self).__init__(parent)
        a_parent = self._parent.get_a_entity()
        self._a_entity = self.soup.new_tag("a-entity", id='markerset',
                                           shadow='cast:false; receive:false')
        a_parent.append(self._a_entity)

        for i in zip(x, y, z):
            self._a_entity.append(self.soup.new_tag("a-sphere",
                                                    position=f'{i[0]} {i[1]} {i[2]}',
                                                    radius="0.01",
                                                    color=color,
                                                    shadow='cast:true; receive:false'
                                                    ))