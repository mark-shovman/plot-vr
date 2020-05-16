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

TODO: add distinction between frame and axes
TODO: add axes graphics and interaction
TODO: add wobble to frames
TODO: add color, size, and marker to scatterplot

"""

__all__ = ['scene', 'plot', 'show']

from ._artists import Scene, MarkerSet

__all_scenes = {}
__current_scene = None

#%% scripting layer functions

def scene(num=None):
    global __current_scene, __all_scenes

    if num is None:
        num_scenes = [x for x in __all_scenes if isinstance(x, int)]
        if num_scenes:
            num = max(num_scenes) + 1
        else:
            num = 1

    if num in __all_scenes.keys():
        __current_scene = __all_scenes[num]
    else:
        __current_scene = Scene(name=num)
        __all_scenes[num] = __current_scene

    return __current_scene

def plot(x, y, z, color="#FFFFFF"):
    global __current_scene

    if __current_scene is None:
        scene()
    frame = __current_scene.gcf()
    frame.add_artist(MarkerSet(parent=frame, x=x, y=y, z=z, color=color))

def show():
    global __current_scene, __all_scenes
    for scene in __all_scenes:
        __all_scenes[scene].show()
