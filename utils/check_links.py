#!/usr/bin/env python3
"""Check the links and page-to-schedule wiring that `mkdocs build --strict` cannot.

`--strict` validates markdown links between pages. It does NOT validate the
schedule's links, because `docs/index.md` renders them as raw HTML through a
Jinja loop — so a renamed lecture silently 404s from the site's home page,
which is the most-used navigation surface in the course.

Three checks:
  1. every link in docs/schedule.yml resolves to a built page under site/ —
     the Links column and the Sec01/Sec02 summaries alike
  2. every `exercise` row has a Prep link — enforced once docs/prep/ holds at
     least one page (before that, a notice only, so the site builds while the
     prep pages are still being written)
  3. every docs/prep/*.md is dated to a session on the schedule

Run after `mkdocs build`:  python3 utils/check_links.py
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PREP = ROOT / "docs/prep"
MONTHS = {m: i for i, m in enumerate(
    ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

if not SITE.is_dir():
    sys.exit("no site/ directory — run `mkdocs build` first")


def resolves(url):
    """Does an internal schedule URL have a built page under site/?"""
    p = SITE / url.lstrip("/")
    return (p if p.suffix else p / "index.html").exists()


sched = yaml.safe_load((ROOT / "docs/schedule.yml").read_text())
bad, ok = [], 0
no_prep = []
dates = {}  # "2026-10-01" -> (week, day, type)

for wk in sched["weeks"]:
    for day in ("tuesday", "thursday", "friday"):
        d = wk.get(day)
        if not d:
            continue
        mon, dd = d["date"].split()
        dates[f"2026-{MONTHS[mon]:02d}-{int(dd):02d}"] = (wk["week"], day, d["type"])
        links = d.get("links") or []
        if d["type"] == "exercise" and not any(l["text"] == "Prep" for l in links):
            no_prep.append(f"week {wk['week']} {day} ({d['date']}): {d['topic']}")
        # The per-section resources render as links in the same cell; only the
        # summary is internal, the recording is a Zoom URL.
        section_links = [{"text": f"{sec} {kind}", "url": url}
                         for sec in ("section_01", "section_02")
                         for kind, url in (d.get(sec) or {}).items()]
        for link in links + section_links:
            url = link["url"]
            if url.startswith("http"):
                continue
            if resolves(url):
                ok += 1
            else:
                bad.append(f"week {wk['week']} {day}: {link['text']} -> {url}")

print(f"schedule links resolved: {ok}")
if bad:
    print(f"\n{len(bad)} broken:")
    for b in bad:
        print(f"  {b}")

# Prep pages: names must parse, and their date must be a session date.
prep_pages = sorted(PREP.glob("*.md")) if PREP.is_dir() else []
bad_prep = []
for md in prep_pages:
    m = re.match(r"(\d+)-cs326-(\d{4}-\d{2}-\d{2})-prep-(.+)", md.stem)
    if not m:
        bad_prep.append(f"{md.name}: not named WW-cs326-YYYY-MM-DD-prep-slug.md")
        continue
    stamp = m.group(2)
    if stamp not in dates:
        bad_prep.append(f"{md.name}: {stamp} is not a session date")
    elif dates[stamp][2] != "exercise":
        bad_prep.append(f"{md.name}: {stamp} is a {dates[stamp][2]} row, not an exercise session")
print(f"prep pages checked: {len(prep_pages)}")
if bad_prep:
    print(f"\n{len(bad_prep)} prep page(s) mis-dated:")
    for b in bad_prep:
        print(f"  {b}")

# Every exercise session needs a Prep link — once the prep pages exist at all.
if prep_pages:
    if no_prep:
        print(f"\n{len(no_prep)} exercise session(s) without a Prep link:")
        for b in no_prep:
            print(f"  {b}")
else:
    print(f"notice: docs/prep/ has no pages yet — {len(no_prep)} exercise "
          f"session(s) have no Prep link; this becomes an error once the first "
          f"prep page exists")
    no_prep = []

if bad or bad_prep or no_prep:
    sys.exit(1)
print("all schedule links resolve to built pages")
