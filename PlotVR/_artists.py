# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 22:47:45 2020

@author: mark.shovman

"""

import os
import tempfile
import webbrowser

from bs4 import BeautifulSoup

from ._base import Artist

__all__ = ['Scene', 'Frame']

class Scene(Artist):
    __html_template = """
    <html>
      <head>
        <script src="https://aframe.io/releases/1.0.4/aframe.min.js"></script>
      </head>
      <title>PlotVR Figure</title>
      <body>
        <a-scene>
            <a-light type="ambient" color="#222"></a-light>
            <a-light type="directional" castShadow="true;" position="0 4 1"></a-light>
            <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#222" shadow="receive: true"></a-plane>
            <a-sky color="#000000"></a-sky>

            <a-entity id="content"></a-entity>

            <a-entity id="frame" position="0 1.5 -4" scale="0.1 0.1 0.1" shadow="receive: false"></a-entity>

        </a-scene>
      </body>
    </html>
    """

    def __init__(self, name=None):
        super(Scene, self).__init__()
        self.soup = BeautifulSoup(Scene.__html_template, features="html.parser")
        if name is not None:
            if type(name) is str:
                self.soup.title.string = name
            elif type(name) is int:
                self.soup.title.string = f'Figure {name}'
            else:
                self.soup.title.string = str(name)

        self._a_entity = self.soup.find_all(id='content')[0]

        #TODO: add frame as child

        #TODO: obsolete
        self.frames = self.soup.find_all(id='frame')
        self._current_frame = self.frames[0]

    def gcf(self):
        return self._current_frame

    def show(self):
        Artist.show(self)

        with tempfile.NamedTemporaryFile('w', delete=False, prefix='PlotVR_', suffix='.html') as f:
            f.write(str(self.soup))
            webbrowser.open('file://' + os.path.realpath(f.name), new=0)

class Frame(Artist):
    pass

class MarkerSet(Artist):
    pass