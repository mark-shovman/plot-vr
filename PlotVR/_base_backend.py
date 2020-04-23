# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 20:47:13 2020

@author: mark.shovman
"""
class Space():
    pass

class Renderer():
    """
  	* draw_path - same, but in 3D
  	* draw_image - same, but in 3D, so needs a 3D rect to draw on
  	* draw_text - same, but in 3D - anchor point, blackboarding behaviour, etc
  	* get_text_width_height_descent - same (wow)
  	* draw_markers - same, but the markers are most likely 3D glyphs
  	* draw_path_collection - same
  	* draw_quad_mesh - same in 3D

  	need to add:
  	* draw_3D_mesh - the main primitive for 3D
  	* draw_volumetric_data - tricky, but important to get right (later)
    """
    pass

class Event():
    """
    Event handlers for VR controllers
    """
    pass



class Artist():
    pass
