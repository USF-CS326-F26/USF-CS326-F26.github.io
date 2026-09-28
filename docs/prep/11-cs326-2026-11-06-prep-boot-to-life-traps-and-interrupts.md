# Prep: Boot to Life, Traps, and Interrupts — 42k · 43k · 44k

**Session:** Fri Nov 6, 1h30 · **Exercises:** `42k_boot_to_life`, `43k_traps`, `44k_interrupts` · **Prep time:** ~30 min · **Lecture:** [Week 11 · Files, Boot Order, and Traps](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md)

## What you will build

Three few-line pieces; the reading is the work. First, the boot sequence: four subsystems — the kernel page table with the MMU on, the process table, the console, and the page allocator — come up in an order their dependencies decide, and `cargo run` prints the banner and idles. Second, the kernel drops from machine mode to supervisor mode, points `stvec` at the given trap vector, and survives its first trap — a breakpoint it counts and steps past. Third, it opens the interrupt gates so the CLINT timer, armed in machine mode and forwarded down as a supervisor software interrupt, is acknowledged and counted. The graded build checks that each subsystem reports ready, that execution continues past the breakpoint, and that ticks arrive at a sensible pace — neither absent nor a storm.

## Concepts you need

- **Boot is a dependency graph** — [Week 11 · Boot is a dependency graph](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#42k-graph) · [rv6 Architecture: The boot sequence](../guides/rv6-architecture.md#the-boot-sequence)
- **Three privilege modes** — [Week 11 · Three modes, three words](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-modes) · [RISC-V guide: Privilege modes](../guides/riscv.md#privilege-modes)
- **Exception, interrupt, trap** — [Week 11 · Three modes, three words](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-modes)
- **The machine-to-supervisor handoff** — [Week 11 · Three modes, three words](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-modes), [For the exam: The M→S handoff](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam-handoff) · [RISC-V guide: Control and status registers](../guides/riscv.md#control-and-status-registers)
- **The supervisor trap path** — [Week 11 · The supervisor trap path](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-path), [Re-run or step past](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-sepc), [Reading and writing CSRs](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-csrs) · [RISC-V guide: What the hardware does on a trap](../guides/riscv.md#what-the-hardware-does-on-a-trap-and-what-it-does-not)
- **The timer's detour and the three gates** — [Week 11 · Why a timer, and why it takes a detour](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#44k-timer), [Decode `scause` top bit first](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#44k-scause), [Three gates and a pending bit](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#44k-gates) · [rv6 Architecture: Path 1, the machine-mode timer interrupt](../guides/rv6-architecture.md#path-1-the-machine-mode-timer-interrupt)

## Read before class

| What | Time |
|---|---|
| [Week 11 · Friday · `42k` Boot to life](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#fri-42k), both sections | 3 min |
| [Week 11 · Friday · `43k` Traps](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#fri-43k), all four sections | 6 min |
| [Week 11 · Friday · `44k` The timer](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#fri-44k), all three sections | 5 min |
| [Week 11 · For the exam](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam): [The M→S handoff](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam-handoff) and [`stval` and `sscratch`](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam-stval). Not needed today; on Midterm 2 | 2 min |
| [RISC-V guide: Decoding `scause`](../guides/riscv.md#decoding-scause) and [rv6 Architecture: Two builds of the same kernel](../guides/rv6-architecture.md#two-builds-of-the-same-kernel) | 5 min |

## Mental model

Every trap lands on one vector with one cause register, so a handler first decodes `scause`. Two values you will not meet on Friday:

```rust
let a: usize = 0x8000_0000_0000_0009; // bit 63 set:   interrupt 9  (a keypress)
let b: usize = 0x0000_0000_0000_000d; // bit 63 clear: exception 13 (load page fault)
// test bit 63 FIRST; only then read the cause code in the low bits
// a: nothing failed; sepc is already the next instruction. Acknowledge, return.
// b: sepc points AT the load: re-run it once repaired, or kill the process.
```

The codes overlap — 9 is also "ecall from S-mode" — so skipping the top-bit test turns an instruction access fault, exception 1, into a "handled" tick that spins on one instruction. Next week's keystroke, and later the system call, take this exact path.

## Check yourself

1. Why must the page allocator come up before the MMU is switched on? <details><summary>Answer</summary>Building the kernel page table allocates pages. With the free list empty the root is null, `satp` points at physical page 0, and the next instruction fetch goes through garbage — a fault with no handler and no message.</details>
2. A breakpoint handler returns without touching `sepc`. What happens, and why is an interrupt different? <details><summary>Answer</summary>`sret` resumes at `sepc`, still the `ebreak`, so it traps again forever and the harness times out. An exception's instruction has not completed, so the handler chooses re-run or step past; an interrupt failed nothing, and `sepc` already holds the next instruction.</details>
3. The timer ticks once, then the kernel hangs. Which gate is closed? <details><summary>Answer</summary>None — one tick was delivered, so all three were open. The handler did not clear `sip.SSIP`; `sret` restores `SIE` from `SPIE` and the still-pending interrupt is redelivered immediately: an interrupt storm, with not one instruction of progress between traps.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 11 · Problem 2: Decode five causes](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#problem-2), [Problem 3: Trace a tick](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#problem-3) and [Problem 4: Order a boot](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#problem-4) on paper. Watch it boot with `cargo run` from `rv6/`. Then start next Thursday's prep page, [Prep: The Console and the Kernel Shell](12-cs326-2026-11-12-prep-console-and-shell.md), or the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf) chapter 4, "Traps and system calls."
