#!/usr/bin/env bash
# Render og.png using the live shader from index.html, so the card cannot drift from
# the site. Requires Chrome (for WebGPU in headless) and python3.
#
#   ./tools/build-og.sh [style] [mode]
#     style: wash | glow | lit | poster   (default lit)
#     mode:  dark | light                 (default dark)
set -euo pipefail
cd "$(dirname "$0")/.."

STYLE_NAME="${1:-lit}"
MODE="${2:-dark}"
case "$STYLE_NAME" in
  wash) STYLE=0 ;;
  glow) STYLE=1 ;;
  lit) STYLE=2 ;;
  poster) STYLE=3 ;;
  *) echo "unknown style: $STYLE_NAME (wash|glow|lit|poster)" >&2; exit 1 ;;
esac

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME" >&2; exit 1; }

WORK="$(mktemp -d)"
cleanup() {
  [ -f "$WORK/pid" ] && kill "$(cat "$WORK/pid")" 2>/dev/null || true
  rm -rf "$WORK"
}
trap cleanup EXIT

cp tools/og-gen.html "$WORK/"

# The generator fetches the shader as a sibling file. Extract it from index.html so
# there is exactly one copy of the WGSL in the repo.
python3 - "$WORK/shader.wgsl" <<'PY'
import pathlib, re, sys
src = pathlib.Path("index.html").read_text()
m = re.search(r"const SHADER = `(.*?)`;", src, re.S)
if not m:
    sys.exit("could not find the shader in index.html")
pathlib.Path(sys.argv[1]).write_text(m.group(1))
PY

python3 -m http.server 8799 --directory "$WORK" >/dev/null 2>&1 &
echo $! > "$WORK/pid"
sleep 1

"$CHROME" --headless=new --disable-gpu-sandbox --enable-unsafe-webgpu --use-angle=metal \
  --screenshot="$PWD/og.png" --window-size=1200,630 --virtual-time-budget=5000 \
  "http://localhost:8799/og-gen.html?mode=$MODE&style=$STYLE&t=40" >/dev/null 2>&1

# Chrome writes ~230K of 24-bit RGB. The card is a dither screen over two flat tones, so
# a 4-bit palette is lossless in practice and lands around 55K. Optional - without
# pngquant on PATH the card is just larger.
if command -v pngquant >/dev/null 2>&1; then
  pngquant --quality=65-92 --speed 1 --strip --force --output og.png og.png
fi

echo "og.png <- $STYLE_NAME / $MODE ($(du -h og.png | cut -f1))"
