#!/usr/bin/env python3
"""Generate docs/assignments/exercises.md from OSlings' info.toml.

The master exercise table is the most-used page on the site and it must not
drift from the registry the tool actually reads. Generate it.

Run from the site repo root:  python3 utils/gen_exercises.py
"""
import tomllib
from pathlib import Path

INFO = Path("/Users/benson/sync/cs326/dev/git/OSlings/info.toml")
OUT = Path(__file__).resolve().parent.parent / "docs/assignments/exercises.md"

SESSION = {
 'r00_hello_rust':'Fri Aug 28','r01_control_flow':'Fri Aug 28','r02_ownership':'Tue Sep 1',
 'r03_borrowing':'Thu Sep 3','r04_structs_impl':'Fri Sep 4','r05_enums_match':'Fri Sep 4',
 'r06_collections':'Tue Sep 8','r07_traits':'Thu Sep 10','r08_errors':'Thu Sep 10',
 'c00_echo':'Fri Sep 11','c01_cat':'Fri Sep 11','c02_wc':'Tue Sep 15',
 'c03_head':'Tue Sep 15','c04_grep':'Thu Sep 17','a00_asm_bridge':'Fri Sep 18',
 'r09_unsafe_bridge':'Tue Sep 22',
 '00_rust_kernel_basics':'Thu Sep 24','01_boot':'Fri Sep 25','02_physical_memory':'Thu Oct 1',
 '03_paging':'Tue Oct 6','04_processes':'Thu Oct 8','05_context_switch':'Fri Oct 9',
 '06_scheduling':'Thu Oct 15','07_spinlocks':'Thu Oct 22','08_semaphores':'Fri Oct 23',
 '09_virtual_memory':'Tue Oct 27','10_filesystem':'Thu Oct 29','11_devices':'Fri Oct 30',
 '12_boot_to_life':'Fri Oct 30','13_traps':'Thu Nov 5','14_interrupts':'Fri Nov 6',
 '15_console':'Fri Nov 6','16_shell':'Thu Nov 12','17_file_commands':'Fri Nov 13',
 '18_user_mode':'Thu Nov 19 – Fri Nov 20','19_exec':'Thu Dec 3','20_file_descriptors':'Thu Dec 3',
 '21_fork_wait':'Fri Dec 4','22_userland':'Tue Dec 8',
 '23_elf_loader':'Dec 8 / office hours','25_ship_your_commands':'Dec 8 / office hours',
}
WHAT = {
 'r00_hello_rust':'Bindings, integer types, hex literals, and the numbers a kernel is written in',
 'r01_control_flow':'Functions, `if`/`loop`/`while`, and integer overflow',
 'r02_ownership':'Ownership and moves — why a kernel needs no garbage collector',
 'r03_borrowing':'`&` and `&mut`, the aliasing rule, and lifetimes by example',
 'r04_structs_impl':'Structs, methods, `const fn`, and the newtype pattern',
 'r05_enums_match':'Enums, `Option`, and exhaustive `match`',
 'r06_collections':'Arrays, slices, `Vec`, and fixed kernel tables',
 'r07_traits':'Traits, generics, and the abstractions the scheduler needs',
 'r08_errors':'`Option`, `Result`, and `?` — errors without exceptions',
 'c00_echo':'Your first command: argv, writing bytes, separators vs terminators',
 'c01_cat':'Streaming a file through a fixed buffer; the short-read contract',
 'c02_wc':'Counting with O(1) state — a word-boundary state machine',
 'c03_head':'Parsing an argument, and stopping early',
 'c04_grep':'Substring search and its edge cases',
 'a00_asm_bridge':'RISC-V assembly called from Rust: `add3`, a byte copy, and a baby context switch',
 'r09_unsafe_bridge':'Raw pointers, `unsafe`, `volatile` MMIO, and leaving `std`',
 '00_rust_kernel_basics':'`no_std`, `no_main`, the panic handler, and `_entry`',
 '01_boot':'The entry trampoline, the linker script, and printing over the UART',
 '02_physical_memory':'A page allocator built on an intrusive free list',
 '03_paging':'Sv39 page tables: the `Pte` newtype, `walk`, and `mappages`',
 '04_processes':'The process control block, the state enum, and the process table',
 '05_context_switch':'`swtch` — saving and restoring registers in assembly',
 '06_scheduling':'A round-robin scheduler driven by real context switches',
 '07_spinlocks':'A `SpinLock` on atomics, with `Send`/`Sync` and an RAII guard',
 '08_semaphores':'A counting semaphore — and the kernel heap comes online',
 '09_virtual_memory':'Build the kernel page table and turn the MMU on',
 '10_filesystem':'An in-memory filesystem of inodes and directories',
 '11_devices':'A real polled UART driver, tested by loopback',
 '12_boot_to_life':'Assemble the boot sequence — `cargo run` boots rv6 for real',
 '13_traps':'The M→S transition and supervisor trap handling',
 '14_interrupts':'Timer interrupts via the CLINT, delegated to supervisor mode',
 '15_console':'Interrupt-driven UART input routed through the PLIC',
 '16_shell':'A kernel-mode REPL: `pwd`, `ls`, `cd`, `mkdir`',
 '17_file_commands':'`touch`, `cat`, `echo >`, `rm`, `rmdir`',
 '18_user_mode':'The trampoline, the trapframe, `ecall`, and the first `sret`',
 '19_exec':'Load a named program of any size, with `argv`',
 '20_file_descriptors':'A per-process fd table over the filesystem',
 '21_fork_wait':'`fork`, `exit`, `wait`, and a real multi-process scheduler',
 '22_userland':'`exec` as a system call — a shell running in user mode',
 '23_elf_loader':'Read a real ELF executable — entry point, per-segment permissions, and `.bss`',
 '25_ship_your_commands':'Run the commands you wrote in week 3 on your own kernel',
}
MODE = {'test':'`cargo test`','build':'compiles','qemu':'boots in QEMU'}
PARTS = {
 0:('Module 1 — Rust, Commands, and Assembly',
    'Everything here runs on your own laptop with `cargo test`. No QEMU, no kernel, '
    'no nightly Rust — so a bare-metal toolchain that is still being fixed cannot block you. '
    '(`a00_asm_bridge` is the exception: it is bare metal, and it is the deadline for a '
    'working QEMU.)'),
 1:('Module 2 — Build the Kernel',
    'From an empty crate to a kernel that boots, pages, schedules, and handles interrupts. '
    'Each exercise starts from the reference version of everything before it, so a session '
    'that did not go well never blocks the next one.'),
 2:('Module 3 — Extend a Complete Kernel',
    'You receive the finished Module 2 kernel and add the layers that make it a Unix: '
    'a shell, user mode, system calls, program loading, and processes.'),
 3:('Extra Credit',
    'Worked in the final week or in office hours. See [Extra Credit](extra-credit.md) '
    'for what each is worth.'),
}

