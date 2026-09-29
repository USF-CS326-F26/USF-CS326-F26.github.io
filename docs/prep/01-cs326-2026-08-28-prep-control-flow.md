# Prep: Control Flow — 01r

**Session:** Fri Aug 28, 1h30 · **Exercises:** `01r_control_flow` · **Prep time:** ~25 min · **Lecture:** [Week 1 · Building an Operating System, and Your First Rust](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md)

## What you will build

Thursday's functions computed one thing and handed it back; Friday's have to *decide*, *repeat*, and do arithmetic near the edge of a number. You will write a few small `usize` functions on your laptop that are the kernel's page-allocator arithmetic with the pointers removed: keep an address inside the board's 128 MiB of RAM (`0x8000_0000..0x8800_0000`), walk a range one 4 KiB page at a time, and move an address up to a page boundary, both plainly and in a form that reports failure instead of wrapping.

## Concepts you need

- **Expressions vs statements: a block's value is its last expression; a trailing semicolon makes it `()`** — [Week 1 · Functions, and the semicolon that bites](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-tail), [Key terms](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#terms)
- **`if` as an expression: no truthiness, braces required, every branch the same type** — [Week 1 · `if` is an expression](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-if)
- **Three loops and half-open ranges: `a..b` excludes `b`; RAM is `KERNBASE..PHYSTOP`** — [Week 1 · Three loops, and half-open ranges](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-loops) · [Cheatsheet: Physical memory map](../guides/cheatsheet.md#physical-memory-map-qemu-virt)
- **`break` with a value: only `loop` can, since a `while` or `for` can stop without one** — [Week 1 · Three loops, and half-open ranges](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-loops), [Problem 3: Why `loop`?](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-3)
- **Integer overflow: debug panics, release wraps; the same bug either way** — [Week 1 · Overflow: debug panics, release wraps](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-overflow), [Problem 2: Debug or release?](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-2)
- **`wrapping_*`, `checked_*`, `saturating_*`: say what you mean** — [Week 1 · Say what you mean](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-explicit), [Overflow in both builds](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam-overflow)
- **`Option`, just enough: `Some` or `None`, taken apart with `match`** — [Week 1 · `Option`, in two arms](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-option) · [Rust for Systems guide: `Option<T>`](../guides/rust-for-systems.md#optiont)

## Read before class

| What | Time |
|---|---|
| [Week 1 · Functions, and the semicolon that bites](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-tail), a reread from Thursday, then [Friday · `01r` Control flow and overflow](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#fri-01r) through [Three loops, and half-open ranges](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-loops) | 6 min |
| [Week 1 · Overflow: debug panics, release wraps](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-overflow), [Say what you mean](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-explicit) and [`Option`, in two arms](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#01r-option) | 6 min |
| [Week 1 · For the exam: Overflow in both builds](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam-overflow). Not needed today; on Midterm 1 | 1 min |
| [Week 1 · Problem 2: Debug or release?](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-2), on paper, before opening the solution | 5 min |
| [Cheatsheet: Constants you must not misremember](../guides/cheatsheet.md#constants-you-must-not-misremember) | 3 min |

## Mental model

Find the largest power of two that fits in a `u8`:

```rust
let mut p: u8 = 1;
let top = loop {
    match p.checked_mul(2) {
        Some(next) => p = next,   // still fits: keep doubling
        None => break p,          // the loop's value: 128
    }
};
```

`loop` has no exit except `break`, so it can hand back a value; `checked_mul` returns an `Option<u8>`, and the `None` arm is the exit. With plain `p * 2` the stopping rule vanishes: the eighth doubling is 256, not a `u8`. Under `cargo test` that line panics with `attempt to multiply with overflow`; a release build wraps it to 0, and `0 * 2` never overflows, so the loop never ends.

## Check yourself

1. `fn cap(x: u32) -> u32 { if x > 9 { 9 } else { x }; }` — what does the compiler say, and why? <details><summary>Answer</summary>`error[E0308]: mismatched types`, expected `u32`, found `()`. The semicolon discards the `if` expression's value, so the body is `()`. Delete it and the `if` becomes the tail expression.</details>
2. The allocator's loop tests `p + PGSIZE <= stop`, not `p < stop`. What changes when `stop` is not page-aligned? <details><summary>Answer</summary>`p < stop` would hand out a final page that runs past `stop`. The allocator deals in whole pages, so the test asks "does the *whole* page fit?", the same half-open convention as `KERNBASE..PHYSTOP`.</details>
3. `let m = usize::MAX; m + 1` — what happens under `oslings run`, and under `--release`? What would you write instead? <details><summary>Answer</summary>As written, neither build runs: with `usize::MAX` in view, `rustc` rejects the line, "this arithmetic operation will overflow" ([Week 1 · Literals have types too](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#deeper-literals)). When `m` arrives at run time instead: debug, a panic, `attempt to add with overflow`; release, silently `0`. `wrapping_add(1)` when wrapping is the intent (a counter, a ring index); `checked_add(1)` when the caller must handle `None`; `saturating_add(1)` when clamping is sane. Plain `+` is for arithmetic you can prove cannot overflow.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 1 · Problem 3: Why `loop`?](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-3) and [Problem 5: An average that overflows](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-5) on paper. [Rustlings](https://github.com/rust-lang/rustlings): the `03_if` and `04_primitive_types` groups, then a peek ahead at `12_options`. [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/): Chapter 2, "A Basic Calculator" (`if`/`else`, panics, `while` and `for`, overflow, the `wrapping`/`checked`/`saturating` methods).
