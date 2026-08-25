#!/usr/bin/env python3
"""Regenerate the Lectures and Assignments sections of mkdocs.yml.

The lecture nav in CS 315 is ~80 hand-maintained lines that must stay in sync
with the filenames, and it drifts. Generate it instead.

Lecture files are named `{WW}-cs326-{YYYY-MM-DD}-{kebab-topic}.md`, each with a
matching `-slides.html`. Sorting by filename sorts by week then date, which is
chronological, so no ordering metadata is needed.

Run from the repo root:  python3 utils/gen_nav.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

# Assignment pages, in the order they matter to a student, not alphabetical.
ASSIGNMENT_ORDER = [
    ("exercises.md", "All Exercises"),
    ("lab00-setup.md", "Lab 00 · Setup"),
    ("practice-set-01.md", "Practice Set 1"),
    ("midterm-1.md", "Midterm 1"),
    ("practice-set-02.md", "Practice Set 2"),
    ("midterm-2.md", "Midterm 2"),
    ("practice-set-03.md", "Practice Set 3"),
    ("final.md", "Final Exam"),
    ("extra-credit.md", "Extra Credit"),
]


def title_of(md: Path) -> str:
    """The page's own `# Heading`, so nav labels cannot drift from content."""
    for line in md.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md.stem


def lecture_entries():
    out = []
    for md in sorted((DOCS / "lectures").glob("*.md")):
        m = re.match(r"(\d+)-cs326-(\d{4})-(\d{2})-(\d{2})-(.+)", md.stem)
        if not m:
            print(f"  ! skipping oddly-named {md.name}", file=sys.stderr)
            continue
        _, _, mm, dd, _ = m.groups()
        month = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(mm)]
        label = f"{month} {int(dd)} · {title_of(md)}"
        out.append((label, f"lectures/{md.name}"))
        slides = md.with_name(md.stem + "-slides.html")
        if slides.exists():
            out.append((f"{month} {int(dd)} · Slides", f"lectures/{slides.name}"))
    return out


def assignment_entries():
    out = []
    seen = set()
    for name, label in ASSIGNMENT_ORDER:
        if (DOCS / "assignments" / name).exists():
            out.append((label, f"assignments/{name}"))
            seen.add(name)
    # Anything not in the explicit order still gets listed rather than lost.
    for md in sorted((DOCS / "assignments").glob("*.md")):
        if md.name not in seen:
            out.append((title_of(md), f"assignments/{md.name}"))
    return out


def yaml_label(label: str) -> str:
    """Quote a nav label. Titles routinely contain a colon ("Rust I: Values..."),
    which YAML would read as a nested mapping and reject."""
    return '"' + label.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(entries, indent="      "):
    if not entries:
        return f"{indent}[]"
    return "\n".join(
        f"{indent}- {yaml_label(label)}: {path}" for label, path in entries
    )


def replace_section(text: str, header: str, body: str) -> str:
    """Replace `  - <header>:` and everything indented under it."""
    pattern = re.compile(
        rf"^(  - {re.escape(header)}:).*?(?=^  - |\Z)", re.S | re.M
    )
    if not pattern.search(text):
        raise SystemExit(f"could not find nav section '{header}' in mkdocs.yml")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n", text)


def main():
    lectures = lecture_entries()
    assignments = assignment_entries()

    text = MKDOCS.read_text()
    text = replace_section(text, "Assignments", render(assignments))
    text = replace_section(text, "Lectures", render(lectures))
    MKDOCS.write_text(text)

    pages = sum(1 for l, _ in lectures if "Slides" not in l)
    decks = len(lectures) - pages
    print(f"nav updated: {pages} lecture pages, {decks} slide decks, "
          f"{len(assignments)} assignment pages")


if __name__ == "__main__":
    main()
