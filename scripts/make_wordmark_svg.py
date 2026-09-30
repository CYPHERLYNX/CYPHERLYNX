#!/usr/bin/env python3
"""3D extruded ASCII wordmark inside a macOS-style terminal window.

Avi-style hero panel: the wordmark wipes in left-to-right (SMIL clip).
Regenerate locally when the wordmark changes:
    python3 scripts/make_wordmark_svg.py
"""
import pyfiglet
import html
import os

OUT = os.path.expanduser('~/workspace/profile-redesign/wordmark.svg')
TITLE = 'x0d4n@github: ~$ ./wordmark.sh --3d'
TEXT = 'X0D4N'

FONT_SIZE = 24
LINE_H = 30
ART_W = 560          # forced via textLength so extrusion layers align exactly
PAD_X = 40
TOP = 78
LAYERS = 5           # extrusion depth steps
STEP = 1.6           # px offset per layer
DEEP = (18, 28, 42)      # darkest extrusion shade
FACE = (230, 237, 243)   # bright face


def main():
    raw = pyfiglet.figlet_format(TEXT, font='ansi_shadow')
    lines = [l.rstrip() for l in raw.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    width = max(len(l) for l in lines)
    lines = [l.ljust(width) for l in lines]  # uniform advance under textLength

    art_h = len(lines) * LINE_H
    W = PAD_X * 2 + ART_W + int(LAYERS * STEP) + 10
    H = int(TOP + art_h + LAYERS * STEP + 34)

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
    p.append('<defs><linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/>'
             '</linearGradient>')
    p.append(f'<clipPath id="wipe"><rect x="{PAD_X}" y="{TOP - LINE_H}" width="0" '
             f'height="{art_h + LAYERS * STEP + LINE_H}">'
             f'<animate attributeName="width" from="0" to="{ART_W + LAYERS * STEP + 20}" '
             f'begin="0.25s" dur="1.5s" fill="freeze"/></rect></clipPath></defs>')
    p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg2)"/>')
    p.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
             f'fill="none" stroke="#30363d" stroke-width="1"/>')
    p.append(f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="#30363d"/>')
    for cx, col in ((20, '#ff5f56'), (36, '#ffbd2e'), (52, '#27c93f')):
        p.append(f'<circle cx="{cx}" cy="15" r="5" fill="{col}"/>')
    p.append(f'<text x="{W / 2:.0f}" y="19" fill="#7d8590" font-size="12" '
             f'text-anchor="middle">{html.escape(TITLE)}</text>')

    p.append('<g clip-path="url(#wipe)">')
    for li in range(LAYERS):
        t = li / (LAYERS - 1)
        col = tuple(int(DEEP[i] + (FACE[i] - DEEP[i]) * t ** 1.6) for i in range(3))
        fill = '#%02x%02x%02x' % col
        dx = dy = (LAYERS - 1 - li) * STEP
        for i, line in enumerate(lines):
            y = TOP + i * LINE_H + dy
            p.append(
                f'<text xml:space="preserve" x="{PAD_X + dx:.1f}" y="{y:.1f}" '
                f'fill="{fill}" font-size="{FONT_SIZE}" textLength="{ART_W}" '
                f'lengthAdjust="spacingAndGlyphs">{html.escape(line)}</text>'
            )
    p.append('</g>')
    p.append('</svg>')

    with open(OUT, 'w') as f:
        f.write(''.join(p))
    print(f'wrote {OUT} ({W}x{H})')


if __name__ == '__main__':
    main()
