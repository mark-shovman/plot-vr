# Aim

**Create a python module that allows plotting data in VR and manipulating the view there.**

## MVP
* 3D scatterplot of two or more data sets, with axes
* scale/rotate/move interaction
* home/save/2D snapshot menu
* API similar to matplotlib or seaborn

#User stories

##Single-user
* Danny (teh data analyst) is writing python code analysing some data.
* He imports this module, and calls its function to plot his data.
* A plot window opens, similar to 3D plot of matplotlib, but with an additional button 'View in VR'
* Danny presses this button, puts on his VR headset, and sees the plot in VR
* He can rotate/move/scale it with controllers, like in Google Sketch
* There is a hand-held palette menu (again, like in Sketch) with options like 'Reset View', 'Save 3D', 'Save 2D' etc.

##Asymmetric collaboration
* Alice (Danny's colleague) comes up to his table to discuss the data, but there is only one VR headset.
* Danny, wearing the headset, positions a 'camera' gewgaw (3D UI element) in VR.
* this gewgaw corresponds and controls the window view of the data that Alice can see and interact with.
* it has a look and feel of a smartphone, with a screen on the back that shows exactly what Alice is seeing
* it can be moved by Danny in VR, or by Alice outside, using the standard 3D mouse controls.
* mouse selection by Alice is visible to Danni as a ray coming from the gewgaw, highlighting parts of the plotted data.

##Symmetric collaboration
* TBD: Danny and Alice are both in VR, in the same virtual space created by Danny

##Asymmetric presentation
* TBD: Danny in VR, Bob (the boss, not a data analyst) not in VR; -or- Bob in VR, Danny outside talking Bob through it

##Symmetric presentation
* TBD: Danny, Bob and Alice are all in the same VR space, Danny tells a story.

#Tech stack
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

#Diary and ruminations

##12 Apr 2020
Much of the functionality I need here is already implemented in matplotlib. would it be possible to use it instead of rewriting it? Started reading http://www.aosabook.org/en/matplotlib.html , a chapter on matplotlib architecture. Lovely reading, so far seems like injecting my bits into matplotlib is a good idea.

##14 Apr 2020
Learning about matplotlib, and considering my case.
* The backend layer is different, and the render primitives are probably different
	* **FigureCanvas** is now a space
	* **Renderer** has to be aware of 3D
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

	* **Event** should handle controllers, not kbd/mouse
* the artist layer is very different, with 3D istead of 2D in most artists;
	* existing primitives: Line2D, Rectangle, Circle, and Text - are totally irrelevant
	* likely primitives: Line3D, Mesh, Text, GlyphSet... - need to think
	* composites can be the same, after all, that's what graphs are - axes, labels, ticks, etc...
	* Text3D primitive has to have orientation and aslo billboarding behaviour
	* GlyphSet (or MarkerSet) Same idea, a scatter of identical 3D meshes, optionally with different size and colour
* the scripting layer is similar, but will probably have to be tweaked considerably

So, it seems that, though I like the architecture, most of it will have to be rewritten. still, it might be useful to keep to the architecture, not for code reusal (although mpl axes3D manage somehow), but for readability by developers familiar with matplotlib.

### offtopic - corona analyses and visualisations
* https://jhepc.github.io/about.html Excellence in Visualisation contest. interesting. Entries must be submitted by June, 1st to the form at https://forms.gle/SrexmkDwiAmDc7ej7
* https://vita.had.co.nz/papers/letter-value-plot.html - https://seaborn.pydata.org/generated/seaborn.boxenplot.html#seaborn.boxenplot - similar to my stackplot, but Balalaika is still better :D
* Idea - combo of linear and log scale, where an axis is linear till 10**n, and log afterwards. must sketch and try - should be clearly visible, yet not messy.

##18 Apr 2020
* Still thinking about architecture. Backend is currently a-frame, good idea to abstract it in case a-frame is no good. However, I think it's safe to assume that the backend will have some sort of a scenegraph implemented, so transforms are basically taken care of there - thus, it makes sense to tie artists closer to the backend. For a-frame, at least, I think, an artist should have a connection to the point in scenegraph; renderer should be a thin wrapper around a-frame soup.

* might have to dive into https://threejs.org/ directly.

* can/should I avoid writing dedicated entites in a-frame? I can, in principle, move all the backend, and even artists, to a-frame primitives, and leave only thin wrappers in python.

* I wonder how mpl handles statefulness - what's the backend, for instance. Checked in C:\Anaconda3\Lib\site-packages\matplotlib. OMG what a mess O.O

##30 May 2020

* Since April, implemented Artist/Scripting layer, multiple Scenes, and multiple plots in a scene. Did not log much because COVID-19.

* Next step - Axes, bounding boxes, etc.

* Tried to show the scene in Jupyter via IFrame. Almost works, but fails on 'jquery.min.js:6084 Not allowed to load local resource'. There are ways around it, e.g. saving the temp file in a project dorectory. Later.







