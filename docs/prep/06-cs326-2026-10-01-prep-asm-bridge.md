# Prep: The Assembly Bridge — 20a

**Session:** Thursday Oct 1, 1h45 · **Exercises:** `20a_asm_bridge` · **Prep time:** ~45 min · **Lecture:** [RISC-V Registers and Calling Assembly from Rust](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md)

!!! warning "QEMU deadline is today"

    First exercise that boots on the emulated machine; no host-side fallback.
    Run `oslings doctor` **before class**. Anything red: see the
    [troubleshooting table](../guides/dev-setup.md#troubleshooting-keyed-on-what-doctor-reports)
    or get help in office hours now.

## What you will build

Three short routines in RISC-V assembly, called from Rust through
`global_asm!` and `extern "C"`, running bare-metal under QEMU:
a three-operand add that proves the calling convention works as you expect,
a byte-copy loop built from loads, stores, and local numeric labels,
and a baby context switch that saves four registers into one `#[repr(C)]`
struct, loads them from another, and returns into a different thread of
execution on a different stack. A given harness boots, calls each routine with
its edge cases (zero bytes, a context switched to itself), and the test
passes when the serial console prints `OSLINGS:PASS`.

## Concepts you need

- **ABI names and the register file** — [Lecture §2](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#2-the-rv64-register-file) · [RISC-V guide: Registers](../guides/riscv.md#registers)
- **Caller-saved vs. callee-saved** — [Lecture §3](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#3-caller-saved-and-callee-saved), [§3.1](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#31-why-a-context-switch-is-cheap) · [RISC-V guide: caller/callee split](../guides/riscv.md#the-callercallee-split)
- **The calling convention: `a0`–`a7`, `ra`, `sp`** — [Lecture §4](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#4-the-calling-convention-and-the-stack-frame) · [RISC-V guide: Calling convention](../guides/riscv.md#calling-convention)
- **Loads, stores, and `1b`/`2f` labels** — [Lecture §5.1](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#51-only-loads-and-stores-touch-memory), [§5.2](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#52-local-numeric-labels) · [RISC-V guide: Local numeric labels](../guides/riscv.md#local-numeric-labels)
- **`global_asm!`, `extern "C"`, and `#[repr(C)]`** — [Lecture §6.1](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#61-global_asm), [§6.2](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#62-extern-c-and-why-calling-it-is-unsafe), [§6.3](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#63-reprc-now-load-bearing) · [RISC-V guide: Assembly inside Rust](../guides/riscv.md#assembly-inside-rust)
- **A `ret` that lands somewhere else** — [Lecture §8.3](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#83-what-just-happened), [§8.4](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#84-save-everything-before-loading-anything)

## Read before class

| What | Time |
|---|---|
| [Lecture §2–§4](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#2-the-rv64-register-file) | 15 min |
| [Lecture §5–§6](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#5-the-instructions-you-actually-need) | 12 min |
| [Lecture §8.3–§8.4](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#83-what-just-happened) | 5 min |
| [RISC-V guide](../guides/riscv.md#registers): Registers, Calling convention, Local labels | 5 min |
| [Dev Setup §7](../guides/dev-setup.md#7-oslings-doctor): run `oslings doctor` · [QEMU guide: how to get out of QEMU](../guides/qemu-gdb.md#first-how-to-get-out-of-qemu) | 8 min |

## Mental model

The whole bridge fits in one leaf function that fills a two-field struct:

```rust
#[repr(C)]
pub struct Pair { pub lo: u64, pub hi: u64 }   // lo at offset 0, hi at 8

core::arch::global_asm!(r#"
.globl fill_pair
fill_pair:                  # a0 = *mut Pair, a1 = lo, a2 = hi
    sd   a1, 0(a0)
    sd   a2, 8(a0)
    ret                     # jalr zero, 0(ra)
"#);

extern "C" { pub fn fill_pair(p: *mut Pair, lo: u64, hi: u64); }
```

The arguments arrive in `a0`–`a2` because `extern "C"` promised they would.
A leaf touches no callee-saved register and never overwrites `ra`, so nothing
is saved. The `0` and `8` are literals welded into the `sd` instructions; they
match the struct only because `#[repr(C)]` forbids reordering fields. A
kernel's context switch is this pattern scaled up: stores at hard-coded
offsets, loads from another struct, and a `ret` to whatever `ra` was just
loaded. Get one offset wrong, or load before you store, and nothing faults;
the machine runs perfectly, in the wrong place.

## Check yourself

1. A function you call uses `s3` and `t2` as scratch. Which must it save and restore, and why? <details><summary>Answer</summary>Only `s3`: it is callee-saved, so the caller trusts it to survive. `t2` is caller-saved; the caller already assumed it was gone.</details>
2. `ret` is a pseudo-instruction. What does it expand to, and what does that say about a function that overwrites `ra` before returning? <details><summary>Answer</summary>`jalr zero, 0(ra)`. It jumps to whatever `ra` holds *now*, so a function that loads a new `ra` returns somewhere else. That is the whole mechanism of a context switch.</details>
3. Assembly does `sd a1, 8(a0)` into a struct that is *not* `#[repr(C)]`. What can go wrong? <details><summary>Answer</summary>The compiler may reorder fields, so offset 8 may be a different field. The 8 is baked into the instruction; the store silently corrupts the wrong field and no tool complains.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Work lecture [Practice Problem 3](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#problem-3-compute-the-offsets) and [Problem 4](../lectures/04-cs326-2026-09-17-riscv-registers-and-calling-assembly.md#problem-4-find-the-bug), then start reading [Friday's prep page](06-cs326-2026-10-02-prep-unsafe-and-kernel-basics.md). Chapter 2 of the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf) shows where the assembly lives in a real kernel.
