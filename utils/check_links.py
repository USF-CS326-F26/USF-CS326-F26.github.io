#!/usr/bin/env python3
"""Check the links and page-to-schedule wiring that `mkdocs build --strict` cannot.

`--strict` validates markdown links between pages. It does NOT validate the
schedule's links, because `docs/index.md` renders them as raw HTML through a
Jinja loop — so a renamed lecture silently 404s from the site's home page,
which is the most-used navigation surface in the course. Nor does it look
inside the reveal.js decks, which MkDocs copies through as static files.

Seven checks:
  1. every link in docs/schedule.yml resolves to a built page under site/ —
     the Links column and the Sec01/Sec02 summaries alike
  2. every `exercise` row has a Prep link — enforced once docs/prep/ holds at
     least one page (before that, a notice only, so the site builds while the
     prep pages are still being written)
  3. every docs/prep/*.md is dated to a session on the schedule
  4. every `lecture` row has exactly one "Lecture" link and at most one
     "Slides" link, and the final-exam row (Dec 8) has an "Optional reading"
     link — the page read in place of a lecture that week
  5. every docs/lectures/*.md is dated, by its filename, to a lecture or exam
     row in gen_schedule.sessions(), since that is the only way a page reaches
     the schedule
  6. every prep page's **Lecture:** header cites docs/lectures pages that exist
     and whose WW prefix is the prep page's own WW
  7. every relative link in docs/lectures/*-slides.html (href and src
     attributes, and markdown links in the slide source) resolves inside the
     built site/; #fragments are ignored, and http(s)/mailto links skipped

Run after `mkdocs build`:  python3 utils/check_links.py
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PREP = ROOT / "docs/prep"
LECTURES = ROOT / "docs/lectures"
MONTHS = {m: i for i, m in enumerate(
    ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
FINAL_READING_DATE = "Dec 8"  # the exam row whose page is read, not lectured

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_schedule import sessions, stamp  # noqa: E402

if not SITE.is_dir():
    sys.exit("no site/ directory — run `mkdocs build` first")


def resolves(url):
    """Does an internal schedule URL have a built page under site/?"""
    p = SITE / url.lstrip("/")
    return (p if p.suffix else p / "index.html").exists()


sched = yaml.safe_load((ROOT / "docs/schedule.yml").read_text())
bad, ok = [], 0
no_prep = []
bad_rows = []
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
        # A lecture row shows the page presented that day, and its deck.
        texts = [l["text"] for l in links]
        where = f"week {wk['week']} {day} ({d['date']})"
        if d["type"] == "lecture":
            n_lec, n_sl = texts.count("Lecture"), texts.count("Slides")
            if n_lec != 1:
                bad_rows.append(f"{where}: {n_lec} \"Lecture\" links, want exactly 1")
            if n_sl > 1:
                bad_rows.append(f"{where}: {n_sl} \"Slides\" links, want at most 1")
        if d["date"] == FINAL_READING_DATE and "Optional reading" not in texts:
            bad_rows.append(f"{where}: {d['type']} row has no \"Optional reading\" link")
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

if not any(d == stamp(FINAL_READING_DATE) for d in dates):
    bad_rows.append(f"no {FINAL_READING_DATE} row on the schedule")

print(f"schedule links resolved: {ok}")
if bad:
    print(f"\n{len(bad)} broken:")
    for b in bad:
        print(f"  {b}")

lecture_rows = sum(1 for t in dates.values() if t[2] == "lecture")
print(f"lecture rows checked: {lecture_rows}")
if bad_rows:
    print(f"\n{len(bad_rows)} schedule row(s) with the wrong lecture links:")
    for b in bad_rows:
        print(f"  {b}")

# Prep pages: names must parse, and their date must be a session date.
prep_pages = sorted(PREP.glob("*.md")) if PREP.is_dir() else []
bad_prep = []
for md in prep_pages:
    m = re.match(r"(\d+)-cs326-(\d{4}-\d{2}-\d{2})-prep-(.+)", md.stem)
    if not m:
        bad_prep.append(f"{md.name}: not named WW-cs326-YYYY-MM-DD-prep-slug.md")
        continue
    st = m.group(2)
    if st not in dates:
        bad_prep.append(f"{md.name}: {st} is not a session date")
    elif dates[st][2] != "exercise":
        bad_prep.append(f"{md.name}: {st} is a {dates[st][2]} row, not an exercise session")
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

# Lecture pages: the schedule attaches a page only to the lecture or exam row
# of its date, so a page dated to any other day never appears on it.
row_type = {stamp(s["date"]): (s["type"], s["day"], s["date"]) for s in sessions()}
lecture_pages = sorted(LECTURES.glob("*.md"))
bad_lec = []
for md in lecture_pages:
    m = re.match(r"(\d+)-cs326-(\d{4}-\d{2}-\d{2})-(.+)", md.stem)
    if not m:
        bad_lec.append(f"{md.name}: not named WW-cs326-YYYY-MM-DD-slug.md")
        continue
    st = m.group(2)
    if st not in row_type:
        bad_lec.append(f"{md.name}: {st} is not a session date")
    elif row_type[st][0] not in ("lecture", "exam"):
        typ, day, date = row_type[st]
        bad_lec.append(f"{md.name}: {date} is a {day} {typ} row, not a lecture or exam")
print(f"lecture pages checked: {len(lecture_pages)}")
if bad_lec:
    print(f"\n{len(bad_lec)} lecture page(s) not dated to a lecture or exam row:")
    for b in bad_lec:
        print(f"  {b}")

# Prep headers: a prep page belongs to week WW, so the lecture it names must be
# week WW's page, not a page from the week it was taught in under the old plan.
bad_cite, n_cites = [], 0
for md in prep_pages:
    m = re.match(r"(\d+)-cs326-", md.stem)
    if not m:
        continue  # already reported as mis-named above
    ww = m.group(1)
    header = next((l for l in md.read_text().splitlines() if "**Lecture:**" in l), None)
    if header is None:
        bad_cite.append(f"{md.name}: no **Lecture:** header line")
        continue
    cited = re.findall(r"lectures/([\w-]+)\.md", header)
    if not cited:
        bad_cite.append(f"{md.name}: **Lecture:** header cites no docs/lectures page")
    for stem in cited:
        n_cites += 1
        if not (LECTURES / f"{stem}.md").exists():
            bad_cite.append(f"{md.name}: **Lecture:** cites {stem}.md, which does not exist")
        elif stem.split("-")[0] != ww:
            bad_cite.append(f"{md.name}: **Lecture:** cites {stem}.md, "
                            f"a week-{stem.split('-')[0]} page, not week {ww}")
print(f"prep **Lecture:** citations checked: {n_cites}")
if bad_cite:
    print(f"\n{len(bad_cite)} prep header citation(s) wrong:")
    for b in bad_cite:
        print(f"  {b}")


# Decks: MkDocs copies docs/lectures/*-slides.html to site/lectures/ untouched,
# so their links are relative to site/lectures/ and nothing else checks them.
def blank(s):
    """`s` as spaces, newlines kept, so offsets and line numbers still hold."""
    return re.sub(r"[^\n]", " ", s)


ATTR = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']*)["']""")
MDLINK = re.compile(r"\]\(\s*<?([^)\s>]+)")
TEXTAREA = re.compile(r"(<textarea\b[^>]*>)(.*?)(</textarea>)", re.S)
FENCE = re.compile(r"^[ \t]*```.*?^[ \t]*```[^\n]*$", re.S | re.M)
INLINE = re.compile(r"`[^`\n]*`")
SKIP = ("http://", "https://", "mailto:", "//", "javascript:", "data:")
site_root = os.path.normpath(SITE)
deck_base = os.path.join(site_root, "lectures")

