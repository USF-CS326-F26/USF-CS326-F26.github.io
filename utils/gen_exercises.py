#!/usr/bin/env python3
"""Generate docs/assignments/exercises.md from OSlings' info.toml.

The master exercise table is the most-used page on the site and it must not
drift from the registry the tool actually reads, nor from the schedule. So it
is generated from both: exercise names, modes, and extra-credit flags come from
`info.toml`; the session each exercise is released in comes from
`gen_schedule.sessions()`.

The registry path defaults to the instructor repo next to this one; override
with `OSLINGS_INFO=/path/to/info.toml`. Old (pre-rename) exercise names are
translated through RENAME so the page is correct before and after the OSlings
repo moves to the `NN<letter>_name` scheme.

Run from the site repo root:  python3 utils/gen_exercises.py
"""
import os
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_schedule import sessions, session_label  # noqa: E402

INFO = Path(os.environ.get(
    "OSLINGS_INFO", "/Users/benson/sync/cs326/dev/git/cs326-oslings/info.toml"))
OUT = Path(__file__).resolve().parent.parent / "docs/assignments/exercises.md"

# Old info.toml name -> new name. Identity for names already renamed.
RENAME = {
    'r00_hello_rust': '00r_hello_rust', 'r01_control_flow': '01r_control_flow',
    'r02_ownership': '02r_ownership', 'r03_borrowing': '03r_borrowing',
    'r04_structs_impl': '04r_structs_impl', 'r05_enums_match': '05r_enums_match',
    'r06_collections': '06r_collections', 'r07_traits': '07r_traits',
    'r08_errors': '08r_errors',
    'c00_echo': '10c_echo', 'c01_cat': '11c_cat', 'c02_wc': '12c_wc',
    'c04_grep': '13c_grep', 'c03_head': '14c_head',
    'a00_asm_bridge': '20a_asm_bridge', 'r09_unsafe_bridge': '21r_unsafe_bridge',
    '00_rust_kernel_basics': '30k_kernel_basics', '01_boot': '31k_boot',
    '02_physical_memory': '32k_physical_memory', '03_paging': '33k_paging',
    '04_processes': '34k_processes', '05_context_switch': '35k_context_switch',
    '06_scheduling': '36k_scheduling', '07_spinlocks': '37k_spinlocks',
    '08_semaphores': '38k_semaphores', '09_virtual_memory': '39k_virtual_memory',
    '10_filesystem': '40k_filesystem', '11_devices': '41k_devices',
    '12_boot_to_life': '42k_boot_to_life', '13_traps': '43k_traps',
    '14_interrupts': '44k_interrupts', '15_console': '45k_console',
    '16_shell': '46k_shell', '17_file_commands': '47k_file_commands',
    '18_user_mode': '48k_user_mode', '19_exec': '49k_exec',
    '20_file_descriptors': '50k_file_descriptors', '21_fork_wait': '51k_fork_wait',
    '22_userland': '52k_userland', '25_ship_your_commands': '53k_ship_your_commands',
    '23_elf_loader': '54k_elf_loader', '24_pipes': '55k_pipes',
}
EXTRA_CREDIT = {'14c_head', '41k_devices', '47k_file_commands', '54k_elf_loader'}

WHAT = {
 '00r_hello_rust': 'Bindings, integer types, hex literals, and the numbers a kernel is written in',
 '01r_control_flow': 'Functions, `if`/`loop`/`while`, and integer overflow',
 '02r_ownership': 'Ownership and moves — why a kernel needs no garbage collector',
 '03r_borrowing': '`&` and `&mut`, the aliasing rule, and lifetimes by example',
 '04r_structs_impl': 'Structs, methods, `const fn`, and the newtype pattern',
 '05r_enums_match': 'Enums, `Option`, and exhaustive `match`',
 '06r_collections': 'Arrays, slices, `Vec`, and fixed kernel tables',
 '07r_traits': 'Traits, generics, and the abstractions the scheduler needs',
 '08r_errors': '`Option`, `Result`, and `?` — errors without exceptions',
 '10c_echo': 'Your first command: argv, writing bytes, separators vs terminators',
 '11c_cat': 'Streaming a file through a fixed buffer; the short-read contract',
 '12c_wc': 'Counting with O(1) state — a word-boundary state machine',
 '13c_grep': 'Substring search and its edge cases',
 '14c_head': 'Parsing an argument, and stopping early',
 '20a_asm_bridge': 'RISC-V assembly called from Rust: `add3`, a byte copy, and a baby context switch',
 '21r_unsafe_bridge': 'Raw pointers, `unsafe`, `volatile` MMIO, and leaving `std`',
 '30k_kernel_basics': '`no_std`, `no_main`, the panic handler, and `_entry`',
 '31k_boot': 'The entry trampoline, the linker script, and printing over the UART',
 '32k_physical_memory': 'A page allocator built on an intrusive free list',
 '33k_paging': 'Sv39 page tables: the `Pte` newtype, `walk`, and `mappages`',
 '34k_processes': 'The process control block, the state enum, and the process table',
 '35k_context_switch': '`swtch` — saving and restoring registers in assembly',
 '36k_scheduling': 'A round-robin scheduler driven by real context switches',
 '37k_spinlocks': 'A `SpinLock` on atomics, with `Send`/`Sync` and an RAII guard',
 '38k_semaphores': 'A counting semaphore — and the kernel heap comes online',
 '39k_virtual_memory': 'Build the kernel page table and turn the MMU on',
 '40k_filesystem': 'An in-memory filesystem of inodes and directories',
 '41k_devices': 'A real polled UART driver, tested by loopback',
 '42k_boot_to_life': 'Assemble the boot sequence — `cargo run` boots rv6 for real',
 '43k_traps': 'The M→S transition and supervisor trap handling',
 '44k_interrupts': 'Timer interrupts via the CLINT, delegated to supervisor mode',
 '45k_console': 'Interrupt-driven UART input routed through the PLIC',
 '46k_shell': 'A kernel-mode REPL: `pwd`, `ls`, `cd`, `mkdir`',
 '47k_file_commands': '`touch`, `cat`, `echo >`, `rm`, `rmdir`',
 '48k_user_mode': 'The trampoline, the trapframe, `ecall`, and the first `sret`',
 '49k_exec': 'Load a named program of any size, with `argv`',
 '50k_file_descriptors': 'A per-process fd table over the filesystem',
 '51k_fork_wait': '`fork`, `exit`, `wait`, and a real multi-process scheduler',
 '52k_userland': '`exec` as a system call — a shell running in user mode',
 '53k_ship_your_commands': 'Run the commands you wrote in Module 1 on your own kernel',
 '54k_elf_loader': 'Read a real ELF executable — entry point, per-segment permissions, and `.bss`',
 '55k_pipes': 'Design a pipe: a bounded buffer between two processes (design only)',
}
MODE = {'test': '`cargo test`', 'build': 'compiles', 'qemu': 'boots in QEMU'}

