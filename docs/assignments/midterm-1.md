# Midterm 1

**Tuesday, October 13 — in class, full period**

## Format

Pencil and paper, closed book. One permitted reference: the
[Cheatsheet](../guides/cheatsheet.md), which you may print and bring. No
electronic devices of any kind.

You will not be asked to write long programs from memory. You will be asked to
read code, trace what it does, decode bit layouts, and explain why something
is arranged the way it is.

## Scope

Everything through **exercise 04**, plus the concepts of exercise 05.

**Module 1 — Rust**

- Bindings, mutability, integer types and why exact widths matter
- Hex literals and the underscore convention
- Expressions vs statements, and the no-semicolon return
- Integer overflow: debug vs release, and `wrapping_*` / `checked_*`
- Ownership, moves, `Copy` vs non-`Copy`, and why there is no `free()`
- Borrowing, `&` vs `&mut`, the aliasing rule, lifetimes by example
- Structs, `impl`, methods, `const fn`, the newtype pattern, `#[repr(C)]`
- Enums, `Option`, exhaustive `match`
- Arrays, slices, `Vec`, and why kernels use fixed tables
- Traits, generics, monomorphization
- `Result`, `?`, and error enums

**Module 1 — RISC-V and the commands**

- The register file and ABI names
- The caller-saved / callee-saved split, and its consequence for context switching
- The calling convention: `a0`–`a7`, return in `a0`, `ra`, `sp`
- `global_asm!`, `extern "C"`, and why calling assembly is `unsafe`
- The instruction subset: loads, stores, branches, `ret`
- The short-read contract and why `write_all` exists
- Streaming with fixed buffers and O(1) state

**Module 2 — the kernel so far**

- `#![no_std]`, `#![no_main]`, the panic handler; what `core` gives you
- Raw pointers, `unsafe` and what it does *not* disable
- `read_volatile` / `write_volatile` and why MMIO needs them
- The boot chain: reset → `_entry` → stack → `kmain`
- The linker script: load address, the `.entry` section, the `end` symbol
- The `virt` memory map: UART, CLINT, PLIC, RAM
- Physical page allocation and the intrusive free list
- Sv39: the address split, the PTE bit layout, the three-level walk,
  **translation by hand**
- The process control block, the state machine, the fixed process table

**Not on this exam**: turning the MMU on (`ex09`), locks and semaphores beyond
the concept of a race, traps and interrupts, user mode, system calls,
filesystems.

## What the questions look like

Three shapes recur. Each appears on the exam and each is practised in
[Practice Set 1](practice-set-01.md).

**Trace the registers.** Given a short assembly routine or a `swtch`-style
sequence, say what each register holds at each step, and what the function
returns to.

**Decode the bits.** Given a PTE value, say which permissions it grants and
what physical page it points at. Given a virtual address, translate it through
a page table drawn on the page. Given a number in hex, say what it is aligned
to.

**Order the steps, and justify.** Given the pieces of a boot sequence in the
wrong order, put them right and say what constraint forces each position.

There will also be short "explain why" questions — why a kernel disables
interrupts around a spinlock, why `#[repr(C)]` is required on `Context`, why
the free list can live inside the free pages.

## How to prepare

1. **Reread your own code.** You wrote it; you will remember it better than
   anything you read. Open `r02`, `r04`, `ex02`, `ex03` and follow them.
2. **Redraw the diagrams from memory** — the Sv39 split, the PTE layout, the
   free list, the boot chain. If you can draw it, you understand it.
3. **Do [Practice Set 1](practice-set-01.md) on paper** before looking at the
   solutions. Reading a solution feels like learning and mostly is not.
4. Skim [Key Concepts](../guides/key-concepts.md) last, as a checklist.

Bring your printed [Cheatsheet](../guides/cheatsheet.md). Practise with it, so
you know where things are on it before the exam rather than during.
