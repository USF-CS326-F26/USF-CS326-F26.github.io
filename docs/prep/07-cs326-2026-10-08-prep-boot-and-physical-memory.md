# Prep: Boot, and Physical Memory — 31k · 32k

**Session:** Thu Oct 8, 1h45 · **Exercises:** `31k_boot`, `32k_physical_memory` · **Prep time:** ~45 min · **Lecture:** [Boot: From Reset to `kmain`](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md), [Physical Memory and the Free List](../lectures/06-cs326-2026-09-29-physical-memory-and-the-free-list.md)

## What you will build

First, a kernel that boots: QEMU's ROM jumps to `0x8000_0000`, the linker script has parked your entry stub there, a few hand-written assembly instructions give the hart a stack before any Rust runs, and your first Rust function prints by storing bytes to the UART at `0x1000_0000`, then stops QEMU through the test finisher. Second, a physical page allocator that carves the RAM above the linker symbol `end` into 4 KiB pages threaded on an intrusive free list. The test boots each kernel in QEMU and watches the serial console for `OSLINGS:PASS`; the allocator's given self-test also checks that a freed page comes back next.

## Concepts you need

- **Reset state and `-bios none`** — [L05 §1](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#1-the-machine-at-reset)–[§2](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#2-firmware-and-what-bios-none-deletes) · [Memory Map §Why `0x8000_0000`](../guides/memory-map.md#why-0x8000_0000-and-what-bios-none-buys-you)
- **`virt` memory map and MMIO** — [L05 §3](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#3-the-address-space-of-the-virt-board) · [Memory Map §The QEMU `virt` physical map](../guides/memory-map.md#the-qemu-virt-physical-map)
- **Linker script: `.entry` first, `end` last** — [L05 §4](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#4-kernelld-line-by-line) · [Memory Map §`kernel.ld`, line by line](../guides/memory-map.md#kernelld-line-by-line)
- **A stack before any Rust** — [L05 §5](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#what-happens-if-you-skip-it) · [RISC-V §Calling convention](../guides/riscv.md#calling-convention)
- **Volatile UART stores; the test finisher** — [L05 §6](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#why-volatile-is-not-optional)–[§7](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md#7-stopping-the-machine-and-what-comes-next) · [Unsafe Rust §Volatile access and MMIO](../guides/rust-unsafe-nostd.md#volatile-access-and-mmio)
- **Pages; where free memory starts** — [L06 §2](../lectures/06-cs326-2026-09-29-physical-memory-and-the-free-list.md#2-why-pages), [§4](../lectures/06-cs326-2026-09-29-physical-memory-and-the-free-list.md#4-where-the-list-comes-from) · [Memory Map §What the allocator does with `end`](../guides/memory-map.md#what-the-allocator-does-with-end)
- **Intrusive free list, LIFO, the ordering bug** — [L06 §3](../lectures/06-cs326-2026-09-29-physical-memory-and-the-free-list.md#3-the-intrusive-free-list), [§7](../lectures/06-cs326-2026-09-29-physical-memory-and-the-free-list.md#7-the-ordering-bug) · [Unsafe Rust §Raw pointers](../guides/rust-unsafe-nostd.md#raw-pointers)

## Read before class

| What | Time |
|---|---|
| L05 §§1–5 | 18 min |
| L05 §§6–7 | 7 min |
| L06 §§1–4 | 12 min |
| L06 §7 | 3 min |
| Memory Map §What the allocator does with `end` | 5 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Start reading Friday's prep page, [Prep: Paging](07-cs326-2026-10-09-prep-paging.md): the pages you just handed out become page tables. Or the xv6 book's "Code: starting xv6" section (Chapter 2) and its physical memory allocation sections (Chapter 3).
