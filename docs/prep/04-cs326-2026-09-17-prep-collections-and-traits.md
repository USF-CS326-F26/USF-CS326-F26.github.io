# Prep: Collections and Traits — 06r · 07r

**Session:** Thu Sep 17, 1h45 · **Exercises:** `06r_collections`, `07r_traits` · **Prep time:** ~20 min · **Lecture:** [Week 4 · Collections, Traits, Errors, and Your First Command](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md)

## What you will build

Two small exercises, one idea each. First, a miniature of rv6's process table: a fixed array of `NPROC` slots, filled by the lowest-free-slot rule, searched by pid, and never indexed by a number it has not checked. Second, the kernel's two key abstractions: an output sink with one required method plus a default built on it, and a scheduling policy driven by a shared loop that never learns which policy it holds.

## Concepts you need

- **Array, slice, `Vec`: where the bytes live; slices are the interface** — [Week 4 · Arrays, slices, and `Vec`](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#06r-containers) · [Rust for Systems: Arrays, slices, `Vec`, iteration](../guides/rust-for-systems.md#5-arrays-slices-vec-iteration)
- **Bounds checks; validating an untrusted index at the boundary** — [Week 4 · Arrays, slices, and `Vec`](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#06r-containers)
- **`iter` vs `iter_mut`, `enumerate`, adapters that allocate nothing** — [Week 4 · Loops that read, loops that write](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#06r-iterating) · [Rust for Systems: Iteration](../guides/rust-for-systems.md#iteration)
- **Why `PROCS` is an array, and where `Vec` belongs** — [Week 4 · Why the kernel's tables are arrays](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#06r-fixed)
- **Traits: required and default methods, `impl Trait for Type`** — [Week 4 · A trait: what a type promises](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#07r-traits)
- **Trait bounds, monomorphization, `dyn` dispatch** — [Week 4 · Generic functions and their bounds](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#07r-generics), [Static and dynamic dispatch](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#07r-dispatch), [Count the copies](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#exam-copies) · [Rust for Systems: Static dispatch vs `dyn`](../guides/rust-for-systems.md#static-dispatch-vs-dyn)

## Read before class

| What | Time |
|---|---|
| [Week 4 · This week](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#this-week), then [Thursday · `06r` Arrays, slices, and fixed tables](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#thu-06r), all three sections | 6 min |
| [Week 4 · Thursday · `07r` Traits and generics](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#thu-07r), all three sections | 5 min |
| [Week 4 · For the exam: Count the copies](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#exam-copies). Not needed today; on Midterm 1 | 1 min |
| [Rust for Systems: Iteration](../guides/rust-for-systems.md#iteration), the table, and [Static dispatch vs `dyn`](../guides/rust-for-systems.md#static-dispatch-vs-dyn) | 4 min |

## Mental model

One fixed table, one slice over it, one trait, one bound:

```rust
pub trait Sink { fn put(&mut self, b: u8); }        // one required method, no data

struct Uart;
impl Sink for Uart  { fn put(&mut self, b: u8) { /* store to the UART register */ } }
struct Tally(usize);                                 // stores nothing, counts everything
impl Sink for Tally { fn put(&mut self, _: u8) { self.0 += 1; } }

fn drain<S: Sink>(ring: &[u8], sink: &mut S) {       // any length, any sink
    for &b in ring.iter() { if b != 0 { sink.put(b); } }
}
// static KEYS: [u8; 256];  drain(&KEYS, &mut Uart);  drain(&KEYS[..4], &mut Tally(0));
```

`KEYS` sits in `.bss` before any code runs, so nothing allocates and nothing can fail on the trap path. `&KEYS` becomes a `&[u8]` at the call, so `drain` serves the whole ring or a four-byte window without a copy. The bound is all `drain` may assume, and it is enough: the compiler emits `drain::<Uart>` and `drain::<Tally>`, two direct, inlinable copies, no vtable, no heap.

## Check yourself

1. A function takes `states: &[ProcState]`. Can its body call `states.iter_mut()`? <details><summary>Answer</summary>No. `&[T]` is a shared borrow, read only; `iter_mut` needs `&mut [T]`. The signature decides which iterator you may use.</details>
2. `fn log<S: Sink>(s: &mut S, line: &str)` is called with three sink types. How many copies of `log` exist, and what changes with `&mut dyn Sink`? <details><summary>Answer</summary>Three, one per concrete type (monomorphization), each with `put` resolved at compile time and inlinable. With `dyn Sink`: one copy, an indirect vtable call per `put`, and a sink you can store in a field or a `Vec`.</details>
3. A system call hands the kernel an unchecked index. Why is `table[i]` the wrong first move? <details><summary>Answer</summary>A bad index panics, and a kernel panic halts the machine: a user program would own a denial of service. Check `i` against the length once, at the boundary, and return an error; index freely after that.</details>

## What "done" looks like

`oslings run` is green for both exercises, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 4 · Problem 1: Which loops compile?](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#problem-1) and [Problem 2: Count the copies](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#problem-2) on paper. Then Rustlings (<https://github.com/rust-lang/rustlings>): the `vecs`, `iterators`, `generics`, and `traits` groups. 100 Exercises To Learn Rust (<https://rust-exercises.com/100-exercises/>): chapter 4, *Traits*, and chapter 6, *Ticket Management*. Or start Friday's prep page, [Prep: Errors, and Your First Command](04-cs326-2026-09-18-prep-errors-and-echo.md).
