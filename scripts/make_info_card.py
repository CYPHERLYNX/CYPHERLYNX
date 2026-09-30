"""Hand-authored neofetch-style info card SVG.

Dark panel, one soft-blue accent for keys, light gray values. Each row fades
and slides in on a stagger (SMIL, plays once, freezes). No emojis, no invented
claims — factual content only.

Usage: python scripts/make_info_card.py [output.svg]
"""

from __future__ import annotations

import sys
import xml.sax.saxutils as sax

W, H = 490, 330
BG, BORDER = "#0d1117", "#21262d"
TITLE, KEY, VAL, PROMPT = "#ffffff", "#79c0ff", "#c9d1d9", "#7ee787"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

TITLE_LINE = "cypherlynx@github"
ROWS: list[tuple[str, str]] = [
    ("user", "CYPHERLYNX (X0D4N)"),
    ("role", "final-year student · software developer"),
    ("focus", "cybersecurity enthusiast"),
    ("stack", "TypeScript · Electron · Python · Flask · SQLite"),
    ("security", "detection engineering · SOAR/EDR automation"),
    ("tooling", "network-security suite (Nmap · Scapy)"),
    ("now", "shipping one original AI tool every day"),
]


def build_svg() -> str:
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="about CYPHERLYNX">',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
        # title bar
        f'<g font-family="{MONO}" font-size="14">',
        f'<text x="24" y="42" fill="{PROMPT}" font-weight="700">$</text>',
        f'<text x="44" y="42" fill="{TITLE}" font-weight="700">~</text>',
        f'<text x="62" y="42" fill="{VAL}">{sax.escape(TITLE_LINE)}</text>',
        "</g>",
        f'<line x1="24" x2="{W - 24}" y1="60" y2="60" stroke="{BORDER}"/>',
    ]
    y = 92
    for i, (k, v) in enumerate(ROWS):
        begin = 0.4 + i * 0.32
        key_txt = (
            f'<text x="24" y="{y}" fill="{KEY}" font-weight="700">{sax.escape(k)}</text>'
            if k
            else ""
        )
        kx = 150 if k else 24
        p.append(
            f'<g opacity="0" font-family="{MONO}" font-size="13">'
            f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" '
            f'begin="{begin:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="-10 0" to="0 0" begin="{begin:.2f}s" dur="0.4s" fill="freeze"/>'
            f"{key_txt}"
            f'<text x="{kx}" y="{y}" fill="{VAL}">{sax.escape(v)}</text>'
            f"</g>"
        )
        y += 30
    p.append("</svg>")
    return "\n".join(p)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    with open(out, "w") as f:
        f.write(build_svg())
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