decks = sorted(LECTURES.glob("*-slides.html"))
bad_deck, n_deck = [], 0
for deck in decks:
    text = deck.read_text()
    # Inside the slide source, code is code: `v[i](x)` or a pasted <a href> in a
    # fence is not a link. Blank it out (same length) before looking.
    found = []  # (offset, url)
    outside = TEXTAREA.sub(lambda m: m.group(1) + blank(m.group(2)) + m.group(3), text)
    found += [(m.start(1), m.group(1)) for m in ATTR.finditer(outside)]
    for ta in TEXTAREA.finditer(text):
        src = ta.group(2)
        for code in (FENCE, INLINE):
            src = code.sub(lambda m: blank(m.group(0)), src)
        base = ta.start(2)
        found += [(base + m.start(1), m.group(1)) for m in ATTR.finditer(src)]
        found += [(base + m.start(1), m.group(1)) for m in MDLINK.finditer(src)]
    for off, url in sorted(found):
        path = url.split("#", 1)[0].split("?", 1)[0]
        if not path or path.lower().startswith(SKIP):
            continue
        n_deck += 1
        line = text.count("\n", 0, off) + 1
        target = os.path.normpath(os.path.join(
            site_root if path.startswith("/") else deck_base, unquote(path).lstrip("/")))
        if target != site_root and not target.startswith(site_root + os.sep):
            bad_deck.append(f"{deck.name}:{line}: {url} leaves site/")
            continue
        if path.endswith("/") or not os.path.splitext(target)[1]:
            target = os.path.join(target, "index.html")
        if not os.path.exists(target):
            bad_deck.append(f"{deck.name}:{line}: {url} -> "
                            f"site/{os.path.relpath(target, site_root)} not built")
print(f"deck links resolved: {n_deck - len(bad_deck)} of {n_deck} in {len(decks)} decks")
if bad_deck:
    print(f"\n{len(bad_deck)} broken deck link(s):")
    for b in bad_deck:
        print(f"  {b}")

if bad or bad_prep or no_prep or bad_rows or bad_lec or bad_cite or bad_deck:
    sys.exit(1)
print("all schedule links resolve to built pages")
print("lecture rows, lecture page dates, prep headers, and deck links all check out")
