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
| **Midterm 1** | Thu **Oct 15**, in class, full period | Module 1 (`00r`–`21r`) plus `30k`–`33k` | 15% |
| **Midterm 2** | Thu **Nov 19**, in class, full period | `34k`–`48k` — processes through user mode | 15% |
| **Final** | Tue **Dec 8**, in class, full period | cumulative, weighted toward `49k`–`53k` | 20% |

All three are given in class, in the period we already meet. The midterms
fall on Thursdays, with no Friday exercise session in an exam week; the final is
on the last day of class, and **there is no exam during finals week**. Later
exams are cumulative in
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

Because the cheatsheet is permitted, no question rewards memorizing a constant
that is printed on it. Questions reward knowing what to *do* with the constant.

## Shape 1 — trace the registers

> **Worked example.** `proc_yield` calls `swtch(&p.context, &SCHED_CTX)`
> (`usermode.rs`). Give `a0`, `a1`, `ra`, and `sp` at each stage, and say
> where the final `ret` goes.

| Stage | `a0` | `a1` | `ra` | `sp` |
|---|---|---|---|---|
| entry to `swtch` | `&p.context` | `&SCHED_CTX` | into `proc_yield`, just after the call | `p`'s kernel stack |
| after the 14 `sd`s | unchanged | unchanged | unchanged | unchanged — 14 words have been *stored* into `p.context` |
| after the 14 `ld`s | unchanged | unchanged | `SCHED_CTX.ra` | `SCHED_CTX.sp` — the scheduler's stack |
| at `ret` | — | — | — | jumps to `SCHED_CTX.ra` |

The `ret` lands inside `scheduler`, on the instruction after *its* call to
`swtch` (`usermode.rs`) — a different function from the one that called
this `swtch`. That is the whole trick of a context switch, and it is genuinely
disorienting the first time: a function returns to a caller it never had.

Notice what is *not* saved. `a0` and `a1` are read as pointers and never
modified; no `t` or `a` register is saved or restored. `Context` has exactly fourteen fields — `ra`, `sp`,
`s0`–`s11` (`swtch.rs`) — because the calling convention already forced the
caller to spill anything it cared about in the caller-saved registers before
making the call. `#[repr(C)]` is on the struct because the assembly hardcodes
those byte offsets.

A syscall trace is the same shape with more moving parts. `write(1, buf, 5)`
leaves `ulib` with `a7 = 16`, `a0 = 1`, `a1 = &buf`, `a2 = 5`, then `ecall`:

| Step | Where | What holds what |
|---|---|---|
| the `ecall` | hardware | `sepc` ← address of the `ecall`; `scause` ← 8; `sstatus.SPP` ← 0 (the trap came *from* U-mode); `pc` ← `stvec` = `uservec` |
| `csrrw a0, sscratch, a0` | `uservec` | `a0` ← `TRAPFRAME` (`0x3F_FFFF_E000`); `sscratch` ← the user's `a0` |
| 31 `sd`s | `uservec` | every user register parked at a fixed offset: `a0` at 112, `a7` at 168 (`usermode.rs`) |
| `ld sp, 8(a0)` / `ld t0, 16(a0)` / `ld t1, 0(a0)` | `uservec` | kernel stack top, `usertrap`'s address, the kernel's `satp` |
| `csrw satp, t1` … `jr t0` | `uservec` | page table swapped mid-instruction-stream; only works because the trampoline is mapped at the same virtual address in both tables |
| cause 8: a system call | `usertrap` | the number and arguments are read from the trapframe, because the live registers now hold kernel values; the result travels back through the trapframe's `a0` slot |
| `csrrw a0, sscratch, a0` … `sret` | `userret` | user `a0` restored; `pc` ← `sepc` |

One value in that trace is a decision, not a copy. The hardware left `sepc`
pointing *at* the `ecall`, so a kernel that resumed there unchanged would make
the same call forever. Say why the saved pc has to move past the 4-byte
instruction before `sret`, and you have the mark that most answers miss.

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
  reachable from user mode. Exactly the permissions a loaded program's code
  pages carry: the program may run them but never rewrite them.

Two things trip people up every year. First, a PTE holds a page *number*, not
an address: the `>> 12` / `<< 10` pair in `Pte::new` (`vm.rs`) is the entire
encoding, and the ten low bits are why they do not cancel. Second, a PTE with
`V` set and `R`, `W`, `X` all clear is **not** a leaf — it is a pointer to the
next level, which is what makes the walk loop terminate correctly
(`vm.rs`).

The same decoding applies to `satp`. `0x8000_0000_0008_0005`: mode field (bits
63:60) = 8 = Sv39; the low 44 bits are the root table's PPN = `0x8_0005`, so
the root page table sits at `0x8000_5000` (shift the PPN back left by 12).
Mode 0 means paging off — which is what `start.rs` writes before `mret`.

