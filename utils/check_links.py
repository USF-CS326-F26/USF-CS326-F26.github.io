#!/usr/bin/env python3
"""Check the links that `mkdocs build --strict` cannot.

`--strict` validates markdown links between pages. It does NOT validate the
schedule's links, because `docs/index.md` renders them as raw HTML through a
Jinja loop — so a renamed lecture silently 404s from the site's home page,
which is the most-used navigation surface in the course.

Run after `mkdocs build`:  python3 utils/check_links.py
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

if not SITE.is_dir():
    sys.exit("no site/ directory — run `mkdocs build` first")

sched = yaml.safe_load((ROOT / "docs/schedule.yml").read_text())
bad, ok = [], 0

for wk in sched["weeks"]:
    for day in ("tuesday", "thursday", "friday"):
        d = wk.get(day)
        if not d:
            continue
        for link in d.get("links") or []:
            url = link["url"]
            if url.startswith("http"):
                continue
            p = SITE / url.lstrip("/")
            target = p if p.suffix else p / "index.html"
            if target.exists():
                ok += 1
            else:
                bad.append(f"week {wk['week']} {day}: {link['text']} -> {url}")

print(f"schedule links resolved: {ok}")
if bad:
    print(f"\n{len(bad)} broken:")
    for b in bad:
        print(f"  {b}")
    sys.exit(1)
print("all schedule links resolve to built pages")
