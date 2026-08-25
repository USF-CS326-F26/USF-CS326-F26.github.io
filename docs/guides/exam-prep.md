# Exam Preparation

This page is for the two weeks before each exam. It says what is examinable,
what the questions actually look like, and how to study a kernel on paper when
every habit you have built this semester involves a running QEMU. Read it once
early — it changes how you take notes while you work — and again while you
revise. For the material itself, see [Key Concepts](key-concepts.md); for the
constants, the [Cheatsheet](cheatsheet.md).

## The three exams

| Exam | When | Covers | Weight |
|---|---|---|---|
| **Midterm 1** | Tue **Oct 13**, in class, full period | Module 1 (`r00`–`r09`, `c00`–`c04`, `a00`) plus `ex00`–`ex04` | 10% |
| **Midterm 2** | Tue **Nov 24**, in class, full period | the rest of Module 2 (`ex05`–`ex15`) plus `ex16`–`ex18` | 15% |
| **Final** | **Dec 11–17**, registrar's assigned slot | cumulative, weighted toward Module 3 (`ex19`–`ex21`, plus userland and pipes) | 20% |

The final's exact date, time, and room are set by the registrar, not by the
course — check the official final exam schedule. Later exams are cumulative in
*concepts*: anything earlier may reappear as a building block, but no question
rests only on old material. You must average C or better across the three to
pass the course.

## Format

- **On paper.** No laptop, so no guess-and-check: an answer you cannot justify
  is an answer you cannot fix.
- **Closed book**, with exactly one permitted reference: the
  [Cheatsheet](cheatsheet.md), which you may print and annotate. Nothing else —
  no notes, no printed source listings.
- **No electronic devices**, including phones, watches, and calculators. All the
  arithmetic is hex shifting and masking, done by hand.
- You will not write a long program from memory. You will read code, trace it,
  decode bit layouts, order steps, and explain why something is arranged the way
  it is.

Because the cheatsheet is permitted, no question rewards memorising a constant
that is printed on it. Questions reward knowing what to *do* with the constant.

## Shape 1 — trace the registers

> **Worked example.** `proc_yield` calls `swtch(&p.context, &SCHED_CTX)`
> (`usermode.rs:365`). Give `a0`, `a1`, `ra`, and `sp` at each stage, and say
> where the final `ret` goes.

| Stage | `a0` | `a1` | `ra` | `sp` |
|---|---|---|---|---|
| entry to `swtch` | `&p.context` | `&SCHED_CTX` | into `proc_yield`, just after the call | `p`'s kernel stack |
| after the 14 `sd`s | unchanged | unchanged | unchanged | unchanged — 14 words have been *stored* into `p.context` |
| after the 14 `ld`s | unchanged | unchanged | `SCHED_CTX.ra` | `SCHED_CTX.sp` — the scheduler's stack |
| at `ret` | — | — | — | jumps to `SCHED_CTX.ra` |

The `ret` lands inside `scheduler`, on the instruction after *its* call to
`swtch` (`usermode.rs:297`) — a different function from the one that called
this `swtch`. That is the whole trick of a context switch, and it is genuinely
disorienting the first time: a function returns to a caller it never had.

Notice what is *not* saved. `a0` and `a1` are read as pointers and never
modified; no `t` or `a` register is saved or restored. `Context` has exactly fourteen fields — `ra`, `sp`,
`s0`–`s11` (`swtch.rs:5`) — because the calling convention already forced the
caller to spill anything it cared about in the caller-saved registers before
making the call. `#[repr(C)]` is on the struct because the assembly hardcodes
those byte offsets.

A syscall trace is the same shape with more moving parts. `write(1, buf, 5)`
leaves `ulib` with `a7 = 16`, `a0 = 1`, `a1 = &buf`, `a2 = 5`, then `ecall`:

