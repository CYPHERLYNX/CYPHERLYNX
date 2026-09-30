"""Fetch the public contribution calendar (no auth, no token) and store raw data.

Source: https://github.com/users/<username>/contributions — the same public
HTML fragment the profile page itself uses. stdlib only.

Usage: python scripts/fetch_contributions.py [username]   (default: CYPHERLYNX)
Writes: data/contributions.json
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "profile-art-bot/1.0 (+https://github.com/CYPHERLYNX)"

TD_RE = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"')
TIP_RE = re.compile(r"<tool-tip[^>]*>([^<]*)</tool-tip>")
TOTAL_RE = re.compile(r"([\d,]+)\s+contributions?\s+in the last year")
COUNT_RE = re.compile(r"([\d,]+)\s+contribution")


def fetch(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", "replace")


def parse(html: str) -> tuple[list[dict], int]:
    tds = TD_RE.findall(html)
    tips = TIP_RE.findall(html)
    days: list[dict] = []
    for i, (date, level) in enumerate(tds):
        count = 0
        if i < len(tips):
            m = COUNT_RE.search(tips[i])
            if m:
                count = int(m.group(1).replace(",", ""))
        days.append({"date": date, "level": int(level), "count": count})
    m = TOTAL_RE.search(html)
    total = int(m.group(1).replace(",", "")) if m else sum(d["count"] for d in days)
    return days, total


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else "CYPHERLYNX"
    html = fetch(username)
    days, total = parse(html)
    out = {
        "username": username,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "total": total,
        "days": days,
    }
    dest = ROOT / "data" / "contributions.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2))
    print(f"wrote {dest} ({len(days)} days, {total} contributions)")


if __name__ == "__main__":
    main()
