# All Exercises

Every exercise in the course, in order. Each is released at the start of the
session listed and you run `oslings submit` before you leave the room, passed
or not. An exercise not passed in class can be finished on your own for 75%:
an unfinished one is completed at a make-up session — office hours, on the
class network — before the next session. Two hints ship
with each exercise; the reference solution ships with the next release
(`oslings solution <name>`).

Run one with `oslings run <name>`, or just `oslings` for the full-screen app.


## Module 1 — Rust, Commands, and Bridges to Bare Metal

Exercises `00r`–`21r`. Everything here runs on your own laptop with `cargo test`, and every exercise is self-contained — none depends on code from an earlier one. The two bridges at the end are the exception in kind: `20a_asm_bridge` runs bare metal and is the deadline for a working QEMU (Thu Oct 1), and `21r_unsafe_bridge` is the last stop before the kernel.

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `00r` | **00r_hello_rust** | Bindings, integer types, hex literals, and the numbers a kernel is written in | Thu Aug 27 | `cargo test` |
| `01r` | **01r_control_flow** | Functions, `if`/`loop`/`while`, and integer overflow | Fri Aug 28 | `cargo test` |
| `02r` | **02r_ownership** | Ownership and moves — why a kernel needs no garbage collector | Thu Sep 3 | `cargo test` |
| `03r` | **03r_borrowing** | `&` and `&mut`, the aliasing rule, and lifetimes by example | Fri Sep 4 | `cargo test` |
| `04r` | **04r_structs_impl** | Structs, methods, `const fn`, and the newtype pattern | Thu Sep 10 | `cargo test` |
| `05r` | **05r_enums_match** | Enums, `Option`, and exhaustive `match` | Fri Sep 11 | `cargo test` |
| `06r` | **06r_collections** | Arrays, slices, `Vec`, and fixed kernel tables | Thu Sep 17 | `cargo test` |
| `07r` | **07r_traits** | Traits, generics, and the abstractions the scheduler needs | Thu Sep 17 | `cargo test` |
| `08r` | **08r_errors** | `Option`, `Result`, and `?` — errors without exceptions | Fri Sep 18 | `cargo test` |
| `10c` | **10c_echo** | Your first command: argv, writing bytes, separators vs terminators | Fri Sep 18 | `cargo test` |
| `11c` | **11c_cat** | Streaming a file through a fixed buffer; the short-read contract | Thu Sep 24 | `cargo test` |
| `12c` | **12c_wc** | Counting with O(1) state — a word-boundary state machine | Fri Sep 25 | `cargo test` |
| `13c` | **13c_grep** | Substring search and its edge cases | Fri Sep 25 | `cargo test` |
| `20a` | **20a_asm_bridge** | RISC-V assembly called from Rust: `add3`, a byte copy, and a baby context switch | Thu Oct 1 | boots in QEMU |
| `21r` | **21r_unsafe_bridge** | Raw pointers, `unsafe`, `volatile` MMIO, and leaving `std` | Fri Oct 2 | `cargo test` |

## Module 2 — Build the Kernel

Exercises `30k`–`53k`. From an empty crate to a kernel that boots, pages, schedules, takes interrupts, runs a shell, and finally runs your own Module 1 commands in user mode. Kernel exercises are cumulative: each starts from the reference version of everything before it, so read the given code before you write the marker. Later exercises give more code and ask for one focused piece.

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `30k` | **30k_kernel_basics** | `no_std`, `no_main`, the panic handler, and `_entry` | Fri Oct 2 | compiles |
| `31k` | **31k_boot** | The entry trampoline, the linker script, and printing over the UART | Thu Oct 8 | boots in QEMU |
| `32k` | **32k_physical_memory** | A page allocator built on an intrusive free list | Thu Oct 8 | boots in QEMU |
| `33k` | **33k_paging** | Sv39 page tables: the `Pte` newtype, `walk`, and `mappages` | Fri Oct 9 | boots in QEMU |
| `34k` | **34k_processes** | The process control block, the state enum, and the process table | Thu Oct 22 | boots in QEMU |
| `35k` | **35k_context_switch** | `swtch` — saving and restoring registers in assembly | Fri Oct 23 | boots in QEMU |
| `36k` | **36k_scheduling** | A round-robin scheduler driven by real context switches | Fri Oct 23 | boots in QEMU |
| `37k` | **37k_spinlocks** | A `SpinLock` on atomics, with `Send`/`Sync` and an RAII guard | Thu Oct 29 | boots in QEMU |
| `38k` | **38k_semaphores** | A counting semaphore — and the kernel heap comes online | Thu Oct 29 | boots in QEMU |
| `39k` | **39k_virtual_memory** | Build the kernel page table and turn the MMU on | Fri Oct 30 | boots in QEMU |
| `40k` | **40k_filesystem** | An in-memory filesystem of inodes and directories | Thu Nov 5 | boots in QEMU |
| `42k` | **42k_boot_to_life** | Assemble the boot sequence — `cargo run` boots rv6 for real | Fri Nov 6 | boots in QEMU |
| `43k` | **43k_traps** | The M→S transition and supervisor trap handling | Fri Nov 6 | boots in QEMU |
| `44k` | **44k_interrupts** | Timer interrupts via the CLINT, delegated to supervisor mode | Fri Nov 6 | boots in QEMU |
| `45k` | **45k_console** | Interrupt-driven UART input routed through the PLIC | Thu Nov 12 | boots in QEMU |
| `46k` | **46k_shell** | A kernel-mode REPL: `pwd`, `ls`, `cd`, `mkdir` | Thu Nov 12 | boots in QEMU |
| `48k` | **48k_user_mode** | The trampoline, the trapframe, `ecall`, and the first `sret` | Fri Nov 13 | boots in QEMU |
| `49k` | **49k_exec** | Load a named program of any size, with `argv` | Thu Dec 3 | boots in QEMU |
| `50k` | **50k_file_descriptors** | A per-process fd table over the filesystem | Thu Dec 3 | boots in QEMU |
| `51k` | **51k_fork_wait** | `fork`, `exit`, `wait`, and a real multi-process scheduler | Fri Dec 4 | boots in QEMU |
| `52k` | **52k_userland** | `exec` as a system call — a shell running in user mode | Fri Dec 4 | boots in QEMU |
| `53k` | **53k_ship_your_commands** | Run the commands you wrote in Module 1 on your own kernel | Fri Dec 4 | boots in QEMU |

## Extra credit

Optional, released alongside the session listed, and not worked in class. Nothing later depends on this code. Each is worth a small amount; extra credit is capped at +3% of the course grade. See [Extra Credit](extra-credit.md).

| # | Exercise | What you build | Session | Passes when |
|---|---|---|---|---|
| `14c` | **14c_head** | Parsing an argument, and stopping early | Fri Sep 25 | `cargo test` |
| `41k` | **41k_devices** | A real polled UART driver, tested by loopback | Thu Nov 5 | boots in QEMU |
| `47k` | **47k_file_commands** | `touch`, `cat`, `echo >`, `rm`, `rmdir` | Thu Nov 12 | boots in QEMU |
| `54k` | **54k_elf_loader** | Read a real ELF executable — entry point, per-segment permissions, and `.bss` | Fri Dec 4 | boots in QEMU |


Every layer under this line is yours:

```text
rv6$ run mygrep cat notes.txt
the cat sat
```
