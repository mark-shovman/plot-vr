# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 22:32:37 2020

@author: mark.shovman

TODO: make into a class
TODO: add methods equivalent to plt.figure, plt.plot and plt.show
"""

import os
import tempfile
import webbrowser

from bs4 import BeautifulSoup

import numpy as np

pos = np.random.rand(100, 3)*10 - 5


html = """
<html>
  <head>
    <script src="https://aframe.io/releases/1.0.4/aframe.min.js"></script>
  </head>
  <body>
    <a-scene>
        <a-entity light="type:directional; castShadow:true;" position="0 4 1"></a-entity>
        <a-entity id="axes" position="0 1.5 -4" scale="0.1 0.1 0.1" shadow="receive: false">>
        </a-entity>
        <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#202020" shadow="receive: true">></a-plane>
        <a-sky color="#000000"></a-sky>
    </a-scene>
  </body>
</html>
"""

soup = BeautifulSoup(html)
scene = soup.find(id='axes')

for i in range(len(pos)):
    scene.append(soup.new_tag("a-sphere", position=f"{pos[i,0]} {pos[i,1]} {pos[i,2]}", radius="0.1", color="#EF2D5E"))

with tempfile.NamedTemporaryFile('w', delete=False, prefix='Figure_', suffix='.html') as f:
    f.write(str(soup))
    webbrowser.open('file://' + os.path.realpath(f.name), new=0)