info = tomllib.load(open(INFO, "rb"))

out = ["""# All Exercises

Every exercise in the course, in order. Each is released at the start of the
session that works it, and each is graded independently — passing exercise 12
does not require having passed exercise 11.

Run one with `oslings run <name>`, or just `oslings` for the full-screen app.

!!! tip "Nothing cascades"
    Every exercise's starting point contains the *reference* completed code
    for all earlier exercises. Missing one costs you that exercise and
    nothing else.
"""]

last = None
for e in info["exercises"]:
    p = e.get("part", 1)
    if p != last:
        last = p
        title, blurb = PARTS[p]
        out += [f"\n## {title}\n\n{blurb}\n",
                "| # | Exercise | What you build | Session | Passes when |",
                "|---|---|---|---|---|"]
    n = e["name"]
    out.append(f"| `{n.split('_')[0]}` | **{n}** | {WHAT.get(n,'')} | "
               f"{SESSION.get(n,'TBA')} | {MODE[e['mode']]} |")

out.append("""

Every layer under this line is yours:

```text
rv6$ run mygrep cat notes.txt
the cat sat
```
""")

OUT.write_text("\n".join(out))
print(f"exercises.md: {len(info['exercises'])} exercises across "
      f"{len({e.get('part',1) for e in info['exercises']})} parts")
