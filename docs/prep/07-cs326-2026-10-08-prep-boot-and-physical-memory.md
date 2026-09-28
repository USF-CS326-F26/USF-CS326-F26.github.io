# Prep: Boot, and Physical Memory — 31k · 32k

**Session:** Thu Oct 8, 1h45 · **Exercises:** `31k_boot`, `32k_physical_memory` · **Prep time:** ~20 min · **Lecture:** [Week 7 · From Reset to Page Tables](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md)

## What you will build

First, a kernel that boots: QEMU's ROM jumps to `0x8000_0000`, the linker script has parked your entry stub there, a few hand-written assembly instructions give the hart a stack before any Rust runs, and your first Rust function prints by storing bytes to the UART at `0x1000_0000`, then stops QEMU through the test finisher. Second, a physical page allocator that carves the RAM above the linker symbol `end` into 4 KiB pages threaded on an intrusive free list. The test boots each kernel in QEMU and watches the serial console for `OSLINGS:PASS`; the allocator's given self-test also checks that a freed page comes back next.

## Concepts you need

- **Reset state and `-bios none`** — [Week 7 · The machine at reset](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#31k-reset) · [Memory Map guide: Why `0x8000_0000`](../guides/memory-map.md#why-0x8000_0000-and-what-bios-none-buys-you)
- **`virt` memory map and MMIO** — [Week 7 · The machine at reset](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#31k-reset) · [Memory Map guide: The QEMU `virt` physical map](../guides/memory-map.md#the-qemu-virt-physical-map)
- **Linker script: `.entry` first, `end` last** — [Week 7 · The linker script puts you first](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#31k-linker) · [Memory Map guide: `kernel.ld`, line by line](../guides/memory-map.md#kernelld-line-by-line)
- **A stack before any Rust** — [Week 7 · A stack before any Rust](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#31k-stack) · [RISC-V guide: Calling convention](../guides/riscv.md#calling-convention)
- **Volatile UART stores; the test finisher** — [Week 7 · The machine at reset](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#31k-reset) · [Unsafe guide: Volatile access and MMIO](../guides/rust-unsafe-nostd.md#volatile-access-and-mmio)
- **Pages; where free memory starts** — [Week 7 · Why pages](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#32k-pages), [Building the list from `end`](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#32k-building) · [Memory Map guide: What the allocator does with `end`](../guides/memory-map.md#what-the-allocator-does-with-end)
- **Intrusive free list, LIFO, the ordering bug** — [Week 7 · The intrusive free list](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#32k-free-list) · [Unsafe guide: Raw pointers](../guides/rust-unsafe-nostd.md#raw-pointers)

## Read before class

| What | Time |
|---|---|
| [Week 7 · This week](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#this-week), then [Thursday · `31k` Boot](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#thu-31k), all three sections | 5 min |
| [Week 7 · Thursday · `32k` The free list](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#thu-32k), all three sections | 5 min |
| [Week 7 · For the exam: Reset to Rust](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#exam-boot-order). Not needed today; on Midterm 1 | 1 min |
| [Memory Map guide: What the allocator does with `end`](../guides/memory-map.md#what-the-allocator-does-with-end) | 3 min |

## Mental model

In an intrusive free list the nodes *are* the resource: one head pointer lives outside the pages; each free page stores the next free page's address in its first eight bytes. Three pages, freed A, B, C:

```text
head = NULL
free(A): A[0..8] = NULL; head = A      head -> A
free(B): B[0..8] = A;    head = B      head -> B -> A
free(C): C[0..8] = B;    head = C      head -> C -> B -> A
alloc(): r = head; head = C[0..8]      returns C; head -> B -> A
free(C); alloc()                       returns C again (LIFO)
```

Why a kernel cares: freeing can never fail, because the room to record a free page is the page itself, and teardown runs exactly when memory is short. And order matters: write the page's link *before* moving the head, or the page points at itself and every allocation returns it.

## Check yourself

1. At reset `sp` is garbage. Why can the first Rust function not simply fix it? <details><summary>Answer</summary>Every compiled function begins with a prologue that stores through `sp`, so it faults before its first line; with the trap vector still zero, the machine loops forever at address 0. The fix is a few hand-written instructions that use no stack: point `sp` one past the top of a reserved array, then call into Rust. Forget it: silent hang, OSlings timeout.</details>
2. `ENTRY(...)` does not tell QEMU where to jump. What guarantees your entry stub runs first? <details><summary>Answer</summary>The ROM always jumps to `0x8000_0000`. The linker script sets the location counter there and lists `*(.entry)` first inside `.text`, so the one function marked `#[link_section = ".entry"]` lands at offset 0.</details>
3. The initial list is built by freeing every page from the page-rounded `end` up to `PHYSTOP`, ascending. Which page does the first allocation return? <details><summary>Answer</summary>The highest page, `0x87FF_F000`: pushed last, popped first.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 7 · Problem 1: The first pages out](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#problem-1) and [Problem 4: A double free, drawn](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#problem-4) on paper. Then start reading Friday's prep page, [Prep: Paging](07-cs326-2026-10-09-prep-paging.md): the pages you just handed out become page tables. Or the xv6 book's "Code: starting xv6" section (Chapter 2) and its physical memory allocation sections (Chapter 3).
