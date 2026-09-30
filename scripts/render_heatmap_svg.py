"""Render data/contributions.json as an animated contribution heatmap SVG.

53-week x 7-day grid, GitHub-style green ramp, diagonal slide-in reveal that
plays once and freezes (SMIL). Month labels, Less->More legend, stats footer.
stdlib only.

Usage: python scripts/render_heatmap_svg.py [output.svg]   (default: contrib-heatmap.svg)
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import xml.sax.saxutils as sax
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
MUTED = "#8b949e"

CELL, GAP, PITCH = 10, 4, 14
LEFT, TOP = 8, 24
TOTAL_W = 860


def build_svg(days: list[dict], total: int) -> str:
    # The contributions HTML lists day cells row-major (all Sundays, then all
    # Mondays, ...), so position cells by date, not by document order.
    first_date = min(dt.date.fromisoformat(d["date"]) for d in days)
    first_sunday = first_date - dt.timedelta(days=(first_date.weekday() + 1) % 7)
    grid: dict[tuple[int, int], dict] = {}
    for d in days:
        delta = (dt.date.fromisoformat(d["date"]) - first_sunday).days
        grid[(delta // 7, delta % 7)] = d
    n_weeks = max(w for w, _ in grid) + 1
    weeks: list[list[dict | None]] = [
        [grid.get((w, d)) for d in range(7)] for w in range(n_weeks)
    ]
    grid_bottom = TOP + 7 * PITCH
    H = grid_bottom + 42

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}" height="{H}" '
        f'viewBox="0 0 {TOTAL_W} {H}" role="img" aria-label="contribution graph">',
        # month labels
        f'<g font-family="{MONO}" font-size="10" fill="{MUTED}">',
    ]
    prev_month = None
    for w in range(n_weeks):
        sunday = first_sunday + dt.timedelta(days=7 * w)
        month = sunday.strftime("%b")
        if month != prev_month:
            p.append(f'<text x="{LEFT + w * PITCH}" y="14">{month}</text>')
            prev_month = month
    p.append("</g>")

    # day cells, diagonal reveal
    for w, week in enumerate(weeks):
        for d, day in enumerate(week):
            if not day:
                continue
            x, y = LEFT + w * PITCH, TOP + d * PITCH
            color = PALETTE[min(day["level"], 4)]
            begin = (w + d) * 0.035
            tip = sax.escape(f"{day['count']} contributions on {day['date']}")
            p.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" opacity="0">'
                f"<title>{tip}</title>"
                f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" '
                f'begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
                f"</rect>"
            )

    # footer: stats left, legend right
    fy = grid_bottom + 26
    legend_x = TOTAL_W - 8
    legend_cells = "".join(
        f'<rect x="{legend_x - 96 + i * 14}" y="{fy - 10}" width="10" height="10" '
        f'rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )
    p.append(
        f'<g font-family="{MONO}" font-size="12" fill="{MUTED}">'
        f'<text x="{LEFT}" y="{fy}">{total} contributions in the last year</text>'
        f'<text x="{legend_x - 132}" y="{fy}">Less</text>'
        f"{legend_cells}"
        f'<text x="{legend_x - 34}" y="{fy}">More</text>'
        f"</g>"
    )
    p.append("</svg>")
    return "\n".join(p)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "contrib-heatmap.svg")
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    Path(out).write_text(build_svg(data["days"], data["total"]))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
