# CLAUDE.md — PlotVR Codebase Guide

## Project Overview

PlotVR is a Python library for 3D data visualization in VR. It provides a matplotlib-inspired API that generates A-Frame (WebXR) HTML scenes from Python, designed for use in Jupyter notebooks and VR headsets.

**Status**: Early-stage / prototype (April–May 2020). Core scatter-plot workflow works; many planned features are stubs or TODOs.

---

## Repository Structure

```
plot-vr/
├── PlotVR/                     # Main Python package
│   ├── __init__.py             # Re-exports everything from _plotvr
│   ├── _plotvr.py              # Scripting layer (public API)
│   ├── _base.py                # Base classes: Artist, Renderer, Event
│   ├── _artists.py             # Concrete artists: Scene, Frame, MarkerSet
│   └── _scene_template.html   # A-Frame HTML template (loaded at runtime)
├── try_plotvr.py               # Quick example / smoke test
├── try_plotvr.ipynb            # Jupyter notebook example
└── README.md                   # Project vision, user stories, diary
```

There is no `setup.py`, `pyproject.toml`, or `requirements.txt`. Dependencies are implicit.

---

## Architecture

The design intentionally mirrors matplotlib's three-layer architecture:

```
Scripting layer  (_plotvr.py)    →  scene(), plot(), show()
Artist layer     (_artists.py)   →  Scene, Frame, MarkerSet
Backend layer    (_base.py)      →  Artist (base), Renderer (stub), Event (stub)
```

### Layer responsibilities

| Layer | File | Role |
|---|---|---|
| Scripting | `_plotvr.py` | Global state, convenience functions (like `plt.plot`) |
| Artist | `_artists.py` | Build A-Frame scene graph via BeautifulSoup |
| Backend | `_base.py` | Abstract base; `Renderer` and `Event` are documented stubs |

### Key design decisions

- **Scene → Frame → MarkerSet** hierarchy (analogous to Figure → Axes → Line2D in matplotlib)
- Each `Artist` holds a reference to the BeautifulSoup document (`self.soup`) inherited from its parent
- Each `Artist` holds a reference to its A-Frame entity (`self._a_entity`)
- Global state in `_plotvr.py` tracks `__all_scenes` and `__current_scene` (like `plt.gcf()`)

---

## Public API

```python
import PlotVR as pvr

pvr.scene(num=None)                              # Create or switch to a scene (int or string name)
pvr.plot(x, y, z, color, size, marker)          # Add a scatter plot to the current scene
pvr.show()                                       # Render all scenes to HTML and display in Jupyter
```

**`pvr.plot()` parameters:**

| Parameter | Default | Description |
|---|---|---|
| `x`, `y`, `z` | — | Coordinate arrays (numpy arrays) |
| `color` | `"#FFFFFF"` | CSS color string, or array of per-point color strings |
| `size` | `0.01` | Marker radius (A-Frame world units), or per-point array of floats |
| `marker` | `'sphere'` | Marker shape: `'sphere'`, `'box'`, `'cone'`, `'cylinder'`, `'dodecahedron'`, `'octahedron'`, `'tetrahedron'`, `'torus'` |

**Typical usage:**
```python
import numpy as np
import PlotVR as pvr

pos = np.random.rand(30, 3)
pvr.plot(x=pos[:,0], y=pos[:,1], z=pos[:,2], color="#0FADE2")
pvr.show()
```

Calling `pvr.plot()` without first calling `pvr.scene()` auto-creates Scene 1.

---

## HTML / A-Frame Output

- `Scene.show()` writes a file `./PlotVR_{title}.html` to the **current working directory**
- The file is based on `_scene_template.html` with artist-generated entities injected into `<div id="content">`
- A-Frame version: **1.0.4**
- External JS dependencies (loaded via CDN): A-Frame, aframe-extras, super-hands

### Scene template components

