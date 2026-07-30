#!/usr/bin/env python3
"""Emit the D mark as an SVG path, straight from the system font.

The favicon ships as an inline SVG data URI, so the glyph has to be a path - a <text>
element would render in whatever font the viewer happens to have installed.

    pip install fonttools
    python3 tools/make-mark.py           # favicon data URI, paste into <link rel="icon">
    python3 tools/make-mark.py --touch   # SVG source for apple-touch-icon.png

To change the face, point FONT/FACE at another family and check the result at 16px
before committing - even stroke weights survive icon sizes, Didone hairlines do not.
"""
import sys

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTCollection

FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
FACE = 1  # Helvetica Neue Bold
GLYPH = "D"
INK_LIGHT = "#1a1a1a"  # --fg, light scheme: the tab strip is light, so the mark is dark
INK_DARK = "#e8e5de"   # --fg, dark scheme
DARK = "#14140f"       # --bg, dark scheme


def path(pad, box=64):
    """Glyph outline scaled to fit a `box`-unit square with `pad` units of margin."""
    font = TTCollection(FONT).fonts[FACE]
    glyphs = font.getGlyphSet()
    glyph = glyphs[GLYPH]

    bounds = BoundsPen(glyphs)
    glyph.draw(bounds)
    x0, y0, x1, y1 = bounds.bounds
    w, h = x1 - x0, y1 - y0

    avail = box - 2 * pad
    scale = avail / max(w, h)
    tx = pad + (avail - w * scale) / 2 - x0 * scale
    ty = pad + (avail - h * scale) / 2 - y0 * scale

    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    # Negative y scale: font units grow upward, SVG grows downward.
    glyph.draw(TransformPen(pen, Transform(scale, 0, 0, -scale, tx, box - ty)))
    return pen.getCommands()


def svg(inner):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{inner}</svg>'


if "--touch" in sys.argv:
    # Opaque on purpose: iOS composites transparency onto black, and applies its own
    # corner mask, so no rounding here either. Normal icon margin.
    print(svg(f'<rect width="64" height="64" fill="{DARK}"/>'
              f'<path fill="{INK_DARK}" d="{path(13)}"/>'))
else:
    # The tab strip follows the OS scheme, so the mark has to as well - a light mark
    # would disappear on a light strip. SVG favicons honour prefers-color-scheme, and
    # the default fill is the light-scheme ink so a browser that ignores the query
    # still shows something legible.
    style = (f"<style>path{{fill:{INK_LIGHT}}}"
             f"@media(prefers-color-scheme:dark){{path{{fill:{INK_DARK}}}}}</style>")
    mark = svg(f'{style}<path d="{path(1)}"/>')
    encoded = (mark.replace('"', "'").replace("#", "%23")
                   .replace("<", "%3C").replace(">", "%3E"))
    print(f"data:image/svg+xml,{encoded}")
