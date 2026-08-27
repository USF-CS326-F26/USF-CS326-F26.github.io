# Prep: Boot to Life, Traps, and Interrupts — 42k · 43k · 44k

**Session:** Friday Nov 6, 1h30 · **Exercises:** `42k_boot_to_life` · `43k_traps` · `44k_interrupts` · **Prep time:** ~45 min · **Lecture:** [Filesystems, Devices, and the Boot Sequence](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md) · [Traps, Privilege Modes, and Interrupts](../lectures/11-cs326-2026-11-03-traps-privilege-modes-and-interrupts.md)

## What you will build

Three few-line pieces; the reading is the work. First, the boot sequence: console, page allocator, kernel page table with the MMU on, and process table come up in dependency order, and `cargo run` prints the banner and idles. Second, the kernel drops from machine mode to supervisor mode, points `stvec` at the given trap vector, and survives its first trap — a breakpoint it counts and steps past. Third, it opens the interrupt gates so the CLINT timer, armed in machine mode and forwarded down as a supervisor software interrupt, is acknowledged and counted. The graded build checks that each subsystem reports ready, that execution continues past the breakpoint, and that ticks arrive at a sensible pace — neither absent nor a storm.

## Concepts you need

- **Boot is a dependency graph** — [L10 §7](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#7-boot-is-a-dependency-graph) · [rv6 Architecture § The boot sequence](../guides/rv6-architecture.md#the-boot-sequence)
- **Three privilege modes** — [L11 §1](../lectures/11-cs326-2026-11-03-traps-privilege-modes-and-interrupts.md#1-three-modes-and-what-each-may-do) · [RISC-V guide § Privilege modes](../guides/riscv.md#privilege-modes)
- **Exception, interrupt, trap** — [L11 §2](../lectures/11-cs326-2026-11-03-traps-privilege-modes-and-interrupts.md#2-exception-interrupt-trap-three-words-three-meanings)
- **The machine-to-supervisor handoff** — [L11 §3](../lectures/11-cs326-2026-11-03-traps-privilege-modes-and-interrupts.md#3-the-machine-to-supervisor-handoff) · [RISC-V guide § Control and status registers](../guides/riscv.md#control-and-status-registers)
- **The supervisor trap path** — [L11 §4](../lectures/11-cs326-2026-11-03-traps-privilege-modes-and-interrupts.md#4-the-supervisor-trap-path) · [RISC-V guide § What the hardware does on a trap](../guides/riscv.md#what-the-hardware-does-on-a-trap-and-what-it-does-not)
- **The timer's detour and the three gates** — [L11 §5](../lectures/11-cs326-2026-11-03-traps-privilege-modes-and-interrupts.md#5-the-timer-and-why-it-takes-a-detour) · [rv6 Architecture § Path 1](../guides/rv6-architecture.md#path-1-the-machine-mode-timer-interrupt)

## Read before class

| What | Time |
|---|---|
| L10 §7–8 (boot graph; reading a boot log) | 12 min |
| L11 §1–2 (modes; exception versus interrupt) | 8 min |
| L11 §3–5 (handoff; trap path; timer) | 20 min |
| [RISC-V guide § Decoding `scause`](../guides/riscv.md#decoding-scause) · [rv6 Architecture § Two builds](../guides/rv6-architecture.md#two-builds-of-the-same-kernel) | 5 min |

## Mental model

Every trap lands on one vector with one cause register, so a handler first decodes `scause`. Two values you will not meet on Friday:

```rust
let a: usize = 0x8000_0000_0000_0009; // bit 63 set:   interrupt 9  (a keypress)
let b: usize = 0x0000_0000_0000_000d; // bit 63 clear: exception 13 (load page fault)
let is_interrupt = |c: usize| (c >> 63) == 1;   // test this FIRST
let code = |c: usize| c & 0xff;
// a: nothing failed; sepc is already the next instruction. Acknowledge, return.
// b: sepc points AT the load: re-run it once repaired, or kill the process.
```

The codes overlap — 9 is also "ecall from S-mode" — so skipping the top-bit test turns a page fault into a "handled" tick that spins on one instruction. Next week's keystroke, and later the system call, take this exact path.

## Check yourself

1. Why must the page allocator come up before the MMU is switched on? <details><summary>Answer</summary>Building the kernel page table allocates pages. With the free list empty the root is null, `satp` points at physical page 0, and the next instruction fetch goes through garbage — a fault with no handler and no message.</details>
2. A breakpoint handler returns without touching `sepc`. What happens, and why is an interrupt different? <details><summary>Answer</summary>`sret` resumes at `sepc`, still the `ebreak`, so it traps again forever and the harness times out. An exception's instruction has not completed, so the handler chooses re-run or step past; an interrupt failed nothing, and `sepc` already holds the next instruction.</details>
3. The timer ticks once, then the kernel hangs. Which gate is closed? <details><summary>Answer</summary>None — one tick was delivered, so all three were open. The handler did not clear `sip.SSIP`; `sret` restores `SIE` from `SPIE` and the still-pending interrupt is redelivered immediately: an interrupt storm, one instruction of progress per trap.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Watch it boot with `cargo run` from `rv6/`. Then start next Thursday's prep page (console and shell), or the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf) chapter 4, "Traps and system calls."
