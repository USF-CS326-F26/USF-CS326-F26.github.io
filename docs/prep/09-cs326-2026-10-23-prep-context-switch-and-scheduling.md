# Prep: The Context Switch and the Scheduler — 35k · 36k

**Session:** Fri Oct 23, 1h30 · **Exercises:** `35k_context_switch`, `36k_scheduling` · **Prep time:** ~35 min · **Lecture:** [The Context Switch and the Scheduler](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md)

## What you will build

First the mechanism: a context is the fourteen callee-saved registers laid out by `#[repr(C)]`, and the switch routine freezes the running context, thaws another, and `ret`s into a different thread. Half of that assembly is given; you write the other half. Then the policy: a round-robin picker that scans the process table from a rotation cursor, skips anything not `Runnable`, wraps around, and drives the double switch. The harness checks that a switch round-trips (control comes back after the call) and that three runnable processes plus one sleeping one run interleaved, one turn each per rotation, instead of one running to completion.

## Concepts you need

- **Callee-saved vs. caller-saved: why 14 registers** — [Context Switch and Scheduler §1](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#1-what-a-context-actually-is) · [RISC-V § The caller/callee split](../guides/riscv.md#the-callercallee-split)
- **`#[repr(C)]` offsets (`ra` 0, `sp` 8, `s11` 104); `ld`/`sd` with `off(reg)`** — [Context Switch and Scheduler §1](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#two-languages-have-to-agree-on-byte-offsets) · [RISC-V § Loads, stores, and offsets](../guides/riscv.md#loads-stores-and-offsets)
- **`ret` jumps to the `ra` just loaded; `global_asm!`, `extern "C"`** — [Context Switch and Scheduler §2](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md) · [RISC-V § Assembly inside Rust](../guides/riscv.md#assembly-inside-rust)
- **The double switch; forging a context that has never run** — [Context Switch and Scheduler §3](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#3-the-double-switch), [§3 Bootstrapping](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#bootstrapping-a-context-that-has-never-run)
- **Mechanism vs. policy: a trait with `&mut self` state** — [Context Switch and Scheduler §4](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#4-mechanism-and-policy) · [Traits, Generics, and the ulib Facade §2](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#2-traits-a-contract-between-types)
- **Round robin: cursor, wraparound, advance past the winner; iterator adapters** — [Context Switch and Scheduler §5](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#5-round-robin) · [Rust for Systems § Iteration](../guides/rust-for-systems.md#iteration)

## Read before class

| What | Time |
|---|---|
| Context Switch and Scheduler §1–§2 | 12 min |
| Context Switch and Scheduler §3 | 8 min |
| Context Switch and Scheduler §4–§5 | 8 min |
| RISC-V guide: The caller/callee split; Loads, stores, and offsets | 7 min |

## Mental model

Two contexts ping-pong through a generic `switch(old, new)`, a call that comes back somewhere else.

```text
L = { ra: ?,    sp: ? }             # the loop; saved by its first switch
P = { ra: ping, sp: page + 4096 }   # forged: entry, top of a fresh page

loop:  switch(&L, &P)           # save into L, load P, ret lands at ping
ping:  s3 = 7; switch(&P, &L)   # save into P, load L, ret lands after loop's call
loop:  switch(&L, &P)           # ret lands inside ping's own call; s3 is 7 again
```

`ret` jumps to the `ra` loaded just before, so the routine "returns" into whichever context it loaded. Every transition in rv6 (yield, block, exit) is this move, always via the scheduler's own context, so the picking code never stands on a stack about to be freed.

## Check yourself

1. Why does a context hold `ra`, `sp`, and `s0`–`s11` but no `t` or `a` registers and no program counter? <details><summary>Answer</summary>The caller spilled any `t`/`a` value it still needed before the call, so saving `sp` reaches them. A suspended thread is always paused inside the switch call, so `ra` is its resume address.</details>
2. States are `[Runnable, Sleeping, Runnable, Sleeping, Runnable]` and the cursor is 3; next four picks and final cursor? What if the cursor is set to the winner instead? <details><summary>Answer</summary>Picks 4 (cursor 0), 0 (cursor 1), 2 (cursor 3), 4 (cursor 0). Cursor-equals-winner picks slot 4 forever, starving the other two.</details>
3. A forged context sets `sp` to the base of its fresh page rather than base + 4096. What goes wrong, and when? <details><summary>Answer</summary>Stacks grow downward, so the first push writes below the page. Nothing faults at the switch; the corruption surfaces later, in unrelated code.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Work [Practice Problems](../lectures/08-cs326-2026-10-13-context-switch-and-scheduling.md#practice-problems) 3 and 5; the §6 vocabulary is Midterm 2 material. Then read chapter 7, "Scheduling," of the xv6 book, or start the next prep page, [Prep: Spinlocks and Semaphores](10-cs326-2026-10-29-prep-spinlocks-and-semaphores.md).
