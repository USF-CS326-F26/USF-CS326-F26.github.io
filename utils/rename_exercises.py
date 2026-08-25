#!/usr/bin/env python3
"""Rename OSlings exercise references across the site to the F26 naming scheme.

Old names -- `r00_hello_rust`, `r00`, `c03_head`, `a00`, `03_paging`, `ex03`,
"exercise 03" -- become `NN<letter>_name` / `NN<letter>`: a two-digit absolute
number plus a track letter, so `ls` order is Rust (00r-08r) -> commands
(10c-14c) -> bridges (20a, 21r) -> kernel (30k-55k). See the plan for the map.

Three passes, in order:

  1. LONG   the 41 registered names (plus the design-only `24_pipes`), longest
            first: `r00_hello_rust` -> `00r_hello_rust`, `03_paging` -> `33k_paging`.
  2. SHORT  r00..r08 -> 00r..08r, r09 -> 21r, c00 -> 10c, c01 -> 11c, c02 -> 12c,
            c04 -> 13c, c03 -> 14c, a00 -> 20a, ex00..ex22 -> 30k..52k,
            ex23 -> 54k, ex24 -> 55k, ex25 -> 53k.
  3. PROSE  "exercise 12" -> "exercise 42k" (a bare two-digit number after the
            word is a kernel number, mapped as ex+NN), including lists and
            ranges ("exercises 05 + 06", "exercises 11, 13, and 15",
            "Exercises 18-20", "18 through 20") and wrapped numbers
            ("exercise `07`", "exercise **14**").

Every token match is whole-word: (?<![A-Za-z0-9_]) KEY (?![A-Za-z0-9_]), so
backticks, `/`, `#anchors`, quotes, hyphens and en/em dashes are boundaries,
a literal `\\n` inside a mermaid string counts as one too, and `0xa00`,
`0x8000_0c00`, `index00` never match. Keys that look like hex (`a00`,
`c00`-`c04`) also refuse a preceding `#` (CSS colors). `<style>` and `<script>`
blocks in HTML are never touched.

The new names never match the old patterns, so the script is idempotent; a
self-test asserts this (and the hex safety) on every run.

Scope: docs/**/*.md, docs/**/*.html, docs/**/*.yml and CONTRIBUTING.md.
Skipped: docs/schedule.yml and docs/assignments/exercises.md (generated),
site/, utils/, .git/, and the two L01 files (docs/lectures/01-cs326-2026-08-25-*,
rewritten by hand; pass --include-l01 once that rewrite has landed).

The report lists what the rename cannot decide on its own:

  RANGE      a range whose endpoints stop being monotonic (ex22-ex25: 23 -> 54k,
             25 -> 53k, 24 -> 55k; r09 -> 21r; c03/c04 swap)
  FRAGMENT   mermaid-style `exNN-NN` labels; the rename leaves `34k-06`
  OSLINGS    `oslings run 03` and friends -- left unchanged, suggestion given
  ANCHOR     `#ex22` -> `#52k`: the heading it points at must produce that slug
  BARE_SPAN  `NN` code spans (00-25) with no "exercise" word before them;
             "likely" when the line talks about exercises, "unlikely" for
             bit patterns and constants
  LEFTOVER   "Part 0..3", "Module 3", "Module 2 -> 3", "all 38/39 exercises",
             `exercises/NN_*/` paths
  UNMAPPED   "exercise NN" with NN outside 00-25

Usage (from anywhere; paths resolve against the repo root):

    python3 utils/rename_exercises.py                 # dry run (default)
    python3 utils/rename_exercises.py --apply         # write in place
    python3 utils/rename_exercises.py --paths docs/guides/exam-prep.md
    python3 utils/rename_exercises.py --verbose       # every prose rewrite
    python3 utils/rename_exercises.py --self-test     # assertions only
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# --------------------------------------------------------------------------
# The maps (plan "Decisions confirmed with Greg", item 3).
# --------------------------------------------------------------------------
LONG = {
    # Rust (part 0)
    "r00_hello_rust": "00r_hello_rust",
    "r01_control_flow": "01r_control_flow",
    "r02_ownership": "02r_ownership",
    "r03_borrowing": "03r_borrowing",
    "r04_structs_impl": "04r_structs_impl",
    "r05_enums_match": "05r_enums_match",
    "r06_collections": "06r_collections",
    "r07_traits": "07r_traits",
    "r08_errors": "08r_errors",
    # Commands (part 1)
    "c00_echo": "10c_echo",
    "c01_cat": "11c_cat",
    "c02_wc": "12c_wc",
    "c04_grep": "13c_grep",
    "c03_head": "14c_head",  # extra credit
    # Bridges to bare metal (part 2)
    "a00_asm_bridge": "20a_asm_bridge",
    "r09_unsafe_bridge": "21r_unsafe_bridge",
    # Kernel (part 3)
    "00_rust_kernel_basics": "30k_kernel_basics",
    "01_boot": "31k_boot",
    "02_physical_memory": "32k_physical_memory",
    "03_paging": "33k_paging",
    "04_processes": "34k_processes",
    "05_context_switch": "35k_context_switch",
    "06_scheduling": "36k_scheduling",
    "07_spinlocks": "37k_spinlocks",
    "08_semaphores": "38k_semaphores",
    "09_virtual_memory": "39k_virtual_memory",
    "10_filesystem": "40k_filesystem",
    "11_devices": "41k_devices",  # extra credit
    "12_boot_to_life": "42k_boot_to_life",
    "13_traps": "43k_traps",
    "14_interrupts": "44k_interrupts",
    "15_console": "45k_console",
    "16_shell": "46k_shell",
    "17_file_commands": "47k_file_commands",  # extra credit
    "18_user_mode": "48k_user_mode",
    "19_exec": "49k_exec",
    "20_file_descriptors": "50k_file_descriptors",
    "21_fork_wait": "51k_fork_wait",
    "22_userland": "52k_userland",
    "25_ship_your_commands": "53k_ship_your_commands",
    "23_elf_loader": "54k_elf_loader",  # extra credit
    # Not in info.toml: the design-only pipes extra credit the site refers to.
    "24_pipes": "55k_pipes",
}

SHORT = {f"r0{n}": f"0{n}r" for n in range(9)}
SHORT["r09"] = "21r"
SHORT.update({"c00": "10c", "c01": "11c", "c02": "12c", "c04": "13c", "c03": "14c", "a00": "20a"})
SHORT.update({f"ex{n:02d}": f"{30 + n}k" for n in range(23)})
SHORT.update({"ex23": "54k", "ex24": "55k", "ex25": "53k"})

# Bare kernel numbers in prose: "exercise 03" -> "exercise 33k".
KERNEL = {k[2:]: v for k, v in SHORT.items() if k.startswith("ex")}

# Keys that are valid hex digits: never match after '#'.
HEX_KEYS = {k for k in SHORT if re.fullmatch(r"[0-9a-f]+", k)}

# Range endpoints whose new number breaks the old ordering.
NONMONOTONIC = {"r09", "c03", "c04", "ex23", "ex24", "ex25"}

# --------------------------------------------------------------------------
# Regexes
# --------------------------------------------------------------------------
LB = r"(?:(?<![A-Za-z0-9_])|(?<=\\n))"  # start boundary, or a literal \n
RB = r"(?![A-Za-z0-9_])"


def _alt(keys):
    return "(?:" + "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True)) + ")"


LONG_RX = re.compile(LB + "(?P<key>" + _alt(LONG) + ")" + RB)
SHORT_RX = re.compile(LB + "(?P<key>" + _alt(SHORT) + ")" + RB)

NUM = r"(?:`\d{2}`|\*\*\d{2}\*\*|\d{2})"
SEP = r"\s*(?:,\s*(?:and|or)\b|,|\+|&|–|—|-|\band\b|\bor\b|\bto\b|\bthrough\b)\s*"
PROSE_RX = re.compile(
    r"\b(?P<word>[Ee]xercises?)(?P<gap>[ \t]+|\n[ \t]*)(?P<list>" + NUM + "(?:" + SEP + NUM + ")*)" + RB
)
NUM_RX = re.compile(r"(`|\*\*)?(\d{2})(`|\*\*)?")
PROSE_RANGE_RX = re.compile(r"(\d{2})[`*]*\s*(?:–|—|-|\bto\b|\bthrough\b)\s*[`*]*(\d{2})")
# "exercise 03 ... 20 minutes": a trailing unit means the last number is not an exercise.
UNIT_RX = re.compile(r"\s*(?:minutes?|mins?|seconds?|secs?|hours?|lines?|pages?|points?|pts|bytes?|%|percent|weeks?|days?)\b")

RANGE_RX = re.compile(
    LB + r"(?P<a>r0\d|c0\d|ex\d{2})\s*(?:–|—|-|\s+to\s+|\s+through\s+)\s*(?P<b>(?:r|c|ex)?\d{2})" + RB
)
FRAGMENT_RX = re.compile(LB + r"ex(?P<a>\d{2})-(?P<b>\d{2})" + RB)
OSLINGS_RX = re.compile(r"oslings\s+(?P<verb>run|goto|reset|hint|lesson|solution|watch)\s+(?P<n>\d{2})" + RB)
EXPATH_RX = re.compile(r"exercises/(?P<name>\d{2}_[a-z0-9_]+)/")
BARE_SPAN_RX = re.compile(r"`(?P<n>0\d|1\d|2[0-5])`")
LEFTOVER_RXS = [
    re.compile(r"\bPart [0-3]\b"),
    re.compile(r"\bModule 3\b"),
    re.compile(r"\bModule 2\s*(?:→|->|to)\s*3\b"),
    re.compile(r"\ball 3[89] exercises\b"),
]
HTML_PROTECT_RX = re.compile(r"<style\b.*?</style>|<script\b.*?</script>", re.S | re.I)

SKIP_REL = {Path("docs/schedule.yml"), Path("docs/assignments/exercises.md")}
SKIP_DIRS = {"site", "utils", ".git"}
L01_PREFIX = "docs/lectures/01-cs326-2026-08-25-"


# --------------------------------------------------------------------------
# Transform
# --------------------------------------------------------------------------
class Result:
    def __init__(self):
        self.tokens = Counter()   # (old, new) -> count
        self.passes = Counter()   # "long" | "short" | "prose" -> count
        self.items = []           # (category, line, message)
        self.prose = []           # (line, old, new) for --verbose

    @property
    def total(self):
        return sum(self.passes.values())


def _line_of(text, pos):
    return text.count("\n", 0, pos) + 1


LIKELY_RX = re.compile(r"exercise|oslings|passes|reference|since|archive|staged|kernel|hands|builds", re.I)


def _ctx(text, pos, width=110):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end == -1:
        end = len(text)
    line = text[start:end].strip()
    if len(line) > width:
        off = max(0, pos - start - width // 2)
        line = ("…" if off else "") + line[off:off + width] + "…"
    return line


def _norm_endpoint(a, b):
    """`ex04-06` -> ('ex04', 'ex06'); `r00–r09` -> ('r00', 'r09')."""
    if b[0].isdigit():
        prefix = a[:-2]
        b = prefix + b
    return a, b


def _prescan(text, ln, res):
    """Report items that need the original (pre-rename) text."""
    for m in RANGE_RX.finditer(text):
        a, b = _norm_endpoint(m.group("a"), m.group("b"))
        if FRAGMENT_RX.fullmatch(m.group(0)):
            continue  # reported as FRAGMENT below
        crosses = a.startswith("ex") and b.startswith("ex") and int(b[2:]) >= 23
        if a in NONMONOTONIC or b in NONMONOTONIC or crosses:
            new = f"{SHORT.get(a, a)}…{SHORT.get(b, b)}"
            res.items.append(("RANGE", ln(text, m.start()),
                              f"`{m.group(0)}` becomes `{new}` — endpoints no longer contiguous; "
                              f"rewrite by hand :: {_ctx(text, m.start())}"))
    for m in FRAGMENT_RX.finditer(text):
        a, b = "ex" + m.group("a"), "ex" + m.group("b")
        note = " (also crosses 22–25)" if int(m.group("b")) >= 23 else ""
        res.items.append(("FRAGMENT", ln(text, m.start()),
                          f"`{m.group(0)}` leaves `{SHORT[a]}-{m.group('b')}`; suggest `{SHORT[a]}–{SHORT.get(b, '?')}`{note} "
                          f":: {_ctx(text, m.start())}"))
    for m in OSLINGS_RX.finditer(text):
        n = m.group("n")
        res.items.append(("OSLINGS", ln(text, m.start()),
                          f"`{' '.join(m.group(0).split())}` left unchanged; suggest `oslings {m.group('verb')} {KERNEL.get(n, '?')}` "
                          f":: {_ctx(text, m.start())}"))
    for m in EXPATH_RX.finditer(text):
        name = m.group("name")
        res.items.append(("LEFTOVER", ln(text, m.start()),
                          f"path `{m.group(0)}` -> `exercises/{LONG.get(name, name)}/`; confirm the path and section still exist "
                          f":: {_ctx(text, m.start())}"))


def _postscan(text, ln, res):
    """Report items on the renamed text (line numbers are unchanged: no newlines are added)."""
    for m in BARE_SPAN_RX.finditer(text):
        n = m.group("n")
        ctx = _ctx(text, m.start())
        tag = "likely" if LIKELY_RX.search(ctx) else "unlikely"
        res.items.append(("BARE_SPAN", ln(text, m.start()),
                          f"{tag}: `{n}` with no \"exercise\" before it; if it is kernel exercise {n}, write `{KERNEL[n]}` "
                          f":: {ctx}"))
    for rx in LEFTOVER_RXS:
        for m in rx.finditer(text):
            res.items.append(("LEFTOVER", ln(text, m.start()),
                              f"\"{m.group(0)}\" :: {_ctx(text, m.start())}"))


def _rename_segment(text, base, orig, res):
    base_line = orig.count("\n", 0, base)

    def ln(seg, pos):
        # Replacements never add or remove newlines, so counting within the
        # current segment stays exact after the LONG/SHORT passes.
        return base_line + seg.count("\n", 0, pos) + 1

    _prescan(text, ln, res)

    def long_sub(m):
        key = m.group("key")
        res.tokens[(key, LONG[key])] += 1
        res.passes["long"] += 1
        return LONG[key]

    text = LONG_RX.sub(long_sub, text)

    def short_sub(m):
        key = m.group("key")
        if m.start() > 0 and text[m.start() - 1] == "#":
            if key in HEX_KEYS:
                return key  # `#a00`, `#c04`: a CSS color, not an exercise
            res.items.append(("ANCHOR", ln(text, m.start()),
                              f"`#{key}` -> `#{SHORT[key]}`: the target heading must produce that anchor "
                              f":: {_ctx(text, m.start())}"))
        res.tokens[(key, SHORT[key])] += 1
        res.passes["short"] += 1
        return SHORT[key]

    text = SHORT_RX.sub(short_sub, text)

    def prose_sub(m):
        lst = m.group("list")
        tail = text[m.end():m.end() + 12]
        unit_follows = bool(UNIT_RX.match(tail))
        nums = list(NUM_RX.finditer(lst))
        pieces, last = [], 0
        for i, nm in enumerate(nums):
            n = nm.group(2)
            is_last = i == len(nums) - 1
            if n in KERNEL and not (is_last and unit_follows):
                repl = (nm.group(1) or "") + KERNEL[n] + (nm.group(3) or "")
                res.tokens[(f"{m.group('word')} {n}", f"{m.group('word')} {KERNEL[n]}")] += 1
                res.passes["prose"] += 1
            else:
                repl = nm.group(0)
                if n not in KERNEL:
                    res.items.append(("UNMAPPED", ln(text, m.start()),
                                      f"\"{m.group('word')} {n}\" — no exercise with that number :: {_ctx(text, m.start())}"))
            pieces.append(lst[last:nm.start()])
            pieces.append(repl)
            last = nm.end()
        pieces.append(lst[last:])
        new_list = "".join(pieces)
        for rm in PROSE_RANGE_RX.finditer(lst):
            if int(rm.group(2)) >= 23 or int(rm.group(1)) >= 23:
                res.items.append(("RANGE", ln(text, m.start()),
                                  f"\"{m.group('word')} {rm.group(0)}\" crosses 22–25 (23 -> 54k, 25 -> 53k); rewrite by hand "
                                  f":: {_ctx(text, m.start())}"))
        new = m.group("word") + m.group("gap") + new_list
        if new != m.group(0):
            res.prose.append((ln(text, m.start()), m.group(0), new))
        return new

    text = PROSE_RX.sub(prose_sub, text)
    _postscan(text, ln, res)
    return text


def transform(text, is_html=False, res=None):
    """Return the renamed text; collect counts and report items into `res`."""
    res = res if res is not None else Result()
    if not is_html:
        return _rename_segment(text, 0, text, res)
    out, pos = [], 0
    for m in HTML_PROTECT_RX.finditer(text):
        out.append(_rename_segment(text[pos:m.start()], pos, text, res))
        out.append(m.group(0))
        pos = m.end()
    out.append(_rename_segment(text[pos:], pos, text, res))
    return "".join(out)


# --------------------------------------------------------------------------
# Self-test: old -> new, new names are fixed points, hex safety, prose forms.
# --------------------------------------------------------------------------
def self_test():
    def t(s, html=False):
        return transform(s, html, Result())

    for old, new in LONG.items():
        assert t(f"`{old}`") == f"`{new}`", old
        assert t(f"exercises/{old}/README.md") == f"exercises/{new}/README.md", old
    for old, new in SHORT.items():
        for tpl in ("({})", "`{}`", "x/{}/y", "#{}", '"{}"', "{}–{}", "{}-{}", "{},{}", " {} "):
            if tpl == "#{}" and old in HEX_KEYS:
                continue  # `#a00`, `#c00`..`#c04` are CSS colors: checked below
            s = tpl.format(old, old)
            assert t(s) == tpl.format(new, new), (s, t(s))
    # New names never match old patterns (idempotence).
    for new in list(LONG.values()) + list(SHORT.values()):
        for tpl in ("`{}`", " {} ", "/{}/", "#{}", '"{}"', "exercise {}", "exercises {} + {}", "{}–{}"):
            s = tpl.format(new, new)
            assert t(s) == s, (s, t(s))
    for key in LONG:
        assert key not in LONG.values() and not any(v.endswith(key) for v in LONG.values())
    for key in SHORT:
        for v in list(SHORT.values()) + list(LONG.values()):
            assert not re.search(LB + re.escape(key) + RB, v), (key, v)
    # Hex / identifier safety.
    for s in ("0xa00", "0x8000_0c00", "0x0c04", "0xc01", "#a00", "#c04", "#c00;", "index00", "hex00", "0ex00", "nr00"):
        assert t(s) == s, (s, t(s))
    # A literal \n inside a mermaid string is a boundary.
    assert t(r'"Module 1\nr00-r09, c00-c04, a00\nex00"') == r'"Module 1\n00r-21r, 10c-13c, 20a\n30k"'
    # Prose.
    assert t("exercise 12") == "exercise 42k"
    assert t("Exercise 03.") == "Exercise 33k."
    assert t("exercises 05 + 06") == "exercises 35k + 36k"
    assert t("exercises 11, 13, 14, and 15 arriving") == "exercises 41k, 43k, 44k, and 45k arriving"
    assert t("Exercises 18–20 ran") == "Exercises 48k–50k ran"
    assert t("Exercises 18 through 20 ran") == "Exercises 48k through 50k ran"
    assert t("Exercises 00-02: `0x8000_0000`") == "Exercises 30k-32k: `0x8000_0000`"
    assert t("exercise `07`.") == "exercise `37k`."
    assert t("exercises `00`–`07` to work") == "exercises `30k`–`37k` to work"
    assert t("exercise **14**;") == "exercise **44k**;"
    assert t("exercise 03_paging") == "exercise 33k_paging"
    assert t("exercise\n03 is") == "exercise\n33k is"
    assert t("exercise 100") == "exercise 100"
    assert t("exercise 03 takes 20 minutes") == "exercise 33k takes 20 minutes"
    assert t("exercise 23") == "exercise 54k" and t("exercise 25") == "exercise 53k"
    assert t("extra-credit.md#ex22") == "extra-credit.md#52k"
    assert t("`03`") == "`03`"  # bare span: reported, never rewritten
    assert t("oslings run 03") == "oslings run 03"  # reported, never rewritten
    # HTML: style/script are untouched, the rest is renamed.
    h = "<style>#c00{color:#a00}</style><p>ex03 r00</p><script>var ex03='r00';</script>"
    assert t(h, True) == "<style>#c00{color:#a00}</style><p>33k 00r</p><script>var ex03='r00';</script>"
    # Second application is a no-op on a mixed corpus.
    corpus = " ".join(f"`{k}` {v}" for k, v in list(LONG.items()) + list(SHORT.items()))
    corpus += " exercise 03, exercises 05 + 06, Exercises 18–20, exercise `07`, 0xa00, #c04"
    once = t(corpus)
    r2 = Result()
    assert transform(once, False, r2) == once and r2.total == 0, "not idempotent"


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


def rel(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="report only (default)")
    mode.add_argument("--apply", action="store_true", help="write files in place")
    ap.add_argument("--paths", nargs="+", metavar="FILE", help="restrict to these files")
    ap.add_argument("--include-l01", action="store_true", help="also process the two L01 files")
    ap.add_argument("--verbose", action="store_true", help="print every prose rewrite")
    ap.add_argument("--self-test", action="store_true", help="run the assertions and exit")
    args = ap.parse_args()

    self_test()
    if args.self_test:
        print("self-test passed")
        return 0

    apply = args.apply
    print(f"rename_exercises.py — {'APPLY' if apply else 'DRY RUN (no files written)'}")
    per_file, results, changed, scanned = {}, {}, 0, 0
    for f in targets(args):
        scanned += 1
        raw = f.read_bytes()
        text = raw.decode("utf-8")
        res = Result()
        new = transform(text, f.suffix == ".html", res)
        results[f] = res
        if new != text:
            changed += 1
            per_file[f] = res
            if apply:
                f.write_bytes(new.encode("utf-8"))

    tokens, passes = Counter(), Counter()
    for res in results.values():
        tokens.update(res.tokens)
        passes.update(res.passes)
    total = sum(passes.values())
    print(f"\nscanned {scanned} files; {changed} with changes; {total} replacements "
          f"(long {passes['long']}, short {passes['short']}, prose {passes['prose']})")

    if per_file:
        print("\nper-file:")
        for f, res in sorted(per_file.items(), key=lambda kv: -kv[1].total):
            p = res.passes
            print(f"  {res.total:5d}  {rel(f)}  (long {p['long']}, short {p['short']}, prose {p['prose']})")

    if tokens:
        print("\nper-token (old -> new: count):")
        for (old, new), n in sorted(tokens.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            print(f"  {n:4d}  {old} -> {new}")

    if args.verbose:
        print("\nprose rewrites:")
        for f, res in sorted(results.items()):
            for line, old, new in res.prose:
                print(f"  {rel(f)}:{line}: {old!r} -> {new!r}")

    items = [(cat, rel(f), line, msg) for f, res in results.items() for cat, line, msg in res.items]
    by_cat = defaultdict(list)
    for cat, path, line, msg in items:
        by_cat[cat].append((path, line, msg))
    print(f"\nREPORT — {len(items)} items need manual review")
    for cat in ("RANGE", "FRAGMENT", "OSLINGS", "UNMAPPED", "ANCHOR", "BARE_SPAN", "LEFTOVER"):
        rows = by_cat.get(cat)
        if not rows:
            continue
        print(f"\n[{cat}] {len(rows)}")
        for path, line, msg in sorted(rows, key=lambda r: (not r[2].startswith("likely"), r[0], r[1])):
            print(f"  {path}:{line}: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
