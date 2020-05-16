# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 22:32:37 2020

@author: mark.shovman

"""

import numpy as np
import PlotVR as pvr

pos = np.random.rand(30, 3) - 0.5

# pvr.scene()
# pvr.scene(num="Scatterplot")
# pvr.scene()
# pvr.scene(num="Scatterplot")

pvr.plot(x=pos[:,0], y = pos[:,1], z = pos[:,2], color="#0FADE2")
pvr.plot(x=pos[:,2], y = pos[:,0], z = pos[:,1], color="#EF2D5E")
pvr.plot(x=pos[:,1], y = pos[:,2], z = pos[:,0], color="#0F0")

pvr.show()

# import matplotlib.pyplot as plt
# plt.plot()