And to `scause`, where the top bit separates interrupts from exceptions:

| `scause` | Meaning | Handled at |
|---|---|---|
| `8` | `ecall` from U-mode — a system call | `usermode.rs` |
| `3` | breakpoint | `trap.rs` |
| `0x8000_…_0001` | supervisor *software* interrupt — the forwarded timer tick | `trap.rs` |
| `0x8000_…_0009` | supervisor *external* interrupt — a device via the PLIC | `trap.rs` |
| `12` / `13` / `15` | instruction / load / store page fault | `usermode.rs`, kills the process |

> **Worked example.** Translate virtual address `0x0001_0FF8`.

The index formula is `px(level, va) = (va >> (12 + 9 * level)) & 0x1FF`
(`vm.rs`):

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
(`memlayout.rs`), so index 16 is the stack page and `0xFF8` is its top word.
Write the arithmetic down — the index and the offset each earn credit, so a
dropped carry costs a line, not the question.

## Shape 3 — order the steps

> **Worked example.** Here are six steps `start()` (`start.rs`) takes in
> machine mode before `kmain` runs, scrambled. Put them in order and name the
> constraint that fixes each.

| # | Step | What forces its position |
|---|---|---|
| 1 | set `mstatus.MPP` to supervisor | `mret` reads `MPP` to choose the mode it drops into; it must be set before `mret`, and nothing else reads it |
| 2 | write `kmain`'s address into `mepc` | `mret` jumps to whatever `mepc` holds; before `mret`, otherwise free |
| 3 | write `0` to `satp` | the first supervisor-mode fetch must not be translated, because no page table exists yet; machine mode ignores `satp`, so only "before `mret`" matters |
| 4 | delegate traps with `medeleg` and `mideleg` | without it, a trap taken in supervisor mode vectors to machine mode's `mtvec` instead of the kernel's `stvec`; traps in machine mode are never delegated, so any point before `mret` works |
| 5 | open physical memory protection to all of physical memory | until a PMP entry allows it, supervisor mode may touch no memory at all, so the very first fetch at `kmain` would fault |
| 6 | `mret` | the jump itself: everything supervisor mode relies on must already be true, so it comes last |

Part of the answer is admitting which steps are genuinely interchangeable.
Steps 1 to 5 could come in any order; step 6 could not. Say so, and say why.
The `mcounteren` write and the timer set-up obey the same rule.

When the steps *do* depend on each other, as the subsystem start-up in `kinit`
does, draw the dependency graph before you write a single number: an arrow
from each step to every step it needs. Any order that respects the arrows is
correct, and two steps with no path between them are the ones you may swap.
[rv6 Architecture](rv6-architecture.md#the-boot-sequence) walks the whole boot
this way.

The same reasoning settles one ordering later in `kmain` (`main.rs`):
`console::init()` enables the UART's receive interrupt, programs the PLIC, and
sets `sie.SEIE`; only then does `trap::intr_on()` set the global `sstatus.SIE`.
Reverse those two and the first keystroke traps before the PLIC can say which
device caused it.

## How to prepare

1. **Reread your own code.** You wrote it, so you will recover it faster than
   anything you merely read. Midterm 1: `02r`, `04r`, `20a`, `32k`, `33k`.
   Midterm 2: `35k`, `37k`, `39k`, `43k`, `48k`. Final: `49k`, `50k`,
   `51k`, `52k`.
2. **Redraw the diagrams from memory**, then check them: the Sv39 address split
   and PTE layout; the free list threaded through the free pages themselves;
   `_entry` → `start` → `mret` → `kmain`; the double switch between a process
   and `SCHED_CTX`; `ecall` → `uservec` → `usertrap` → `usertrapret` →
   `userret` → `sret`; the PLIC's claim/complete handshake. If you can draw it
   blank, you know it.
3. **Do the practice set on paper, before looking at the solutions.** Reading a
   worked solution feels like learning and mostly is not. Sit with a blank page
   and a timer, get it wrong, then read.
4. **Practice with the printed cheatsheet in front of you**, so that on the day
   you already know where the PTE table is rather than hunting for it.
5. **Narrate one path out loud, end to end** — a keystroke to a character on
   screen, or `fork` through `exec` to `wait`. If you can tell the story without
   stalling, you can answer the long question whatever it turns out to be.

## What is not examinable

OSlings CLI flags, `cargo` invocations, QEMU command lines, and exact Rust API
signatures. Structure is what is tested: "the trapframe parks
`a7` at a fixed offset, so the kernel can read the syscall number after every
user register is saved" is an answer. The number 168 is on the cheatsheet.
