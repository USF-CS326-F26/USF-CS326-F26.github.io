# Midterm 2

**Thursday, November 19 — in class, full period.** No exercise session on
Friday, November 20.

## Format

Pencil and paper, closed book. One permitted reference: the
[Cheatsheet](../guides/cheatsheet.md), printed. No electronic devices.

## Scope

**Cumulative in concepts, but weighted heavily toward `34k`–`48k`** —
processes through user mode. Anything from Midterm 1 may reappear as a
building block; nothing will be asked that depends only on Midterm 1 material.
Worth 15% of the course grade.

**Processes through the console (`34k`–`45k`)**

- Context switching: `swtch`, which registers and why only those, `#[repr(C)]`,
  and the double switch through the per-CPU scheduler context
- Scheduling: mechanism vs policy, round robin, and the survey — FCFS, SJF,
  priority, MLFQ, CFS; fairness, quantum, throughput, starvation
- Concurrency: how a race arises, atomicity, test-and-set vs compare-and-swap,
  `Acquire`/`Release`, the RAII guard, `Send`/`Sync`, deadlock, lock ordering,
  and why a kernel disables interrupts while holding a spinlock
- Semaphores, P/V, the lost-wakeup problem, bounded buffers
- The kernel heap: what `#[global_allocator]` is and what `Box`/`Vec`/`Arc` cost
- Turning the MMU on: the bootstrap paradox, identity mapping, the `satp`
  encoding, `sfence.vma`, the TLB
- Filesystems: inodes vs directories, why the name lives in the directory,
  path resolution
- Devices: registers, status flags, polling, `volatile`
- Boot order as a dependency graph
- Traps: M/S/U, exceptions vs interrupts, the M→S handoff and its six CSRs,
  `stvec`/`sepc`/`scause`/`sstatus`/`stval`, `sret`
- Timer interrupts, the CLINT, and why preemption needs a timer
- Device interrupts, the PLIC's four-register protocol, the console ring buffer

**Shell and user mode (`46k`–`48k`)**

- The shell as a REPL and the command table
- User mode: privilege levels, the trampoline page and why it must be mapped
  at the same virtual address in both tables, the trapframe, `ecall`

**Not on this exam**: `exec`, file descriptors, `fork`/`wait`, pipes. Those are
the final's territory.

## What the questions look like

Same three shapes as Midterm 1 — trace the registers, decode the bits, order
the steps — plus two that are specific to this material:

**Find the race.** Given two concurrent sequences, identify an interleaving
that breaks an invariant, and say what makes it safe.

**Trace the trap.** Given an `ecall` or a timer interrupt, walk what the
hardware does and what the software does at each step, naming the CSR involved.

## How to prepare

1. Reread `35k`, `37k`, `39k`, `43k`, `48k` — the five that carry the most
   examinable material.
2. Redraw from memory: the double context switch, the kernel address space
   after `satp` is set, the trap path from `ecall` to `sret`, the PLIC
   handshake.
3. Do [Practice Set 2](practice-set-02.md) on paper.
4. Use [rv6 Architecture](../guides/rv6-architecture.md) as the map; it has all
   three trap paths as diagrams.
