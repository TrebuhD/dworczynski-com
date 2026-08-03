#!/usr/bin/env python3
"""Emit the node mark.

The mark is a node - the point on a Chladni plate that never moves - drawn as a solid
core with a dithered rim, screened the same way the plate itself is: a 4x4 ordered
(Bayer) matrix over a radial falloff. No typeface, so no font dependency.

    python3 tools/make-mark.py           # favicon data URI, paste into <link rel="icon">
    python3 tools/make-mark.py --touch   # SVG source for apple-touch-icon.png
    python3 tools/make-mark.py --card    # SVG for the OG card
    python3 tools/make-mark.py --solid   # undithered, if the dither ever misbehaves

Emerald clears 3.5:1 on the light background and 4.8:1 on the dark one, so one flat
colour works everywhere and the favicon needs no prefers-color-scheme rule. Check any
replacement against BOTH backgrounds - a colour that only works on one means the favicon
dies in half of all browsers. The page's dark-scheme mint (#85d9ab) fails this test:
1.5:1 on the light background.

GRID is 32 on purpose. It divides the 64-unit box evenly, so every coordinate is an
integer and the path stays short; coarser grids (16) break the circular silhouette and
the mark goes lopsided at small sizes.
"""
import sys

ACCENT = "#3f9166"  # emerald
DARK = "#0b1712"    # --bg, dark scheme
BOX = 64
GRID = 32

# The same family of ordered screen the plate's shader uses.
BAYER4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]


def smoothstep(a, b, x):
    if a == b:
        return 0.0 if x < a else 1.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def dithered(r_core, r_outer, grid=GRID):
    """Cells where a radial falloff beats the ordered threshold.

    Solid inside r_core, dissolving to nothing at r_outer.
    """
    n = len(BAYER4)
    cell = BOX / grid
    num = lambda v: f"{v:g}"
    parts = []
    for j in range(grid):
        for i in range(grid):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            d = ((cx - BOX / 2) ** 2 + (cy - BOX / 2) ** 2) ** 0.5
            density = 1.0 - smoothstep(r_core, r_outer, d)
            if density <= 0:
                continue
            if density > (BAYER4[j % n][i % n] + 0.5) / (n * n):
                x, y, s = i * cell, j * cell, cell
                parts.append(f"M{num(x)} {num(y)}h{num(s)}v{num(s)}h-{num(s)}z")
    return f'<path d="{"".join(parts)}"/>'


def svg(inner, fill=ACCENT):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX} {BOX}" '
            f'fill="{fill}" shape-rendering="crispEdges">{inner}</svg>')


# Icon radii, and the touch icon scaled down for the margin iOS expects around a glyph.
# A small core with a far-out falloff: the rim dissolves over most of the mark's radius
# rather than sitting as a thin edge, so the dither is the mark rather than a detail.
ICON = (9, 25)
TOUCH = (7, 21)

if "--solid" in sys.argv:
    body = '<circle cx="32" cy="32" r="18"/>'
else:
    body = dithered(*ICON)

if "--touch" in sys.argv:
    # Opaque on purpose: iOS composites transparency onto black and applies its own
    # corner mask, so no rounding here.
    inner = dithered(*TOUCH)
    print(svg(f'<rect width="{BOX}" height="{BOX}" fill="{DARK}"/>{inner}'))
elif "--card" in sys.argv:
    print(svg(body))
else:
    mark = svg(body)
    encoded = (mark.replace('"', "'").replace("#", "%23")
                   .replace("<", "%3C").replace(">", "%3E"))
    print(f"data:image/svg+xml,{encoded}")