GROUPS = {
 'm1': ('Module 1 — Rust, Commands, and Bridges to Bare Metal',
        'Exercises `00r`–`21r`. Everything here runs on your own laptop with '
        '`cargo test`, and every exercise is self-contained — none depends on code '
        'from an earlier one. The two bridges at the end are the exception in kind: '
        '`20a_asm_bridge` runs bare metal and is the deadline for a working QEMU '
        '(Thu Oct 1), and `21r_unsafe_bridge` is the last stop before the kernel.'),
 'm2': ('Module 2 — Build the Kernel',
        'Exercises `30k`–`53k`. From an empty crate to a kernel that boots, pages, '
        'schedules, takes interrupts, runs a shell, and finally runs your own Module 1 '
        'commands in user mode. Kernel exercises are cumulative: each starts from the '
        'reference version of everything before it, so read the given code before you '
        'write the marker. Later exercises give more code and ask for one focused piece.'),
 'ec': ('Extra credit',
        'Optional, released alongside the session listed, and not worked in class. '
        'Nothing later depends on this code. Each is worth a small amount; extra '
        'credit is capped at +3% of the course grade. See '
        '[Extra Credit](extra-credit.md).'),
}

HEADER = """# All Exercises

Every exercise in the course, in order. Each is released at the start of the
session listed and you run `oslings submit` before you leave the room, passed
or not. An exercise not passed in class can be finished on your own for 75%:
an unfinished one is completed at a make-up session — office hours, on the
class network — before the next session. Two hints ship
with each exercise; the reference solution ships with the next release
(`oslings solution <name>`).

Run one with `oslings run <name>`, or just `oslings` for the full-screen app.
"""


def group_of(name, entry, old_file):
    """'m1' | 'm2' | 'ec'. Extra credit comes from the `extra_credit` flag (new
    registry), the known EC set, or — old registry only — `part = 3`, except
    that 53k_ship_your_commands was part 3 there and is core now."""
    if entry.get('extra_credit') or name in EXTRA_CREDIT:
        return 'ec'
    if old_file and entry.get('part') == 3 and name != '53k_ship_your_commands':
        return 'ec'
    return 'm2' if name[2] == 'k' else 'm1'


def order_key(row):
    """Sort table rows by exercise number, then track letter."""
    n = row.split('**')[1]
    return (int(n[:2]), n)


def main():
    info = tomllib.load(open(INFO, "rb"))
    old_file = any(e['name'] in RENAME for e in info['exercises'])

    # Session label per exercise, from the schedule.
    session = {}
    for s in sessions():
        for n in s['exercises'] + s['extra']:
            session[n] = session_label(s)

    rows = {'m1': [], 'm2': [], 'ec': []}
    unknown = []
    for e in info['exercises']:
        n = RENAME.get(e['name'], e['name'])
        if n not in WHAT:
            unknown.append(n)
        g = group_of(n, e, old_file)
        rows[g].append(
            f"| `{n.split('_')[0]}` | **{n}** | {WHAT.get(n, '')} | "
            f"{session.get(n, 'TBA')} | {MODE[e['mode']]} |")

    out = [HEADER]
    for g in ('m1', 'm2', 'ec'):
        if not rows[g]:
            continue
        title, blurb = GROUPS[g]
        out += [f"\n## {title}\n\n{blurb}\n",
                "| # | Exercise | What you build | Session | Passes when |",
                "|---|---|---|---|---|"]
        out += sorted(rows[g], key=order_key)

    out.append("""

Every layer under this line is yours:

```text
rv6$ run mygrep cat notes.txt
the cat sat
```
""")

    OUT.write_text("\n".join(out))
    n = len(info['exercises'])
    print(f"exercises.md: {n} exercises — Module 1 {len(rows['m1'])}, "
          f"Module 2 {len(rows['m2'])}, extra credit {len(rows['ec'])}"
          f"{' (names translated from the old scheme)' if old_file else ''}")
    unscheduled = [r.split('**')[1] for g in rows.values() for r in g if '| TBA |' in r]
    if unscheduled:
        print(f"  ! not on the schedule: {', '.join(unscheduled)}")
    if unknown:
        print(f"  ! no WHAT blurb for: {', '.join(unknown)}")
    scheduled = set(session)
    registered = {RENAME.get(e['name'], e['name']) for e in info['exercises']}
    for n in sorted(scheduled - registered):
        print(f"  ! scheduled but not in info.toml: {n}")


if __name__ == "__main__":
    main()
