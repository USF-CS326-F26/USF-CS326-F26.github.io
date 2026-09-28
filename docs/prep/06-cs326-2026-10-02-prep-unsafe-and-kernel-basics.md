# Prep: unsafe, and Leaving std — 21r · 30k

**Session:** Fri Oct 2, 1h30 · **Exercises:** `21r_unsafe_bridge` · `30k_kernel_basics` · **Prep time:** ~25 min · **Lecture:** [Week 6 · Below Rust](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md)

## What you will build

First, on your laptop, the inner loop of a UART driver: a raw pointer to a fixed address, volatile register access at base-plus-offset, a safe wrapper that refuses a bad offset, and a plain-memory byte copy. The tests substitute a byte array for the chip's register block. Second, the first kernel crate: a Rust binary that tells the compiler no OS exists beneath it and supplies the one function demanded in return. `oslings run` checks that each register access lands in its own slot and nothing past the end is touched, then that the kernel builds for `riscv64gc-unknown-none-elf` — no QEMU yet.

## Concepts you need

- **Raw pointer vs. reference; `.add(n)` scales by the pointee** — [Week 6 · Memory you cannot borrow: MMIO and raw pointers](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#21r-pointers) · [Unsafe guide: Raw pointers](../guides/rust-unsafe-nostd.md#raw-pointers)
- **`unsafe`: five operations, nothing disabled** — [Week 6 · What `unsafe` unlocks, and what it does not](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#21r-unsafe) · [Unsafe guide: What unsafe does not do](../guides/rust-unsafe-nostd.md#what-unsafe-does-not-do)
- **Safe wrapper, unsafe core** — [Week 6 · What `unsafe` unlocks, and what it does not](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#21r-unsafe) · [Unsafe guide: Before you write unsafe](../guides/rust-unsafe-nostd.md#before-you-write-unsafe)
- **Volatile MMIO** — [Week 6 · Volatile: the load that never repeats](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#21r-volatile)
- **`core` / `alloc` / `std`** — [Week 6 · What `std` is, and why a kernel cannot have it](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#30k-std) · [Unsafe guide: core, alloc, and std](../guides/rust-unsafe-nostd.md#core-alloc-and-std)
- **The `no_std` skeleton, by build error** — [Week 6 · The bare-metal skeleton](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#30k-skeleton) · [Unsafe guide: The no_std skeleton](../guides/rust-unsafe-nostd.md#the-no_std-skeleton)

## Read before class

| What | Time |
|---|---|
| [Week 6 · Friday · `21r` Raw pointers, `unsafe`, and volatile](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#fri-21r), all three sections | 4 min |
| [Week 6 · Friday · `30k` Leaving `std`](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#fri-30k), both sections | 2 min |
| [Unsafe guide: What unsafe does](../guides/rust-unsafe-nostd.md#what-unsafe-does) through [Raw pointers](../guides/rust-unsafe-nostd.md#raw-pointers) | 7 min |
| [Unsafe guide: The no_std skeleton](../guides/rust-unsafe-nostd.md#the-no_std-skeleton) and [Symptoms and their causes](../guides/rust-unsafe-nostd.md#symptoms-and-their-causes) | 4 min |
| [Setup: Check your environment](../assignments/setup.md#6-check-your-environment) — target installed? | 2 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 6 · Problem 2: Which lines need `unsafe`?](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#problem-2), then run the `rustc --print cfg` command from [Week 6 · Reading `riscv64gc-unknown-none-elf`](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#deeper-target) yourself. Then start reading [next Thursday's prep page](07-cs326-2026-10-08-prep-boot-and-physical-memory.md) and its lecture, [Boot: From Reset to `kmain`](../lectures/05-cs326-2026-09-24-boot-from-reset-to-kmain.md). Afterward, the [xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf) chapter 2 through section 2.6, and [The Rustonomicon](https://doc.rust-lang.org/nomicon/) chapters 1–3.
