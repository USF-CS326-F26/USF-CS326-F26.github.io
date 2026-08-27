# Prep: Processes and the PCB — 34k

**Session:** Thu Oct 22, 1h45 · **Exercises:** `34k_processes` · **Prep time:** ~45 min · **Lecture:** [Processes and the Process Control Block](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md)

## What you will build

The kernel's process table: a fixed static array of `NPROC` process control blocks, each a `Proc` with a pid, a `ProcState`, and its own page-table root, plus the two bookkeeping operations that claim an empty slot and give it back. Nothing runs or switches yet; that is Friday. The self-test allocates processes with distinct pids, fills the table to exactly `NPROC`, confirms a full table refuses another, frees one slot, and checks that exactly one more allocation then succeeds with the freed page table gone.

## Concepts you need

- **A process is the unit of isolation and of scheduling; the PCB is the process** — [Processes §1](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#1-a-process-is-a-data-structure) · [rv6 Architecture § Processes, switching, and scheduling](../guides/rv6-architecture.md#processes-switching-and-scheduling)
- **Deriving `Proc` field by field: pid, state, page-table root** — [Processes §2](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#2-deriving-the-pcb-field-by-field)
- **The five-state lifecycle as a Rust `enum`; a new slot starts `Runnable`** — [Processes §3](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#3-the-process-state-machine)
- **A fixed static table built at compile time from a `const fn`** — [Processes §4](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#4-the-process-table)
- **pids are never reused; slot indices are** — [Processes §4](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#pids-and-slots-are-different-things)
- **Raw pointers into a `static mut` through `addr_of_mut!`, never `&mut`** — [Processes §4](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#raw-pointers-into-a-static-mut)
- **Ownership by hand: one owner, one release; release first, `Unused` last** — [Processes §5](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#5-ownership-without-the-borrow-checker)

## Read before class

| What | Time |
|---|---|
| Processes §1–§2 (definition; the PCB field by field) | 15 min |
| Processes §3–§4 (state machine; fixed table; pids versus slots) | 15 min |
| Processes §5, §7 (ownership by hand; what is not in the PCB yet) | 10 min |
| rv6 Architecture § Processes, switching, and scheduling | 5 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Work [Problem 1](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#problem-1-slots-pids-and-reuse) and [Problem 4](../lectures/07-cs326-2026-10-06-processes-and-the-process-control-block.md#problem-4-legal-and-illegal-transitions) on paper, then start reading Friday's prep page, [Prep: Context Switch and Scheduling](09-cs326-2026-10-23-prep-context-switch-and-scheduling.md), where today's slots get a scheduler. For the C ancestor, read chapter 7, "Scheduling," of the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf).
