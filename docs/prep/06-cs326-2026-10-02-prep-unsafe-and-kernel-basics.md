# Prep: unsafe, and Leaving std — 21r · 30k

**Session:** Fri Oct 2, 1h30 · **Exercises:** `21r_unsafe_bridge` · `30k_kernel_basics` · **Prep time:** ~45 min · **Lecture:** [L09 Leaving `std`: `no_std` and Bare-Metal Rust](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md)

## What you will build

First, on your laptop, the inner loop of a UART driver: a raw pointer to a fixed address, volatile register access at base-plus-offset, a safe wrapper that refuses a bad offset, and a plain-memory byte copy. The tests substitute a byte array for the chip's register block. Second, the first kernel crate: a Rust binary that tells the compiler no OS exists beneath it and supplies the one function demanded in return. `oslings run` checks that each register access lands in its own slot and nothing past the end is touched, then that the kernel builds for `riscv64gc-unknown-none-elf` — no QEMU yet.

## Concepts you need

- **Raw pointer vs. reference; `.add(n)` scales by the pointee** — [L09 §2](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#2-raw-pointers) · [Guide § Raw pointers](../guides/rust-unsafe-nostd.md#raw-pointers)
- **`unsafe`: five operations, nothing disabled** — [L09 §3](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#3-unsafe-five-operations-and-a-promise) · [Guide § What unsafe does not do](../guides/rust-unsafe-nostd.md#what-unsafe-does-not-do)
- **Safe wrapper, unsafe core** — [L09 §3](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#the-shape-that-follows-safe-wrapper-unsafe-core) · [Guide § Before you write unsafe](../guides/rust-unsafe-nostd.md#before-you-write-unsafe)
- **Volatile MMIO** — [L09 §4](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#4-volatile-why-mmio-without-it-means-nothing) · [Guide § Volatile access and MMIO](../guides/rust-unsafe-nostd.md#volatile-access-and-mmio)
- **`core` / `alloc` / `std`** — [L09 §5](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#the-three-layers) · [Guide § core, alloc, and std](../guides/rust-unsafe-nostd.md#core-alloc-and-std)
- **The `no_std` skeleton, by build error** — [L09 §5](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#learn-the-errors-not-the-incantations) · [Guide § The no_std skeleton](../guides/rust-unsafe-nostd.md#the-no_std-skeleton)

## Read before class

| What | Time |
|---|---|
| [L09 §1–4](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#1-the-boundary-where-the-type-system-stops) | 15 min |
| [L09 §5–6](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#5-the-cliff-no_std) | 10 min |
| [Guide § What unsafe does](../guides/rust-unsafe-nostd.md#what-unsafe-does) through § Volatile access and MMIO | 10 min |
| [Guide § The no_std skeleton](../guides/rust-unsafe-nostd.md#the-no_std-skeleton) and [§ Symptoms and their causes](../guides/rust-unsafe-nostd.md#symptoms-and-their-causes) | 5 min |
| [Setup §6](../assignments/setup.md#6-check-your-environment) — target installed? | 5 min |

## Mental model

QEMU's `virt` board has a "test finisher" register at `0x10_0000`; storing `0x5555` there powers the machine off — how `oslings` ends every kernel run.

```rust
const FINISHER: *mut u32 = 0x10_0000 as *mut u32;   // safe: a number with a type

pub fn power_off() -> ! {                            // safe wrapper; `!` = never returns
    // promise: this address is the register
    unsafe { core::ptr::write_volatile(FINISHER, 0x5555) }
    loop {}                                          // store did not take: spin
}
```

Making the pointer is safe; only the store needs `unsafe`, in a one-line block with its promise above it. The store is volatile because the address is a chip, not RAM: as `*FINISHER = 0x5555` the compiler may reorder, merge, or delete it. Nothing mentions `std`; `core::ptr` survives `#![no_std]`, so this compiles unchanged on bare RISC-V. Every kernel driver has this shape: a small unsafe core with a named promise, wrapped in safe Rust.

## Check yourself

1. Which of these need `unsafe`: `let p = 0x1000_0000 as *mut u8;`, `p.add(5)`, `*p = 1`? Do two `&mut` borrows of one element compile inside `unsafe { }`? <details><summary>Answer</summary>The last two: making a pointer is just arithmetic; `.add` is an `unsafe fn` (an address outside the allocation is already UB); dereferencing is operation #1. The double borrow still fails with `E0499` — `unsafe` never touches the borrow checker.</details>
2. A driver polls `while *LSR & 0x20 == 0 {}` and hangs, though the device is ready. Why? <details><summary>Answer</summary>Nothing in the loop writes `*LSR`, so the optimizer hoists the load out: "not ready now, spin forever". `core::ptr::read_volatile` forces the load on every iteration.</details>
3. Under `#![no_std]`, which survive: `Option`, `Vec`, `println!`, `core::ptr::write_volatile`? Which error says the panic handler is missing? <details><summary>Answer</summary>`Option` and `write_volatile` live in `core`. `Vec` needs `alloc` and an allocator you have not written; `println!` needs an OS. The error: `` `#[panic_handler]` function required, but not found``.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Work [L09 Problem 1](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#problem-1-which-lines-need-unsafe-and-which-error-survives-it) and [Problem 5](../lectures/05-cs326-2026-09-22-leaving-std-no-std-and-bare-metal-rust.md#problem-5-interrogate-the-target), then start reading [Thursday's prep page](07-cs326-2026-10-08-prep-boot-and-physical-memory.md) and its lecture, [Boot: From Reset to `kmain`](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md). Afterward, the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf) chapter 2 through §2.6, and [The Rustonomicon](https://doc.rust-lang.org/nomicon/) chapters 1–3.
