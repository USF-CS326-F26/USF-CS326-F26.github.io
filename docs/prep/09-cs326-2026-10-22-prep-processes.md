# Prep: Processes and the PCB — 34k

**Session:** Thu Oct 22, 1h45 · **Exercises:** `34k_processes` · **Prep time:** ~25 min · **Lecture:** [Week 9 · Processes, the Context Switch, and Scheduling](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md)

## Back from break

This session's lecture was Tue Oct 13, before Midterm 1 and fall break. Before class, reread [Week 9 · This week](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#this-week) and all of [Thursday · `34k` Processes](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#thu-34k), from [A process is a data structure](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-process) through [Ownership by hand](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-ownership).
Three ideas matter most today: a claimed slot starts `Runnable`, not `Running`; slots are recycled, but pids never are; and a slot reads `Unused` only once it owns nothing.

## What you will build

The kernel's process table: a fixed static array of `NPROC` process control blocks, each a `Proc` with a pid, a `ProcState`, and its own page-table root, plus the two bookkeeping operations that claim an empty slot and give it back. Nothing runs or switches yet; that is Friday. The self-test allocates processes with distinct pids, fills the table to exactly `NPROC`, confirms a full table refuses another, frees one slot, and checks that exactly one more allocation then succeeds with the freed page table gone.

## Concepts you need

- **A process is the unit of isolation and of scheduling; the PCB is the process** — [Week 9 · A process is a data structure](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-process) · [rv6 Architecture: Processes, switching, and scheduling](../guides/rv6-architecture.md#processes-switching-and-scheduling)
- **Deriving `Proc` field by field: pid, state, page-table root** — [Week 9 · The PCB: what it holds, and when](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-pcb)
- **The five-state lifecycle as a Rust `enum`; a new slot starts `Runnable`** — [Week 9 · Five states, one enum](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-states)
- **A fixed static table built at compile time from a `const fn`** — [Week 9 · The process table: slots and pids](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-table) · [Rust for Systems: `const fn`](../guides/rust-for-systems.md#const-fn)
- **pids are never reused; slot indices are** — [Week 9 · The process table: slots and pids](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-table)
- **Raw pointers into a `static mut` through `addr_of_mut!`, never `&mut`** — [Week 9 · Ownership by hand](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-ownership) · [Unsafe guide: `static mut` and `addr_of!`](../guides/rust-unsafe-nostd.md#static-mut-and-addr_of)
- **Ownership by hand: one owner, one release; release first, `Unused` last** — [Week 9 · Ownership by hand](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-ownership)

## Read before class

| What | Time |
|---|---|
| [Week 9 · This week](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#this-week), then [Thursday · `34k` Processes](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#thu-34k) through [The PCB: what it holds, and when](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-pcb) | 3 min |
| [Week 9 · Five states, one enum](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-states) and [The process table: slots and pids](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-table) | 3 min |
| [Week 9 · Ownership by hand](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-ownership) | 2 min |
| [Unsafe guide: `static mut` and `addr_of!`](../guides/rust-unsafe-nostd.md#static-mut-and-addr_of) | 3 min |
| [rv6 Architecture: Processes, switching, and scheduling](../guides/rv6-architecture.md#processes-switching-and-scheduling), the table and the six lifecycle steps | 4 min |

## Mental model

A four-slot table, traced by hand. Slots recycle; pids never do.

```text
boot        [Unused      Unused      Unused  Unused]   next pid 1
claim -> 0  [Runnable 1  Unused      Unused  Unused]   next pid 2
claim -> 1  [Runnable 1  Runnable 2  Unused  Unused]   next pid 3
give back 0 [Unused      Runnable 2  Unused  Unused]   page table freed, field nulled
claim -> 0  [Runnable 3  Runnable 2  Unused  Unused]   same address, new identity
```

A `*mut Proc` to slot 0 taken on line 2 still points at slot 0 on line 5, but the process it named is gone; only the pid said which run that was. Notice the order on line 4: the page table returns to the free list and its field is nulled *before* the slot reads `Unused`. An `Unused` slot advertises itself as claimable, so flipping the state first can free a page table the next claimant just installed.

## Check yourself

1. A freshly claimed slot is marked `Runnable`, not `Running`. Why? <details><summary>Answer</summary>`Running` means "I hold the CPU, do not pick me again," and only the scheduler makes that transition, when it switches in. A new PCB has nothing to switch into yet; `Runnable` is what Friday's round-robin policy filters on.</details>
2. Slot 2 held pid 5, was given back, and is claimed again. What pid does it hold now, and what does a stale `*mut Proc` to slot 2 refer to? <details><summary>Answer</summary>Whatever the counter hands out next, never 5 again. The stale pointer is the slot's address, so it now names the new process; remember processes by pid, not by pointer or index.</details>
3. Why null the page-table field right after releasing the page? <details><summary>Answer</summary>A second release of the same slot, which rollback paths do, would put one page on the free list twice, and two future processes would share a page-table root. A leak costs a page; a double free costs the allocator.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 9 · Problem 1: Slots, pids, and reuse](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#problem-1) and [Problem 2: Legal and illegal transitions](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#problem-2) on paper, then start reading Friday's prep page, [Prep: Context Switch and Scheduling](09-cs326-2026-10-23-prep-context-switch-and-scheduling.md), where today's slots get a scheduler. For the C ancestor, read chapter 7, "Scheduling," of the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf).