| Element | Purpose |
|---|---|
| `#content` | Injection point for Python-generated entities |
| `#framebounds` | Semi-transparent blue box showing data bounds |
| `#axes` | RGB-colored axis lines (red=X, green=Y, blue=Z) |
| Controllers | Left/right VR controllers with physics + gesture (super-hands) |
| `frame_mix` mixin | Makes objects hoverable, grabbable, stretchable, draggable |
| `phase-shift` component | Custom A-Frame component toggling controller physics on grip |

---

## Dependencies

**Python:**
- `numpy` — array operations
- `beautifulsoup4` — HTML generation (`bs4`)
- `IPython` — Jupyter display (`IPython.core.display`, `IPython.display.IFrame`)

**JavaScript (CDN, in HTML template):**
- A-Frame 1.0.4
- aframe-extras
- super-hands

---

## Development Conventions

### Naming
- Internal modules use a leading underscore: `_plotvr.py`, `_base.py`, `_artists.py`
- Public symbols are declared in `__all__` in each module

### Artist pattern
When adding a new artist class:
1. Inherit from `Artist` in `_base.py`
2. Call `super().__init__(parent)` to inherit `self.soup` and register parent
3. Create a new A-Frame tag using `self.soup.new_tag(...)` and assign to `self._a_entity`
4. Append the new entity to `parent.get_a_entity()`
5. Append child artists with `self._a_entity.append(...)`

### Scene/Frame disambiguation
- `Scene` = top-level container; corresponds to a matplotlib `Figure`
- `Frame` = the 3D plotting area within a scene; corresponds to matplotlib `Axes`
- `axes` (the colored lines in `Frame`) = the visual axis indicators, not the Frame itself

### Global state (scripting layer)
- `__all_scenes`: `dict` mapping scene key (int or str) to `Scene` instance
- `__current_scene`: most recently active `Scene`
- `scene(num)` creates a new `Scene` if `num` not in `__all_scenes`, otherwise switches to it

---

## Known Issues / Incomplete Areas

- **Jupyter IFrame**: Loading local HTML files in some Jupyter environments fails with `Not allowed to load local resource`. Workaround is to save the file within the project directory (already done in `Scene.show()`).
- **`Renderer` and `Event`**: Both are documented stubs in `_base.py`. No rendering primitives are implemented yet.
- **Multiple frames per scene**: Not yet supported. `Scene` always creates exactly one `Frame` on construction.
- **Axes/Frame separation**: The `Frame` class conflates the visual bounding box and the axes; these should be separated (noted in TODO in `_plotvr.py`).
- **Hand/controller interaction**: VR controller events are wired in the HTML template but the Python `Event` class is not implemented.
- **No package metadata**: There is no `setup.py` / `pyproject.toml`. Install by placing the `PlotVR/` directory on the Python path.

---

## Workflow

Development happens on the `master` branch directly.

There are no build, lint, or test commands. The typical development loop is:

1. Edit Python files in `PlotVR/`
2. Run `try_plotvr.py` or open `try_plotvr.ipynb` to verify output
3. Open the generated `PlotVR_Figure 1.html` in a WebXR-capable browser

To test in VR: open the HTML file in a browser connected to a WebXR device (e.g. Oculus Browser on Quest).

---

## Roadmap

Tracked as GitHub issues on mark-shovman/plot-vr.

- [x] Separate `Frame` (position in scene) from `Axes` (scale, tick marks, labels)
- [ ] #1 Revive and fix bitrot
- [ ] #4 Add wobble/physics to frames
- [x] #5 Add color, size, and marker type parameters to scatter plots
- [ ] #6 Implement `Renderer` backend primitives
- [ ] #7 Implement VR controller `Event` handling
- [ ] #8 Support multiple frames per scene with automatic layout
- [ ] #9 Add palette menu (reset view, save 3D, save 2D)
- [ ] #10 Improve Jupyter integration (avoid local file restrictions)
- [ ] #11 Add packaging (`setup.py` / `pyproject.toml`)
