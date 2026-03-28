"""
Generate docs/screenshot.png — a synthetic preview of a PlotVR scene.

Uses a simple isometric projection to render three coloured point clusters,
a wireframe bounding box, and RGB axis indicators — matching what the
A-Frame scene looks like in-browser.
"""
import math
import numpy as np
from PIL import Image, ImageDraw

# ── canvas ──────────────────────────────────────────────────────────────────
W, H = 960, 540
img = Image.new("RGB", (W, H), "#0a0a12")
draw = ImageDraw.Draw(img)

# ── isometric projection (same orientation as the A-Frame camera default) ───
# Camera sits forward-right-above the unit cube, tilted down ~25°.
SCALE = 200
CX, CY = W // 2 - 20, H // 2 + 30   # scene centre on canvas

# Basis vectors in pixel space for each world axis
# X→ right-forward, Y→ up, Z→ left-forward (left-hand scene)
ax = np.array([ math.cos(math.radians(30)),  math.sin(math.radians(15))])
ay = np.array([0.0, -1.0])
az = np.array([-math.cos(math.radians(30)),  math.sin(math.radians(15))])


def proj(x, y, z):
    v = ax * x + ay * y + az * z
    return (int(CX + v[0] * SCALE), int(CY + v[1] * SCALE))


# ── wireframe bounding box ───────────────────────────────────────────────────
corners = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
edges = [
    (0,1),(2,3),(4,5),(6,7),   # Z edges
    (0,2),(1,3),(4,6),(5,7),   # Y edges
    (0,4),(1,5),(2,6),(3,7),   # X edges
]
BOX_COLOR = "#1a2a4a"
for i, j in edges:
    draw.line([proj(*corners[i]), proj(*corners[j])], fill=BOX_COLOR, width=1)

# ── axis lines ───────────────────────────────────────────────────────────────
AXIS_W = 3
draw.line([proj(0,0,0), proj(1,0,0)], fill="#e74c3c", width=AXIS_W)   # X red
draw.line([proj(0,0,0), proj(0,1,0)], fill="#2ecc71", width=AXIS_W)   # Y green
draw.line([proj(0,0,0), proj(0,0,1)], fill="#3498db", width=AXIS_W)   # Z blue

# ── tick labels on axes ──────────────────────────────────────────────────────
TICK = 6
for v in (0.25, 0.5, 0.75, 1.0):
    for axis, color in [("x","#e74c3c"), ("y","#2ecc71"), ("z","#3498db")]:
        if axis == "x": p = proj(v, 0, 0)
        elif axis == "y": p = proj(0, v, 0)
        else: p = proj(0, 0, v)
        draw.ellipse((p[0]-2, p[1]-2, p[0]+2, p[1]+2), fill=color)

# ── scatter points (three clusters) ─────────────────────────────────────────
rng = np.random.default_rng(42)

CLUSTERS = [
    (np.array([0.20, 0.25, 0.20]), "#0FADE2", 50),
    (np.array([0.75, 0.70, 0.30]), "#EF2D5E", 50),
    (np.array([0.50, 0.20, 0.78]), "#2ECC71", 50),
]

# Collect all points for depth sorting (painter's algorithm)
all_pts = []
for centre, colour, n in CLUSTERS:
    pts = rng.normal(loc=centre, scale=0.07, size=(n, 3)).clip(0, 1)
    for p in pts:
        # depth = distance from camera (rough: sum of coords for iso view)
        depth = p[0] + p[1] + p[2]
        all_pts.append((depth, p, colour))

all_pts.sort(key=lambda t: -t[0])   # back-to-front

R = 6   # sphere radius in pixels
for depth, p, colour in all_pts:
    px, py = proj(*p)
    # Simple shading: slightly darken based on depth
    shade = 0.75 + 0.25 * (depth / 3.0)
    c = tuple(min(255, int(int(colour[i*2+1:i*2+3], 16) * shade)) for i in range(3))
    draw.ellipse((px-R, py-R, px+R, py+R), fill=c, outline=None)
    # Specular highlight
    draw.ellipse((px-R//2-1, py-R//2-1, px-R//2+2, py-R//2+2), fill="#ffffff")

# ── legend ────────────────────────────────────────────────────────────────────
LX, LY = W - 190, 24
draw.text((LX, LY - 4), "PlotVR - 3D scatter preview", fill="#888888")
for i, (_, colour, _) in enumerate(CLUSTERS):
    y = LY + 22 + i * 22
    draw.ellipse((LX, y+2, LX+12, y+14), fill=colour)
    draw.text((LX+18, y), f"Cluster {i+1}", fill="#cccccc")

# ── watermark / code snippet ─────────────────────────────────────────────────
snippet = [
    "import PlotVR as pvr",
    "pvr.plot(x, y, z, color='#0FADE2')",
    "pvr.show()",
]
SW, SH = 320, 70
sx, sy = 16, H - SH - 12
draw.rectangle((sx, sy, sx+SW, sy+SH), fill="#0d1117", outline="#30363d")
for i, line in enumerate(snippet):
    draw.text((sx+10, sy+8+i*20), line, fill="#8b949e" if i == 0 else "#c9d1d9")

img.save("docs/screenshot.png")
print(f"Saved docs/screenshot.png  ({W}×{H})")
