#!/usr/bin/env python3
"""Contribution heatmap -> animated SVG, Avi-style.

Real data from data/contributions.json (see scripts/fetch_contributions.py).
Cells pop in column by column via CSS keyframes; month + weekday labels and
the yearly total caption match the GitHub look. Runs daily in CI:
    python scripts/render_heatmap_svg.py
"""
import json
import os
from datetime import date, timedelta

BASE = os.path.expanduser('~/workspace/profile-redesign')
DATA = os.path.join(BASE, 'data', 'contributions.json')
OUT = os.path.join(BASE, 'contrib-heatmap.svg')

CELL = 12
GAP = 4
STEP = CELL + GAP
LEFT = 34     # weekday labels
TOP = 24      # month labels
COLORS = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
WEEKDAYS = {1: 'Mon', 3: 'Wed', 5: 'Fri'}


def main():
    with open(DATA) as f:
        d = json.load(f)
    days = sorted(d['days'], key=lambda x: x['date'])
    total = d.get('total', sum(x['count'] for x in days))

    first = date.fromisoformat(days[0]['date'])
    # align to the Sunday-starting column grid GitHub uses
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    last = date.fromisoformat(days[-1]['date'])
    n_weeks = ((last - start).days // 7) + 1

    grid = {}
    for e in days:
        dt = date.fromisoformat(e['date'])
        col = (dt - start).days // 7
        row = (dt.weekday() + 1) % 7  # Monday=1..Sunday=0 -> Sun row 0
        grid[(col, row)] = e['level']

    W = LEFT + n_weeks * STEP + 8
    H = TOP + 7 * STEP + 44

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="888" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">')
    p.append('''<style>
  text.lbl { fill:#7d8590; font-size:13px; font-weight:600; }
  text.total { fill:#e6edf3; font-size:15px; font-weight:700; }
  .c { opacity:0; animation:pop 0.5s ease-out forwards; }
  @keyframes pop { 0%{opacity:0} 60%{opacity:1} 100%{opacity:1} }
</style>''')

    # month labels
    seen = set()
    for col in range(n_weeks):
        dt = start + timedelta(days=col * 7)
        key = (dt.year, dt.month)
        if key not in seen and dt.day <= 7:
            seen.add(key)
            x = LEFT + col * STEP
            p.append(f'<text class="lbl" x="{x}" y="14">{dt.strftime("%b")}</text>')

    # weekday labels
    for row, name in WEEKDAYS.items():
        y = TOP + row * STEP + CELL - 2
        p.append(f'<text class="lbl" x="0" y="{y}">{name}</text>')

    # cells, staggered by column so the graph sweeps left -> right
    for (col, row), level in sorted(grid.items()):
        x = LEFT + col * STEP
        y = TOP + row * STEP
        color = COLORS[max(0, min(level, 4))]
        delay = col * 0.028
        p.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{color}" style="animation-delay:{delay:.3f}s"/>'
        )

    p.append(f'<text class="total" x="{LEFT}" y="{H - 14}">'
             f'{total:,} contributions in the last year</text>')
    p.append('</svg>')

    with open(OUT, 'w') as f:
        f.write(''.join(p))
    print(f'wrote {OUT} ({n_weeks} weeks, total {total})')


if __name__ == '__main__':
    main()
