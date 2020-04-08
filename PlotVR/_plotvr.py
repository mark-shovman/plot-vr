# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 22:47:45 2020

@author: mark.shovman

DIARY
-----
* trying to make it as similar to matplotlib as possible. Instead of figure we
have scene, instead of axes - frames. Frames will have axes inside them, and
data will be plotted relative to these axes.

* https://github.com/andreasplesch/aframe-meshline-component

TODO: consider inheriting from BS
TODO: add distinction between frame and axes
TODO: add axes graphics and interaction
TODO: add wobble to frames
TODO: add color, size, and marker to scatterplot

"""

__all__ = ['scene', 'plot', 'show']


import os
import tempfile
import webbrowser

from bs4 import BeautifulSoup

__all_scenes = {}
__current_scene = None
__current_frame = None

class Scene():
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

            <a-entity id="frame" position="0 1.5 -4" scale="0.1 0.1 0.1" shadow="receive: false"></a-entity>

        </a-scene>
      </body>
    </html>
    """

    def __init__(self, name=None):
        self.soup = BeautifulSoup(Scene.__html_template, features="html.parser")
        self.frames = self.soup.find_all(id='frame')
        self.current_frame = self.frames[0]

    def gcf(self):
        return self.current_frame

    def show(self):
        with tempfile.NamedTemporaryFile('w', delete=False, prefix='PlotVR_', suffix='.html') as f:
            f.write(str(self.soup))
            webbrowser.open('file://' + os.path.realpath(f.name), new=0)

# class Frame(BeautifulSoup):
#     def __init__(self):
#         pass

def scene(num=None):
    global __current_scene

    if num is None:
        num=1

    __current_scene = Scene(name=num)
    return __current_scene

def plot(x, y, z):
    global __current_scene

    if __current_scene is None:
        scene()

    frame = __current_scene.gcf()

    for i in range(len(x)):
        frame.append(__current_scene.soup.new_tag("a-sphere", position=f"{x[i]} {y[i]} {z[i]}", radius="0.1", color="#EF2D5E"))

def show():
    global __current_scene
    __current_scene.show()