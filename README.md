# Aim

**Create a python module that allows plotting data in VR and manipulating the view there.**

## MVP
* 3D scatterplot with axes
* scale/rotate/move interaction
* home/save/2D snapshot menu
* API similar to matplotlib or seaborn

# User stories

## single-user
* Danny (teh data analyst) is writing python code ananlysing some data.
* He imports this module, and calls its function to plot his data.
* A plot window opens, similar to 3D plot of matplotlib, but with an additional button 'View in VR'
* Danny presses this button, puts on his VR headset, and sees the plot in VR
* He can rotate/move/scale it with controllers, like in Google Sketch
* there is a hand-held palette menu (again, like in Sketch) with options like 'Reset View', 'Save 3D', 'Save 2D' etc.

## asymmetric collaboration
* Alice (Danny's colleague) comes up to his table to discuss the data, but there is only one VR headset.
* Danny, wearing the headset, positions a 'camera' gewgaw (3D UI element) in VR.
* this gewgaw corresponds and controls the window view of the data that Alice can see and interact with.
* it has a look and feel of a smartphone, with a screen on the back that shows exactly what Alice is seeing
* it can be moved by Danny in VR, or by Alice outside, using the standard 3D mouse controls.
* mouse selection by Alice is visible to Danni as a ray coming from the gewgaw, highlighting parts of the plotted data.

## symmetric collaboration
* TBD

# Tech stack
* A-frame for VR rendering
* BS4 for html generation
* pandas for data

#TODOs
* check existing solutions (if any)
	* https://www.google.co.il/search?hl=iw&q=data+plot+in+vr
	* https://medium.com/inborn-experience/data-visualization-in-virtual-reality-a-vr-demo-project-a31c577aaefc done in Unity, a week-lomg student project, nice use of grid and shadow.
	* https://studio.knightlab.com/results/exploring-data-visualization-in-vr/uncharted-territory-datavis-vr/ great ideation, journalism, done in sketchfab. GOOD REFERENCES, must read
	* https://store.steampowered.com/app/595490/LookVR/ - commercial, sleek, TODO: TEST	
	* https://github.com/mustafasaifee42/VR-ScatterPlot d3 simple project, a-frame
	* https://pdfs.semanticscholar.org/c2b4/1be6d8bb88181d1f94641e585b0fad7c2f96.pdf lovely paper from 2001, interesting 3D sparse heatmap idea
	* https://www.storybench.org/how-to-make-a-simple-virtual-reality-data-visualization/ tutorial for d3 and Three.js
	* https://www.reddit.com/r/oculus/comments/4getrl/anyone_got_matplotlib_running_in_vr/ reddit thread from 3 yrs ago complaining there is nothing. useful as user requirements
	* https://github.com/guiglass/GravityVR/ VR and python, via pyqtgraph
	
	* https://www.reddit.com/r/virtualreality/comments/5bs5en/lib_for_data_visualization_in_vr/ - TO READ
	* what happened to nirvaniq labs?
	* https://medium.com/inside-machine-learning/visualizing-high-dimensional-data-in-augmented-reality-2150a7e62d5b IBM AR project
	
* check other options for tech stack
    * https://ephtracy.github.io/index.html?page=mv_main - MagicaVoxel, for volumetric viz
	* PyOpenVR, PyOpenGL, PyQt4
