#!/usr/bin/env python3
"""Check that every collapsible <details> block will actually render its markdown.

Python-Markdown hands block-level raw HTML straight to the browser, so markdown
inside a `<details>` that starts its own line is NOT parsed unless the tag
carries a `markdown` attribute and the `md_in_html` extension is enabled.

Nothing fails when it is missing. `mkdocs build --strict` is happy, the page
builds, and the `<summary>` looks right — but the body ships to the browser as
literal source, so a practice-problem solution renders as one run-together
paragraph of `1. **Multiplex the CPU** — ...`. It is invisible until somebody
expands the block, and on a lecture page that is usually a student the night
before an exam.

Three checks:
  1. mkdocs.yml enables `md_in_html`, without which the attribute does nothing
  2. every block-level `<details>` carries a `markdown` attribute
  3. `<details>` and `</details>` are balanced in each file, and each block
     opens with a `<summary>`

Inline `<details><summary>Answer</summary>...</details>` — the shape the prep
pages use inside a numbered list — is span-level HTML. The paragraph around it
is parsed normally, so it neither needs nor wants the attribute; those are
checked for the opposite mistake.

Run any time:  python3 utils/check_details.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

OPEN = re.compile(r"<details\b[^>]*>")
CLOSE = re.compile(r"</details\s*>")
HAS_ATTR = re.compile(r"\bmarkdown\s*=")

missing_attr = []   # block-level tag with no markdown attribute
inline_attr = []    # inline tag that should not have one
unbalanced = []     # open/close counts disagree
no_summary = []     # block opens without a <summary>
n_block = n_inline = 0

# 1. The extension the attribute depends on.
if not re.search(r"^\s*-\s*md_in_html\s*$", MKDOCS.read_text(), re.M):
    sys.exit("FAIL: mkdocs.yml does not enable `md_in_html` — every "
             "`markdown=\"1\"` attribute in docs/ is being ignored")

for md in sorted(DOCS.rglob("*.md")):
    rel = md.relative_to(ROOT)
    lines = md.read_text().splitlines()

    opens = sum(len(OPEN.findall(l)) for l in lines)
    closes = sum(len(CLOSE.findall(l)) for l in lines)
    if opens != closes:
        unbalanced.append(f"{rel}: {opens} <details> vs {closes} </details>")

    for n, line in enumerate(lines, 1):
        tag = OPEN.search(line)
        if not tag:
            continue
        # Block-level: the tag is the whole line. Anything else is span-level
        # HTML inside a paragraph or list item, which Markdown parses already.
        if line.strip() == tag.group(0):
            n_block += 1
            if not HAS_ATTR.search(tag.group(0)):
                missing_attr.append(f"{rel}:{n}: {tag.group(0)} needs markdown=\"1\"")
            nxt = lines[n] if n < len(lines) else ""
            if "<summary" not in nxt:
                no_summary.append(f"{rel}:{n}: block opens without a <summary> on the next line")
        else:
            n_inline += 1
            if HAS_ATTR.search(tag.group(0)):
                inline_attr.append(f"{rel}:{n}: inline <details> should not carry a markdown attribute")

for b in missing_attr:
    print(f"missing attr   {b}")
for b in inline_attr:
    print(f"inline attr    {b}")
for b in no_summary:
    print(f"no summary     {b}")
for b in unbalanced:
    print(f"unbalanced     {b}")

print(f"\ndetails blocks checked: {n_block} block-level, {n_inline} inline")
if missing_attr or inline_attr or no_summary or unbalanced:
    sys.exit(f"FAIL: {len(missing_attr)} unrendered block(s), "
             f"{len(inline_attr)} stray attribute(s), "
             f"{len(no_summary)} without a summary, "
             f"{len(unbalanced)} unbalanced file(s)")
print("every collapsible block will render its markdown")