| Step | Where | What holds what |
|---|---|---|
| the `ecall` | hardware | `sepc` ← address of the `ecall`; `scause` ← 8; `sstatus.SPP` ← 0 (the trap came *from* U-mode); `pc` ← `stvec` = `uservec` |
| `csrrw a0, sscratch, a0` | `uservec` | `a0` ← `TRAPFRAME` (`0x3F_FFFF_E000`); `sscratch` ← the user's `a0` |
| 31 `sd`s | `uservec` | every user register parked at a fixed offset: `a0` at 112, `a7` at 168 (`usermode.rs:33`) |
| `ld sp, 8(a0)` / `ld t0, 16(a0)` / `ld t1, 0(a0)` | `uservec` | kernel stack top, `usertrap`'s address, the kernel's `satp` |
| `csrw satp, t1` … `jr t0` | `uservec` | page table swapped mid-instruction-stream; only works because the trampoline is mapped at the same virtual address in both tables |
| `scause == 8` | `usertrap` | `tf.epc = sepc + 4`, so the `ecall` is not re-executed |
| `dispatch(tf.a7, tf.a0, tf.a1, tf.a2)` | `syscall.rs:33` | the syscall number and three arguments, read from the trapframe |
| `tf.a0 = ret` | `usermode.rs:408` | the return value, planted in the `a0` the user will wake up holding |
| `csrrw a0, sscratch, a0` … `sret` | `userret` | user `a0` restored; `pc` ← `sepc` |

Full credit is naming the register, giving its value, and saying what forces it.
"`a0` is the trapframe" is half an answer; "`a0` is the trapframe, because
`sscratch` was loaded with `TRAPFRAME` before entering user mode and `csrrw`
swaps them" is the whole one.

## Shape 2 — decode the bits

An Sv39 page table entry:

```text
 63        54 53                                10 9 8 7 6 5 4 3 2 1 0
+------------+------------------------------------+---+-+-+-+-+-+-+-+-+
|  reserved  |            PPN (44 bits)           |RSW|D|A|G|U|X|W|R|V|
+------------+------------------------------------+---+-+-+-+-+-+-+-+-+
```

> **Worked example.** What is `0x2008_041B`?

- **Flags** = low 10 bits = `0x41B & 0x3FF` = `0x01B` = `0b0001_1011` → `V`(1),
  `R`(2), `X`(8), `U`(16). `W` is clear.
- **PPN** = `0x2008_041B >> 10` = `0x8_0201`.
- **Physical address** = PPN `<< 12` = `0x8020_1000`.
- **Verdict**: a user *text* page — readable, executable, not writable,
  reachable from user mode. Exactly what `load_segment` installs
  (`vm.rs:228`: `PTE_R | PTE_X | PTE_U`).

Two things trip people up every year. First, a PTE holds a page *number*, not
an address: the `>> 12` / `<< 10` pair in `Pte::new` (`vm.rs:31`) is the entire
encoding, and the ten low bits are why they do not cancel. Second, a PTE with
`V` set and `R`, `W`, `X` all clear is **not** a leaf — it is a pointer to the
next level, which is what makes the walk loop terminate correctly
(`vm.rs:56`).

The same decoding applies to `satp`. `0x8000_0000_0008_0005`: mode field (bits
63:60) = 8 = Sv39; the low 44 bits are the root table's PPN = `0x8_0005`, so
the root page table sits at `0x8000_5000` (`make_satp`, `vm.rs:106`). Mode 0
means paging off — which is what `start.rs:37` writes before `mret`.

And to `scause`, where the top bit separates interrupts from exceptions:

| `scause` | Meaning | Handled at |
|---|---|---|
| `8` | `ecall` from U-mode — a system call | `usermode.rs:399` |
| `3` | breakpoint | `trap.rs:75` |
| `0x8000_…_0001` | supervisor *software* interrupt — the forwarded timer tick | `trap.rs:58` |
| `0x8000_…_0009` | supervisor *external* interrupt — a device via the PLIC | `trap.rs:66` |
| `12` / `13` / `15` | instruction / load / store page fault | `usermode.rs:428`, kills the process |

> **Worked example.** Translate virtual address `0x0001_0FF8`.

The index formula is `px(level, va) = (va >> (12 + 9 * level)) & 0x1FF`
(`vm.rs:44`):

