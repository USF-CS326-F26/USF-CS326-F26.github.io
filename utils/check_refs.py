#!/usr/bin/env python3
"""Check that every code citation in the docs names a file and item that exist.

Course material cites rv6 by **file and item** — `kinit()` (`main.rs`), or
`walk()` in `vm.rs` — never by line number. Line numbers were dropped because no
student can resolve them: Module 1 hands out no kernel source at all, and from
`30k` on the kernel is built cumulatively from skeletons, so the student's
`vm.rs` is a fraction of the finished file and numbered differently. A function
name, unlike a line, is the same in the skeleton, in the student's tree, and in
the reference kernel.

That only holds while the names are real, which is what this checks:

`docs/inclass/` is skipped: it documents the separate `inclass` repo, whose
Rust files are not rv6 files.

  1. no citation carries a line number — those rot on the next edit, and the
     student's cumulative tree is numbered differently from the finished one
  2. every `file.rs` named in the docs exists somewhere in the OSlings tree
  3. every `` `item()` (`file.rs`) `` citation names a real item — in that file,
     in the module a `mod::item()` path names, or, since a citation may name
     where a function is *called* rather than defined, somewhere in the tree

Bare-name citations are not checked: "`mret` in `start.rs`" and "`allocproc` in
`syscall.rs`" are both true prose about a file without being definitions.

Point OSLINGS_ROOT at the OSlings checkout if it is not in the default place;
without one the check reports that it skipped and exits 0.

Run:  python3 utils/check_refs.py
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OSLINGS = Path(os.environ.get(
    "OSLINGS_ROOT", "/Users/benson/sync/cs326/dev/git/cs326-oslings"))

if not OSLINGS.is_dir():
    # The OSlings kernel lives in a separate repo, so this check is a no-op
    # anywhere that repo is not checked out (CI included). It is a notice, not
    # a failure, so the step can sit in the pipeline and start working the day
    # the sources are there.
    print(f"no OSlings checkout at {OSLINGS} — skipping (set OSLINGS_ROOT)")
    sys.exit(0)

SRC_DIRS = ["rv6/src", "ulib/src", "ulib/src/sys", "oslings-cli/src",
            "commands/src/bin", "asmlab/src"]
EX = OSLINGS / "exercises"
if EX.is_dir():
    SRC_DIRS += [f"exercises/{e.name}/{sub}" for e in sorted(EX.iterdir())
                 for sub in ("solution", "skeleton")
                 if (e / sub).is_dir()]

ITEM = re.compile(r"""^[ \t]*
    (?:pub(?:\s*\([^)]*\))?\s+)?
    (?:default\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+"[^"]*"\s+)?
    (?:const\s+(?=fn\b))?(?:async\s+)?(?:unsafe\s+)?
    (?P<kind>fn|struct|enum|union|trait|impl|const|static|type|mod|macro_rules!)
    (?:\s*<[^;{]*?>)?\s+(?:mut\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)""", re.X)
IMPL_TY = re.compile(r"^[ \t]*(?:unsafe\s+)?impl(?:\s*<[^>]*>)?\s+"
                     r"(?:[^{]+?\s+for\s+)?(?P<ty>[A-Za-z_][A-Za-z0-9_]*)")
ASM_LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$")


def items_in(path):
    """Every item name a citation may legitimately use for this file."""
    names, impl_ty = set(), None
    for line in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        m = ITEM.match(line)
        if m:
            kind, name = m.group("kind"), m.group("name")
            if kind == "impl":
                mi = IMPL_TY.match(line)
                impl_ty = mi.group("ty") if mi else name
                names.add(impl_ty)
            else:
                names.add(name)
                if impl_ty and not line[:1].strip():
                    names.add(f"{impl_ty}::{name}")
        ma = ASM_LABEL.match(line)
        if ma:
            names.add(ma.group(1))
    return names


by_base = {}
for d in SRC_DIRS:
    p = OSLINGS / d
    if not p.is_dir():
        continue
    for f in sorted(p.iterdir()):
        if f.suffix == ".rs":
            by_base.setdefault(f.name, []).append(f)

# a citation is satisfied by ANY file of that name in the tree
known = {base: set().union(*(items_in(f) for f in paths))
         for base, paths in by_base.items()}
# `uart::init()` cited inside `main.rs` is a call, not a definition: check it
# against `uart.rs`, the module that owns it. Same for the core/alloc paths.
STD_ROOTS = {"core", "std", "alloc", "ptr", "mem", "cmp", "slice", "str"}
# every item name in the tree: a citation may name where a function is *called*
# rather than where it is defined ("`kvmmake()` (`main.rs`)"), which is true
# prose. What must never happen is citing a name that exists nowhere at all.
anywhere = set().union(*known.values()) if known else set()

# `item()` (`file.rs`)  |  `item` in `file.rs`  — `call` is set when the
# citation used the call form, which is unambiguously a code citation
CITED = re.compile(r"`(?P<item>[A-Za-z_][A-Za-z0-9_:]*)(?P<call>\(\))?`"
                   r"\s*(?:\(`|in `)(?:[A-Za-z0-9_./-]*/)?(?P<file>[a-z_][a-z_0-9]*\.rs)`")
# any `file.rs` mentioned at all
NAMED = re.compile(r"`(?:[A-Za-z0-9_./-]*/)?(?P<file>[a-z_][a-z_0-9]*\.rs)`")
# rustc diagnostics quote real paths and lines; they are transcripts, not citations
SKIP_LINE = re.compile(r"^\s*(-->|\d+\s*\|)")
# docs/inclass/ documents the separate `inclass` repo — its Rust files are not
# rv6 files and are not expected in the OSlings tree
SKIP_DIRS = {"inclass"}

# a citation that grew a line number back
NUMBERED = re.compile(r"`?(?:[A-Za-z0-9_./-]*/)?[a-z_][a-z_0-9]*\.(?:rs|ld|toml):\d+")

unknown_file, unknown_item, numbered, checked = [], [], [], 0
for path in sorted(DOCS.rglob("*")):
    if path.suffix not in (".md", ".html") or not path.is_file():
        continue
    rel = path.relative_to(DOCS)
    if rel.parts and rel.parts[0] in SKIP_DIRS:
        continue
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if SKIP_LINE.match(line):
            continue
        for m in NUMBERED.finditer(line):
            numbered.append((rel, n, m.group(0)))
        for m in NAMED.finditer(line):
            base = m.group("file")
            if base not in known:
                unknown_file.append((rel, n, base))
        for m in CITED.finditer(line):
            base, item = m.group("file"), m.group("item")
            if base not in known:
                continue                      # already reported above
            tail = item.split("::")[-1]
            if item in known[base] or tail in known[base]:
                checked += 1
                continue
            if "::" in item:
                root = item.split("::")[0]
                if root in STD_ROOTS:
                    continue                  # a core/alloc path, not rv6's
                owner = f"{root}.rs"          # a call into another module
                if owner in known:
                    checked += 1
                    if tail not in known[owner]:
                        unknown_item.append((rel, n, item, owner))
                    continue
            # Only the call form has to resolve. Bare names are how the prose
            # says a thing is *used* in a file — "`allocproc` in `syscall.rs`",
            # "`mret` in `start.rs`" — which is true without being a definition.
            if m.group("call"):
                checked += 1
                if tail not in anywhere:
                    unknown_item.append((rel, n, item, base))

for rel, n, text in numbered:
    print(f"line number    {rel}:{n}: {text} — cite the item, not the line")
for rel, n, base in unknown_file:
    print(f"unknown file   {rel}:{n}: `{base}` is not in the OSlings tree")
for rel, n, item, base in unknown_item:
    print(f"unknown item   {rel}:{n}: `{item}` is not in `{base}`")

print(f"\ncode citations checked: {checked}")
print(f"source files indexed:   {sum(len(v) for v in by_base.values())}")
if unknown_file or unknown_item or numbered:
    sys.exit(f"FAIL: {len(unknown_file)} unknown file(s), "
             f"{len(unknown_item)} unknown item(s), "
             f"{len(numbered)} line-numbered citation(s)")
print("every cited file and item exists")
