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

DONE: added distinction between frame and axes (see _artists.py)
TODO: add axes graphics and interaction
TODO: add wobble to frames
DONE: added color (per-point), size (per-point), and marker type to scatterplot

"""

__all__ = ['figure', 'scatter', 'image', 'subplot', 'show', 'Event']

from ._artists import Scene
from ._base import Event

__all_scenes = {}
__current_scene = None

#%% scripting layer functions

def figure(num=None):
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

def scatter(x, y, z, color="#FFFFFF", size=0.01, marker='sphere', event=None):
    global __current_scene

    if __current_scene is None:
        figure()
    axes = __current_scene.gcf().gca()
    axes.register_data(x, y, z, color, size, marker, event)

def image(im, x=0.5, y=0.5, z=0.0, width=None, height=None, rotation="0 0 0"):
    """Place a 2-D image on a rectangle in the current scene.

    Parameters
    ----------
    im : numpy.ndarray or PIL.Image.Image
        Pixel data.  See :class:`~PlotVR._artists.ImagePlane` for details.
    x, y, z : float
        World-space centre position in normalised ``[0, 1]`` coordinates.
    width : float or None
    height : float or None
    rotation : str or tuple/list of three numbers
        A-Frame ``"rx ry rz"`` rotation in degrees.
    """
    global __current_scene
    from ._artists import ImagePlane

    if __current_scene is None:
        figure()
    axes = __current_scene.gcf().gca()
    plane = ImagePlane(parent=axes, im=im, x=x, y=y, z=z,
                       width=width, height=height, rotation=rotation)
    axes._kids.append(plane)


def subplot():
    """Add a new frame to the current scene and make it the active frame.

    Adds a second (or further) subplot to the current scene.  Frames are
    automatically repositioned in an arc around the user each time a new
    frame is added.  Returns the new :class:`~PlotVR._artists.Frame` so
    callers can inspect or further configure it.

    Typical usage::

        import numpy as np
        import PlotVR as pvr

        pvr.scatter(x1, y1, z1, color='#f00')   # goes into frame 0
        pvr.subplot()                            # add frame 1
        pvr.scatter(x2, y2, z2, color='#0f0')   # goes into frame 1
        pvr.show()
    """
    global __current_scene
    if __current_scene is None:
        figure()
    return __current_scene.add_frame()


def show():
    global __current_scene, __all_scenes
    for scene in __all_scenes:
        __all_scenes[scene].show()
