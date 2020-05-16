# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 22:32:37 2020

@author: mark.shovman

"""

import numpy as np
import PlotVR as pvr

pos = np.random.rand(100, 3)*10 - 5

# pvr.scene()
# pvr.scene(num="Scatterplot")
# pvr.scene()
# pvr.scene(num="Scatterplot")

pvr.plot(x=pos[:,0], y = pos[:,1], z = pos[:,2])

pvr.show()

# import matplotlib.pyplot as plt
# plt.plot()