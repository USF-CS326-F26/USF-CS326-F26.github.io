#!/usr/bin/env python3
"""Convert British spellings to American English across the site.

The generated material mixes "behaviour", "virtualise", "labelled" and
"optimisation" into pages that otherwise read as American English. This script
rewrites the known offenders, preserving case ("Behaviour" -> "Behavior",
"BEHAVIOUR" -> "BEHAVIOR") and an un/re/de/mis/dis/pre prefix
("uninitialised" -> "uninitialized", "reorganise" -> "reorganize").

The word list is explicit, generated from stems, so look-alikes are safe:
"optimistic", "realism", "programmer", "programmed", "fulfilled", "enrolled"
and "concentrate" never match. "analyses" is left alone (it is the plural noun
as often as the British verb) and every hit is printed for a human to judge.
"practise/practised/practising" (British verb forms) become
"practice/practiced/practicing"; every other "practice" hit is printed too,
except the obvious nouns "Practice Set" / "Practice Problems".

Where it does NOT rewrite:
  - inline code spans and fenced code blocks -- except comment lines inside a
    fence (`//`, `#`, `;`, `/*`, `<!-- -->`), the trailing `// ...` comment on a
    code line, and ```mermaid fences (their labels are visible prose);
  - URLs and file paths (anything ending in .rs .md .html .ld .toml .py .yml
    .yaml .json .sh .S, with an optional :line suffix);
  - in `-slides.html`: only the <textarea data-template> body (markdown rules)
    and visible HTML text are processed; <style>, <script> and tag markup are
    never touched.
British words seen inside those protected regions are listed under [CODE] so
the apply phase can decide by hand. A heading whose text changes is listed
under [HEADING] because its anchor changes with it.

Scope and skips are the same as rename_exercises.py: docs/**/*.md, *.html,
*.yml and CONTRIBUTING.md; skip docs/schedule.yml and
docs/assignments/exercises.md (generated), site/, utils/, .git/, and the two
L01 files unless --include-l01.

Usage (from anywhere):

    python3 utils/americanize.py                 # dry run (default)
    python3 utils/americanize.py --apply         # write in place
    python3 utils/americanize.py --paths docs/syllabus.md
    python3 utils/americanize.py --self-test
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# --------------------------------------------------------------------------
# Word list
# --------------------------------------------------------------------------
ISE_STEMS = [
    "virtualis", "optimis", "initialis", "recognis", "minimis", "summaris",
    "specialis", "serialis", "synchronis", "organis", "realis", "prioritis",
    "utilis", "normalis",
]
ISE_SUFFIXES = ["e", "es", "ed", "ing", "er", "ers", "ation", "ations", "able"]

WORDS = {stem + suf: stem[:-1] + "z" + suf for stem in ISE_STEMS for suf in ISE_SUFFIXES}
WORDS.update({
    "behaviour": "behavior", "behaviours": "behaviors",
    "behavioural": "behavioral", "behaviourally": "behaviorally",
    "labelled": "labeled", "labelling": "labeling",
    "catalogue": "catalog", "catalogues": "catalogs",
    "catalogued": "cataloged", "cataloguing": "cataloging",
    "honour": "honor", "honours": "honors", "honoured": "honored",
    "honouring": "honoring", "honourable": "honorable",
    "analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing",
    "analyser": "analyzer", "analysers": "analyzers",  # not "analyses"
    "signalling": "signaling", "signalled": "signaled",
    "modelled": "modeled", "modelling": "modeling",
    "practise": "practice", "practised": "practiced", "practising": "practicing",
    "judgement": "judgment", "judgements": "judgments",
    "neighbour": "neighbor", "neighbours": "neighbors", "neighbouring": "neighboring",
    "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods",
    "centre": "center", "centres": "centers", "centred": "centered", "centring": "centering",
    "colour": "color", "colours": "colors", "coloured": "colored",
    "colouring": "coloring", "colourful": "colorful",
    "grey": "gray", "greys": "grays", "greyed": "grayed", "greyscale": "grayscale",
    "licence": "license", "licences": "licenses",
    "defence": "defense", "defences": "defenses",
    "programme": "program", "programmes": "programs",
    "fulfil": "fulfill", "fulfils": "fulfills", "fulfilment": "fulfillment",
    "enrol": "enroll", "enrols": "enrolls", "enrolment": "enrollment",
    "travelling": "traveling", "travelled": "traveled",
    "traveller": "traveler", "travellers": "travelers",
    "cancelled": "canceled", "cancelling": "canceling",
    "totalling": "totaling", "totalled": "totaled",
    "whilst": "while", "amongst": "among", "learnt": "learned", "spelt": "spelled",
})
EXCLUDE = {"afterwards", "towards", "analyses"}
assert not EXCLUDE & set(WORDS)

WORD_RX = re.compile(
    r"(?<![A-Za-z0-9_])(?P<prefix>(?:un|re|de|mis|dis|pre)?)(?P<word>"
    + "|".join(sorted(WORDS, key=len, reverse=True))
    + r")(?![A-Za-z0-9_])",
    re.I,
)
ANALYSES_RX = re.compile(r"\banalyses\b", re.I)
PRACTICE_RX = re.compile(r"\bpractice\b", re.I)
PRACTICE_NOUN_RX = re.compile(r"\bpractice(?:[- ]sets?|[- ]problems?)\b", re.I)  # obvious nouns, not listed

# Protected regions.
CODE_SPAN_RX = re.compile(r"(`+)(.+?)\1")
URL_RX = re.compile(r"(?:https?://|www\.)[^\s)>\]\"']+")
PATH_RX = re.compile(
    r"(?<![A-Za-z0-9_])[\w./~-]*\.(?:rs|md|html|ld|toml|py|yml|yaml|json|sh|S)"
    r"(?::\d+(?:-\d+)?)?(?![A-Za-z0-9_])"
)
FENCE_RX = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})\s*(?P<lang>[\w+-]*)")
COMMENT_LINE_RX = re.compile(r"^\s*(?://|#|;|/\*|\*(?!\*)|<!--)")
TRAILING_COMMENT_RX = re.compile(r"\s//(?=\s)")
HEADING_RX = re.compile(r"^\s{0,3}#{1,6}\s+\S")
TEXTAREA_RX = re.compile(r"(<textarea data-template>)(.*?)(</textarea>)", re.S)
HTML_MARKUP_RX = re.compile(r"<style\b.*?</style>|<script\b.*?</script>|<!--.*?-->|<[^>]*>", re.S | re.I)

SKIP_REL = {Path("docs/schedule.yml"), Path("docs/assignments/exercises.md")}
SKIP_DIRS = {"site", "utils", ".git"}
L01_PREFIX = "docs/lectures/01-cs326-2026-08-25-"


# --------------------------------------------------------------------------
# Transform
# --------------------------------------------------------------------------
class Result:
    def __init__(self):
        self.words = Counter()  # (british, american) lowercase -> count
        self.items = []         # (category, line, message)

    @property
    def total(self):
        return sum(self.words.values())


def match_case(src, repl):
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def slug(heading):
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", heading).strip()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def _ctx(line, width=110):
    line = line.strip()
    return line if len(line) <= width else line[:width] + "…"


def _protected_spans(line):
    spans = [(m.start(), m.end()) for m in CODE_SPAN_RX.finditer(line)]
    spans += [(m.start(), m.end()) for m in URL_RX.finditer(line)]
    spans += [(m.start(), m.end()) for m in PATH_RX.finditer(line)]
    return spans


def substitute(text, protected, lineno, res, line_for_ctx=None):
    """Rewrite British words in `text` outside `protected` [start, end) spans."""
    pieces, last = [], 0
    ctx_src = line_for_ctx if line_for_ctx is not None else text
    for m in WORD_RX.finditer(text):
        word = m.group("word")
        low = word.lower()
        if low in EXCLUDE:
            continue
        if any(s <= m.start() < e for s, e in protected):
            res.items.append(("CODE", lineno, f"{m.group(0)!r} inside code/URL/path — not changed :: {_ctx(ctx_src)}"))
            continue
        new = m.group("prefix") + match_case(word, WORDS[low])
        res.words[(m.group(0).lower(), new.lower())] += 1
        pieces.append(text[last:m.start()])
        pieces.append(new)
        last = m.end()
    pieces.append(text[last:])
    return "".join(pieces)


def process_markdown(block, first_line, res):
    """Markdown rules, line by line. `first_line` is the 1-based line of block[0]."""
    out = []
    fence = None  # (marker char, length, lang)
    in_html_comment = False
    lineno = first_line - 1
    for line in block.splitlines(keepends=True):
        lineno += 1
        body = line.rstrip("\r\n")
        eol = line[len(body):]
        fm = FENCE_RX.match(body)
        if fence is None and fm:
            fence = (fm.group("fence")[0], len(fm.group("fence")), fm.group("lang").lower())
            out.append(line)
            continue
        if fence and fm and fm.group("fence")[0] == fence[0] and len(fm.group("fence")) >= fence[1] and not fm.group("lang"):
            fence, in_html_comment = None, False
            out.append(line)
            continue
        protected = []
        if fence and fence[2] != "mermaid":
            if in_html_comment or body.lstrip().startswith("<!--"):
                if "<!--" in body and "-->" not in body:
                    in_html_comment = True
                elif "-->" in body:
                    in_html_comment = False
            elif COMMENT_LINE_RX.match(body):
                pass  # a comment line: prose
            else:
                tm = TRAILING_COMMENT_RX.search(body)
                protected.append((0, tm.start() if tm else len(body)))
        protected += _protected_spans(body)
        new_body = substitute(body, protected, lineno, res)
        if fence is None and new_body != body and HEADING_RX.match(body):
            res.items.append(("HEADING", lineno,
                              f"anchor changes: #{slug(body)} -> #{slug(new_body)} :: {_ctx(body)} -> {_ctx(new_body)}"))
        out.append(new_body + eol)
    return "".join(out)


def process_html_text(block, first_line, res):
    """Visible text only: markup, <style>, <script> and comments are protected."""
    protected = [(m.start(), m.end()) for m in HTML_MARKUP_RX.finditer(block)]
    out, pos = [], 0
    lineno = first_line - 1
    for line in block.splitlines(keepends=True):
        lineno += 1
        start, end = pos, pos + len(line)
        local = [(max(s, start) - start, min(e, end) - start) for s, e in protected if s < end and e > start]
        local += _protected_spans(line)
        out.append(substitute(line, local, lineno, res))
        pos = end
    return "".join(out)


def transform(text, is_html=False, res=None):
    res = res if res is not None else Result()
    if not is_html:
        return process_markdown(text, 1, res)
    m = TEXTAREA_RX.search(text)
    if not m:
        return process_html_text(text, 1, res)
    head, body, tail = text[:m.start(2)], m.group(2), text[m.end(2):]
    body_line = head.count("\n") + 1
    tail_line = body_line + body.count("\n")
    return (process_html_text(head, 1, res)
            + process_markdown(body, body_line, res)
            + process_html_text(tail, tail_line, res))


def checks(text, res):
    """Hits a human must judge: 'analyses' (never changed) and 'practice' (noun)."""
    practice_sets = 0
    for i, line in enumerate(text.splitlines(), 1):
        for _ in ANALYSES_RX.finditer(line):
            res.items.append(("CHECK analyses", i, f"left as is (plural noun or British verb?) :: {_ctx(line)}"))
        for m in PRACTICE_RX.finditer(line):
            if PRACTICE_NOUN_RX.match(line, m.start()):
                practice_sets += 1
            else:
                res.items.append(("CHECK practice", i, f"noun/adjective? (British verb forms are rewritten) :: {_ctx(line)}"))
    return practice_sets


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------
def self_test():
    def t(s, html=False):
        return transform(s, html, Result())

    pairs = {
        "behaviour": "behavior", "Behaviours": "Behaviors", "BEHAVIOUR": "BEHAVIOR",
        "behaviourally": "behaviorally", "uninitialised": "uninitialized",
        "Reorganise": "Reorganize", "virtualisation": "virtualization",
        "optimiser": "optimizer", "recognisable": "recognizable",
        "programme": "program", "analyse": "analyze", "analysing": "analyzing",
        "practise": "practice", "practised": "practiced", "labelled": "labeled",
        "mislabelled": "mislabeled", "catalogue": "catalog", "honouring": "honoring",
        "dishonour": "dishonor", "signalling": "signaling", "modelled": "modeled",
        "judgement": "judgment", "neighbouring": "neighboring", "centre": "center",
        "recentre": "recenter", "colour": "color", "grey": "gray", "licence": "license",
        "defences": "defenses", "fulfil": "fulfill", "enrol": "enroll",
        "travelling": "traveling", "cancelled": "canceled", "totalling": "totaling",
        "whilst": "while", "amongst": "among", "learnt": "learned", "spelt": "spelled",
        "unsynchronised": "unsynchronized", "deserialise": "deserialize",
    }
    for b, a in pairs.items():
        assert t(f"x {b} y") == f"x {a} y", (b, t(f"x {b} y"))
        assert t(f"({b}).") == f"({a}).", b
    for same in ("optimistic", "realism", "realist", "programmer", "programmed", "fulfilled",
                 "enrolled", "concentrate", "analyses", "practice", "Practice", "afterwards",
                 "towards", "cancellation", "greyhound_x", "my_behaviour", "colour2"):
        assert t(f"x {same} y") == f"x {same} y", (same, t(f"x {same} y"))
    # Markdown protection.
    assert t("the `behaviour` field") == "the `behaviour` field"
    assert t("see https://x.org/colour and www.y.org/centre now") == "see https://x.org/colour and www.y.org/centre now"
    assert t("see docs/behaviour.md and colour.rs:12-14 and entry.S") == "see docs/behaviour.md and colour.rs:12-14 and entry.S"
    assert t("[behaviour](behaviour.md#the-colour)") == "[behavior](behaviour.md#the-color)"
    fence = "```rust\nlet colour = 1; // initialise it\n// the behaviour\n#[derive(Colour)]\n```\ncolour\n"
    assert t(fence) == "```rust\nlet colour = 1; // initialize it\n// the behavior\n#[derive(Color)]\n```\ncolor\n", t(fence)
    r = Result()
    transform(fence, False, r)
    assert any(c == "CODE" for c, _, _ in r.items)
    mermaid = "```mermaid\nA[Virtualise memory] --> B\n```\n"
    assert t(mermaid) == "```mermaid\nA[Virtualize memory] --> B\n```\n"
    admon = "!!! note\n    ```text\n    behaviour\n    <!-- behaviour\n    more -->\n    ```\n    behaviour\n"
    assert t(admon) == "!!! note\n    ```text\n    behaviour\n    <!-- behavior\n    more -->\n    ```\n    behavior\n", t(admon)
    r = Result()
    assert transform("## The Failure Catalogue\n", False, r) == "## The Failure Catalog\n"
    assert any(c == "HEADING" and "#the-failure-catalogue -> #the-failure-catalog" in m for c, _, m in r.items)
    # HTML slides.
    html = ('<title>Colour - CS 326</title><style>.colour{color:grey}</style>\n'
            '<div class="colour">the behaviour</div><!-- colour -->\n'
            '<textarea data-template>\n## Behaviour\n`colour` and colour\n```rust\nlet grey = 0; // grey\n```\n</textarea>\n'
            '<script>var colour = "grey";</script>\n')
    want = ('<title>Color - CS 326</title><style>.colour{color:grey}</style>\n'
            '<div class="colour">the behavior</div><!-- colour -->\n'
            '<textarea data-template>\n## Behavior\n`colour` and color\n```rust\nlet grey = 0; // gray\n```\n</textarea>\n'
            '<script>var colour = "grey";</script>\n')
    assert t(html, True) == want, t(html, True)
    assert t("<p>behaviour</p>", True) == "<p>behavior</p>"
    # Idempotent.
    once = t(html, True)
    r2 = Result()
    assert transform(once, True, r2) == once and r2.total == 0
    once = t(fence + admon + mermaid)
    assert t(once) == once


# --------------------------------------------------------------------------
# File walk
# --------------------------------------------------------------------------
def skip_reason(path, include_l01):
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return None
    if rel.parts and rel.parts[0] in SKIP_DIRS:
        return f"{rel.parts[0]}/ is never touched"
    if rel in SKIP_REL:
        return "generated file"
    if str(rel).startswith(L01_PREFIX) and not include_l01:
        return "L01 is rewritten by hand (--include-l01 to override)"
    return None


def rel(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def targets(args):
    if args.paths:
        files = [Path(p).resolve() for p in args.paths]
    else:
        files = sorted(p for p in DOCS.rglob("*") if p.suffix in (".md", ".html", ".yml"))
        files.append(ROOT / "CONTRIBUTING.md")
    for f in files:
        if not f.is_file():
            print(f"  ! not a file: {f}", file=sys.stderr)
            continue
        why = skip_reason(f, args.include_l01)
        if why:
            print(f"  - skip {rel(f)} ({why})")
            continue
        yield f


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="report only (default)")
    mode.add_argument("--apply", action="store_true", help="write files in place")
    ap.add_argument("--paths", nargs="+", metavar="FILE", help="restrict to these files")
    ap.add_argument("--include-l01", action="store_true", help="also process the two L01 files")
    ap.add_argument("--self-test", action="store_true", help="run the assertions and exit")
    args = ap.parse_args()

    self_test()
    if args.self_test:
        print("self-test passed")
        return 0

    apply = args.apply
    print(f"americanize.py — {'APPLY' if apply else 'DRY RUN (no files written)'}")
    results, changed, scanned, practice_sets = {}, 0, 0, 0
    for f in targets(args):
        scanned += 1
        text = f.read_bytes().decode("utf-8")
        res = Result()
        new = transform(text, f.suffix == ".html", res)
        practice_sets += checks(text, res)
        results[f] = res
        if new != text:
            changed += 1
            if apply:
                f.write_bytes(new.encode("utf-8"))

    words = Counter()
    for res in results.values():
        words.update(res.words)
    total = sum(words.values())
    print(f"\nscanned {scanned} files; {changed} with changes; {total} replacements")

    per_file = {f: r for f, r in results.items() if r.total}
    if per_file:
        print("\nper-file:")
        for f, res in sorted(per_file.items(), key=lambda kv: (-kv[1].total, rel(kv[0]))):
            top = ", ".join(f"{b}×{n}" if n > 1 else b for (b, _), n in res.words.most_common(4))
            print(f"  {res.total:4d}  {rel(f)}  ({top})")

    if words:
        print("\nper-word (british -> american: count):")
        for (b, a), n in sorted(words.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {n:4d}  {b} -> {a}")

    items = [(cat, rel(f), line, msg) for f, res in results.items() for cat, line, msg in res.items]
    by_cat = defaultdict(list)
    for cat, path, line, msg in items:
        by_cat[cat].append((path, line, msg))
    print(f"\nREPORT — {len(items)} items to look at by hand"
          f" (\"Practice Set\"/\"Practice Problems\" occurrences not listed: {practice_sets})")
    for cat in ("HEADING", "CODE", "CHECK analyses", "CHECK practice"):
        rows = by_cat.get(cat)
        if not rows:
            continue
        print(f"\n[{cat}] {len(rows)}")
        for path, line, msg in sorted(rows):
            print(f"  {path}:{line}: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
