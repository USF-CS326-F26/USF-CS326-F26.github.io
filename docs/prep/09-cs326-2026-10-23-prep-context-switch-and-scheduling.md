# Prep: The Context Switch and the Scheduler — 35k · 36k

**Session:** Fri Oct 23, 1h30 · **Exercises:** `35k_context_switch`, `36k_scheduling` · **Prep time:** ~20 min · **Lecture:** [Week 9 · Processes, the Context Switch, and Scheduling](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md)

## Back from break

This session's lecture was Tue Oct 13, before Midterm 1 and fall break. Before class, reread [Week 9 · This week](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#this-week), then all of [Friday · `35k` The context switch](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#fri-35k) and [Friday · `36k` Round robin](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#fri-36k).
Three ideas matter most today: a context is only 14 registers, because the switch is entered by an ordinary call; the switch saves into one context and loads from the *other*, so its `ret` lands where the loaded `ra` points; and round robin keeps its place in a cursor that moves just past each pick.

## What you will build

First the mechanism: a context is the fourteen registers `ra`, `sp` and `s0`–`s11`, laid out by `#[repr(C)]`, and the switch routine freezes the running context, thaws another, and `ret`s into a different thread. Half of that assembly is given; you write the other half. Then the policy: a round-robin picker that scans the process table from a rotation cursor, skips anything not `Runnable`, wraps around, and drives the double switch. The harness checks that a switch round-trips (control comes back after the call) and that three runnable processes plus one sleeping one run interleaved, one turn each per rotation, instead of one running to completion.

## Concepts you need

- **Callee-saved vs. caller-saved: why 14 registers** — [Week 9 · What a context is](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#35k-context) · [RISC-V guide: The caller/callee split](../guides/riscv.md#the-callercallee-split)
- **`#[repr(C)]` offsets the assembly relies on; `ld`/`sd` with `off(reg)`** — [Week 9 · The offset contract, and a `ret` that lands elsewhere](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#35k-offsets) · [RISC-V guide: Loads, stores, and offsets](../guides/riscv.md#loads-stores-and-offsets)
- **`ret` jumps to the `ra` just loaded; `global_asm!`, `extern "C"`** — [Week 9 · The offset contract, and a `ret` that lands elsewhere](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#35k-offsets) · [RISC-V guide: Assembly inside Rust](../guides/riscv.md#assembly-inside-rust)
- **The double switch; forging a context that has never run** — [Week 9 · The double switch](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#36k-double-switch), [Week 9 · Starting a context that never ran](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#35k-fresh)
- **Mechanism vs. policy: a trait with `&mut self` state** — [Week 9 · Mechanism and policy](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#36k-policy)
- **Round robin: cursor, wraparound, advance past the winner; iterator adapters** — [Week 9 · Round robin, by its rules](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#36k-round-robin)

## Read before class

| What | Time |
|---|---|
| [Week 9 · This week](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#this-week), then [Friday · `35k` The context switch](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#fri-35k), all three sections | 5 min |
| [Week 9 · Friday · `36k` Round robin](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#fri-36k), all three sections | 3 min |
| [Week 9 · For the exam](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#exam): [The vocabulary](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#exam-terms) and [The scheduling survey](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#exam-survey). Not needed today; on Midterm 2 | 2 min |
| [RISC-V guide: The caller/callee split](../guides/riscv.md#the-callercallee-split) and [Loads, stores, and offsets](../guides/riscv.md#loads-stores-and-offsets) | 3 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 9 · Problem 3: Trace a switch through a hub](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#problem-3) and [Problem 4: Predict the round-robin order](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#problem-4); [Week 9 · The vocabulary](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#exam-terms) and [The scheduling survey](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#exam-survey) are Midterm 2 material. Then read chapter 7, "Scheduling," of the xv6 book, or start the next prep page, [Prep: Spinlocks and Semaphores](10-cs326-2026-10-29-prep-spinlocks-and-semaphores.md).
