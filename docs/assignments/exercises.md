# All Exercises

Every exercise in the course, in order. Each is released at the start of the
session that works it, and each is graded independently — passing exercise 12
does not require having passed exercise 11.

Run one with `oslings run <name>`, or just `oslings` for the full-screen app.

!!! tip "Nothing cascades"
    Every exercise's starting point contains the *reference* completed code
    for all earlier exercises. Missing one costs you that exercise and
    nothing else.


## Module 1 — Rust, Commands, and Assembly

Everything here runs on your own laptop with `cargo test`. No QEMU, no kernel, no nightly Rust — so a bare-metal toolchain that is still being fixed cannot block you. (`a00_asm_bridge` is the exception: it is bare metal, and it is the deadline for a working QEMU.)

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `r00` | **r00_hello_rust** | Bindings, integer types, hex literals, and the numbers a kernel is written in | Fri Aug 28 | `cargo test` |
| `r01` | **r01_control_flow** | Functions, `if`/`loop`/`while`, and integer overflow | Fri Aug 28 | `cargo test` |
| `r02` | **r02_ownership** | Ownership and moves — why a kernel needs no garbage collector | Tue Sep 1 | `cargo test` |
| `r03` | **r03_borrowing** | `&` and `&mut`, the aliasing rule, and lifetimes by example | Thu Sep 3 | `cargo test` |
| `r04` | **r04_structs_impl** | Structs, methods, `const fn`, and the newtype pattern | Fri Sep 4 | `cargo test` |
| `r05` | **r05_enums_match** | Enums, `Option`, and exhaustive `match` | Fri Sep 4 | `cargo test` |
| `r06` | **r06_collections** | Arrays, slices, `Vec`, and fixed kernel tables | Tue Sep 8 | `cargo test` |
| `r07` | **r07_traits** | Traits, generics, and the abstractions the scheduler needs | Thu Sep 10 | `cargo test` |
| `r08` | **r08_errors** | `Option`, `Result`, and `?` — errors without exceptions | Thu Sep 10 | `cargo test` |
| `c00` | **c00_echo** | Your first command: argv, writing bytes, separators vs terminators | Fri Sep 11 | `cargo test` |
| `c01` | **c01_cat** | Streaming a file through a fixed buffer; the short-read contract | Fri Sep 11 | `cargo test` |
| `c02` | **c02_wc** | Counting with O(1) state — a word-boundary state machine | Tue Sep 15 | `cargo test` |
| `c03` | **c03_head** | Parsing an argument, and stopping early | Tue Sep 15 | `cargo test` |
| `c04` | **c04_grep** | Substring search and its edge cases | Thu Sep 17 | `cargo test` |
| `a00` | **a00_asm_bridge** | RISC-V assembly called from Rust: `add3`, a byte copy, and a baby context switch | Fri Sep 18 | boots in QEMU |
| `r09` | **r09_unsafe_bridge** | Raw pointers, `unsafe`, `volatile` MMIO, and leaving `std` | Tue Sep 22 | `cargo test` |

## Module 2 — Build the Kernel

From an empty crate to a kernel that boots, pages, schedules, and handles interrupts. Each exercise starts from the reference version of everything before it, so a session that did not go well never blocks the next one.

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `00` | **00_rust_kernel_basics** | `no_std`, `no_main`, the panic handler, and `_entry` | Thu Sep 24 | compiles |
| `01` | **01_boot** | The entry trampoline, the linker script, and printing over the UART | Fri Sep 25 | boots in QEMU |
| `02` | **02_physical_memory** | A page allocator built on an intrusive free list | Thu Oct 1 | boots in QEMU |
| `03` | **03_paging** | Sv39 page tables: the `Pte` newtype, `walk`, and `mappages` | Tue Oct 6 | boots in QEMU |
| `04` | **04_processes** | The process control block, the state enum, and the process table | Thu Oct 8 | boots in QEMU |
| `05` | **05_context_switch** | `swtch` — saving and restoring registers in assembly | Fri Oct 9 | boots in QEMU |
| `06` | **06_scheduling** | A round-robin scheduler driven by real context switches | Thu Oct 15 | boots in QEMU |
| `07` | **07_spinlocks** | A `SpinLock` on atomics, with `Send`/`Sync` and an RAII guard | Thu Oct 22 | boots in QEMU |
| `08` | **08_semaphores** | A counting semaphore — and the kernel heap comes online | Fri Oct 23 | boots in QEMU |
| `09` | **09_virtual_memory** | Build the kernel page table and turn the MMU on | Tue Oct 27 | boots in QEMU |
| `10` | **10_filesystem** | An in-memory filesystem of inodes and directories | Thu Oct 29 | boots in QEMU |
| `11` | **11_devices** | A real polled UART driver, tested by loopback | Fri Oct 30 | boots in QEMU |

## Module 3 — Extend a Complete Kernel

You receive the finished Module 2 kernel and add the layers that make it a Unix: a shell, user mode, system calls, program loading, and processes.

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `12` | **12_boot_to_life** | Assemble the boot sequence — `cargo run` boots rv6 for real | Fri Oct 30 | boots in QEMU |
| `13` | **13_traps** | The M→S transition and supervisor trap handling | Thu Nov 5 | boots in QEMU |
| `14` | **14_interrupts** | Timer interrupts via the CLINT, delegated to supervisor mode | Fri Nov 6 | boots in QEMU |
| `15` | **15_console** | Interrupt-driven UART input routed through the PLIC | Fri Nov 6 | boots in QEMU |
| `16` | **16_shell** | A kernel-mode REPL: `pwd`, `ls`, `cd`, `mkdir` | Thu Nov 12 | boots in QEMU |
| `17` | **17_file_commands** | `touch`, `cat`, `echo >`, `rm`, `rmdir` | Fri Nov 13 | boots in QEMU |
| `18` | **18_user_mode** | The trampoline, the trapframe, `ecall`, and the first `sret` | Thu Nov 19 – Fri Nov 20 | boots in QEMU |
| `19` | **19_exec** | Load a named program of any size, with `argv` | Thu Dec 3 | boots in QEMU |
| `20` | **20_file_descriptors** | A per-process fd table over the filesystem | Thu Dec 3 | boots in QEMU |
| `21` | **21_fork_wait** | `fork`, `exit`, `wait`, and a real multi-process scheduler | Fri Dec 4 | boots in QEMU |
| `22` | **22_userland** | `exec` as a system call — a shell running in user mode | Tue Dec 8 | boots in QEMU |

## Extra Credit

Worked in the final week or in office hours. See [Extra Credit](extra-credit.md) for what each is worth.

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `23` | **23_elf_loader** | Read a real ELF executable — entry point, per-segment permissions, and `.bss` | Dec 8 / office hours | boots in QEMU |
| `25` | **25_ship_your_commands** | Run the commands you wrote in week 3 on your own kernel | Dec 8 / office hours | boots in QEMU |


Every layer under this line is yours:

```text
rv6$ run mygrep cat notes.txt
the cat sat
```
