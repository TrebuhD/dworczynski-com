#!/usr/bin/env python3
"""Emit the node mark.

The mark is a single filled circle - a node, the point on a Chladni plate that never
moves. No typeface, so no font dependency and nothing to convert to outlines.

    python3 tools/make-mark.py           # favicon data URI, paste into <link rel="icon">
    python3 tools/make-mark.py --touch   # SVG source for apple-touch-icon.png
    python3 tools/make-mark.py --card    # SVG for the OG card, in the card's ink

Teal clears 3.9:1 on the light background and 4.5:1 on the dark one, so a single flat
colour works everywhere and the favicon needs no prefers-color-scheme rule. If the accent
ever changes, check it against BOTH backgrounds - a colour that only works on one means
the favicon dies in half of all browsers.
"""
import sys

ACCENT = "#2e8b84"  # teal
DARK = "#14140f"    # --bg, dark scheme

# Radii in a 64-unit box. The favicon runs larger because it is never seen bigger than
# 32px; the touch icon needs the margin iOS expects around an app glyph.
R_ICON = 18
R_TOUCH = 15


def svg(inner):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{inner}</svg>'


def node(r, fill):
    return f'<circle cx="32" cy="32" r="{r}" fill="{fill}"/>'


if "--touch" in sys.argv:
    # Opaque on purpose: iOS composites transparency onto black and applies its own
    # corner mask, so no rounding here.
    print(svg(f'<rect width="64" height="64" fill="{DARK}"/>{node(R_TOUCH, ACCENT)}'))
elif "--card" in sys.argv:
    print(svg(node(R_ICON, ACCENT)))
else:
    mark = svg(node(R_ICON, ACCENT))
    encoded = (mark.replace('"', "'").replace("#", "%23")
                   .replace("<", "%3C").replace(">", "%3E"))
    print(f"data:image/svg+xml,{encoded}")
