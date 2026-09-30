#!/usr/bin/env python3
"""Photo -> monochrome ASCII art inside a macOS-style terminal window.

Avi-style hero panel: the portrait types in line by line (SMIL).
Regenerate locally when the photo changes:
    python3 scripts/make_portrait_svg.py
"""
from PIL import Image, ImageOps, ImageFilter
import html
import os

SRC = os.path.expanduser('~/workspace/profile-images/user-profile-reference.jpg')
OUT = os.path.expanduser('~/workspace/profile-redesign/x0d4n-ascii.svg')
TITLE = 'x0d4n@github: ~$ ./portrait.sh'

COLS = 100
RAMP = ' .:-=+*#%@'
FONT_SIZE = 12.9
LINE_H = 13.8
ART_W = 800          # forced via textLength so every row aligns exactly
PAD_X = 20
TOP = 48.1
FG = '#c9d1d9'


def to_ascii(path):
    im = Image.open(path).convert('L')
    # upscale the small source, normalize contrast, kill JPEG noise
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=2)
    im = im.filter(ImageFilter.GaussianBlur(0.9))
    # monospace cells are ~1.78x taller than wide; compensate for aspect
    cell_aspect = LINE_H / (FONT_SIZE * 0.6)
    rows = max(20, int(COLS * (im.height / im.width) / cell_aspect))
    cw, ch = im.width / COLS, im.height / rows
    px = im.load()
    lines = []
    for r in range(rows):
        chars = []
        for c in range(COLS):
            tot = n = 0
            for y in range(int(r * ch), int((r + 1) * ch)):
                for x in range(int(c * cw), int((c + 1) * cw)):
                    tot += px[x, y]
                    n += 1
            b = tot / max(n, 1) / 255
            chars.append(RAMP[min(int(b * len(RAMP)), len(RAMP) - 1)])
        lines.append(''.join(chars))
    return lines


def main():
    lines = to_ascii(SRC)
    W = 840
    H = int(TOP + len(lines) * LINE_H + 26)

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
    p.append('<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/>'
             '</linearGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>')
    p.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
             f'fill="none" stroke="#30363d" stroke-width="1"/>')
    p.append(f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="#30363d"/>')
    for cx, col in ((20, '#ff5f56'), (36, '#ffbd2e'), (52, '#27c93f')):
        p.append(f'<circle cx="{cx}" cy="15" r="5" fill="{col}"/>')
    p.append(f'<text x="{W / 2:.0f}" y="19" fill="#7d8590" font-size="12" '
             f'text-anchor="middle">{html.escape(TITLE)}</text>')

    for i, line in enumerate(lines):
        y = TOP + i * LINE_H
        p.append(
            f'<text xml:space="preserve" x="{PAD_X}" y="{y:.1f}" fill="{FG}" '
            f'font-size="{FONT_SIZE}" opacity="0" textLength="{ART_W}" '
            f'lengthAdjust="spacingAndGlyphs">{html.escape(line)}'
            f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" '
            f'begin="{i * 0.055:.2f}s" dur="0.01s" fill="freeze"/></text>'
        )
    p.append('</svg>')

    with open(OUT, 'w') as f:
        f.write(''.join(p))
    print(f'wrote {OUT} ({W}x{H}, {len(lines)} rows)')


if __name__ == '__main__':
    main()
