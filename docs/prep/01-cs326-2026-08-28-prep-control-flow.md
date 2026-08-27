# Prep: Control Flow — 01r

**Session:** Fri Aug 28, 1h30 · **Exercises:** `01r_control_flow` · **Prep time:** ~30 min · **Lecture:** [Rust I: Values, Types, and Control Flow](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md)

## What you will build

Thursday's functions computed one thing and handed it back; Friday's have to *decide*, *repeat*, and do arithmetic near the edge of a number. You will write a few small `usize` functions on your laptop that are the kernel's page-allocator arithmetic with the pointers removed: keep an address inside the board's 128 MiB of RAM (`0x8000_0000..0x8800_0000`), walk a range one 4 KiB page at a time, and move an address up to a page boundary, both plainly and in a form that reports failure instead of wrapping.

## Concepts you need

- **Expressions vs statements** — a block's value is its last expression; a trailing semicolon makes it `()` — [Lecture §4](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#4-expressions-statements-and-the-semicolon-that-bites) · [Lecture Key Concepts](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#key-concepts)
- **`if` as an expression** — no truthiness, braces required, every branch the same type — [Lecture §6](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#6-if-is-an-expression)
- **Three loops and half-open ranges** — `a..b` excludes `b`; RAM is `KERNBASE..PHYSTOP` — [Lecture §7](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#7-three-ways-to-loop) · [Cheatsheet: Physical memory map](../guides/cheatsheet.md#physical-memory-map-qemu-virt)
- **`break` with a value** — only `loop` can, because its every exit is a `break` — [Lecture §7](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#break-with-a-value)
- **Integer overflow** — debug panics, release wraps; the same bug either way — [Lecture §8](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#8-integer-overflow) · [Lecture Problem 4](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#problem-4-debug-or-release)
- **`wrapping_*`, `checked_*`, `saturating_*`** — say what you mean — [Lecture §8 Saying what you mean](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#saying-what-you-mean)
- **`Option`, just enough** — `checked_add` returns `Option<usize>`; take it apart with `match` — [Lecture §8 Option](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#option-just-enough-of-it) · [Rust for Systems §4 `Option<T>`](../guides/rust-for-systems.md#optiont)

## Read before class

| What | Time |
|---|---|
| Lecture §4, §6, §7 (expressions, `if`, the three loops) | 12 min |
| Lecture §8 (overflow, the explicit methods, `Option`) | 10 min |
| Lecture Practice Problem 4, on paper, before opening the solution | 5 min |
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
3. `let m = usize::MAX; m + 1` — what happens under `oslings run`, and under `--release`? What would you write instead? <details><summary>Answer</summary>Debug: a panic, `attempt to add with overflow`. Release: silently `0`. `wrapping_add(1)` when wrapping is the intent (a counter, a ring index); `checked_add(1)` when the caller must handle `None`; `saturating_add(1)` when clamping is sane. Plain `+` is for arithmetic you can prove cannot overflow.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

[Rustlings](https://github.com/rust-lang/rustlings): the `03_if` and `04_primitive_types` groups, then a peek ahead at `12_options`. [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/): Chapter 2, "A Basic Calculator" (`if`/`else`, panics, `while` and `for`, overflow, the `wrapping`/`checked`/`saturating` methods).