| Field | Bits | Value |
|---|---|---|
| level-2 index | 38:30 | `0` |
| level-1 index | 29:21 | `0` |
| level-0 index | 20:12 | `0x10` = 16 |
| page offset | 11:0 | `0xFF8` |

So the walk reads entry 0 of the root, entry 0 of the middle table, and entry
16 of the leaf table; the physical address is that leaf's PPN `<< 12`, plus
`0xFF8`. Sanity check your answer against the map: `USER_STACK` is
`16 * 4096 = 0x1_0000` and `USER_STACK_TOP` is `0x1_1000`
(`memlayout.rs:72`–`75`), so index 16 is the stack page and `0xFF8` is its top word.
Write the arithmetic down — the index and the offset each earn credit, so a
dropped carry costs a line, not the question.

## Shape 3 — order the steps

> **Worked example.** Here are the six calls in `kinit` (`main.rs:87`),
> scrambled. Put them in order and name the constraint that fixes each.

| # | Step | What forces its position |
|---|---|---|
| 1 | `uart::init()` | printing must work before anything can fail; it is plain MMIO, needing no allocator and no MMU |
| 2 | `kalloc::init()` | builds the free list from the linker's `end` symbol up to `PHYSTOP` (`kalloc.rs:21`); everything below allocates |
| 3 | `vm::kvminithart(vm::kvmmake())` | `kvmmake` allocates every page-table page through `walk` (`vm.rs:62`), so it must follow `kalloc`; the `csrw satp` is followed immediately by `sfence.vma` (`vm.rs:177`), and the kernel identity-maps itself so the *next instruction fetch* still resolves |
| 4 | `proc::init()` | clears the fixed process table; free to move, but must precede any process creation |
| 5 | `trap::init()` | `stvec` must hold `kernelvec` before any trap is possible — and definitely before interrupts are enabled |
| 6 | `fs::FS.lock().init()` | a fixed inode table (`fs.rs:79`); its only real constraint is "before anything opens a file" |

Part of the answer is admitting which steps are genuinely interchangeable.
Steps 4 and 6 could swap; steps 2 and 3 could not. Say so, and say why.

The interesting constraints live just after `kinit`, at `main.rs:119`:
`console::init()` enables the UART's receive interrupt, programs the PLIC, and
sets `sie.SEIE`; only then does `trap::intr_on()` set the global `sstatus.SIE`.
Reverse those two and the first keystroke traps before the PLIC can say which
device caused it.

## How to prepare

1. **Reread your own code.** You wrote it, so you will recover it faster than
   anything you merely read. Midterm 1: `r02`, `r04`, `a00`, `ex02`, `ex03`.
   Midterm 2: `ex05`, `ex07`, `ex09`, `ex13`, `ex18`. Final: `ex19`, `ex20`,
   `ex21`.
2. **Redraw the diagrams from memory**, then check them: the Sv39 address split
   and PTE layout; the free list threaded through the free pages themselves;
   `_entry` → `start` → `mret` → `kmain`; the double switch between a process
   and `SCHED_CTX`; `ecall` → `uservec` → `usertrap` → `usertrapret` →
   `userret` → `sret`; the PLIC's claim/complete handshake. If you can draw it
   blank, you know it.
3. **Do the practice set on paper, before looking at the solutions.** Reading a
   worked solution feels like learning and mostly is not. Sit with a blank page
   and a timer, get it wrong, then read.
4. **Practise with the printed cheatsheet in front of you**, so that on the day
   you already know where the PTE table is rather than hunting for it.
5. **Narrate one path out loud, end to end** — a keystroke to a character on
   screen, or `fork` through `exec` to `wait`. If you can tell the story without
   stalling, you can answer the long question whatever it turns out to be.

## What is not examinable

Line numbers, OSlings CLI flags, `cargo` invocations, QEMU command lines, and
exact Rust API signatures. Structure is what is tested: "the trapframe parks
`a7` at a fixed offset, so the kernel can read the syscall number after every
user register is saved" is an answer. The number 168 is on the cheatsheet.
