# Prep: Collections and Traits — 06r · 07r

**Session:** Thu Sep 17, 1h45 · **Exercises:** `06r_collections`, `07r_traits` · **Prep time:** ~40 min · **Lecture:** [Arrays, Slices, `Vec`, and Fixed Tables](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md) · [Traits, Generics, and the `ulib` Façade](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md)

## What you will build

Two small exercises, one idea each. First, a miniature of rv6's process table: a fixed array of `NPROC` slots, filled by the lowest-free-slot rule, searched by pid, and never indexed by a number it has not checked. Second, the kernel's two key abstractions: an output sink with one required method plus a default built on it, and a scheduling policy driven by a shared loop that never learns which policy it holds.

## Concepts you need

- **Array, slice, `Vec`: where the bytes live; slices are the interface** — [Collections §1](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md#1-three-ways-to-hold-n-things) · [Collections §2](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md#2-what-a-slice-really-is) · [Rust for Systems §5](../guides/rust-for-systems.md#5-arrays-slices-vec-iteration)
- **Bounds checks; validating an untrusted index at the boundary** — [Collections §3](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md#3-indexing-and-bounds-checks)
- **`iter` vs `iter_mut`, `enumerate`, adapters that allocate nothing** — [Collections §4](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md#4-iterating) · [Rust for Systems: Iteration](../guides/rust-for-systems.md#iteration)
- **Why `PROCS` is an array, and where `Vec` belongs** — [Collections §5](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md#5-the-kernel-argument-why-procs-is-an-array) · [Collections §7](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md#7-where-vec-does-belong)
- **Traits: required and default methods, `impl Trait for Type`** — [Traits §2](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#2-traits-a-contract-between-types) · [Traits §2.2](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#22-default-methods)
- **Trait bounds, monomorphization, `dyn` dispatch** — [Traits §3](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#3-generics-and-trait-bounds) · [Traits §4](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#4-monomorphization-what-the-compiler-actually-emits) · [Rust for Systems: Static dispatch vs `dyn`](../guides/rust-for-systems.md#static-dispatch-vs-dyn)

## Read before class

| What | Time |
|---|---|
| Collections §1–§4 (arrays, slices, indexing, iterating) | 12 min |
| Collections §5 and §7 (why `PROCS` is an array; where `Vec` belongs) | 8 min |
| Traits §2–§4 and §5.1 (contracts, bounds, dispatch, `Scheduler`) | 14 min |
| Rust for Systems: the Iteration table; Static dispatch vs `dyn` | 5 min |

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

`oslings run` is green for both exercises, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Thursday 11:59 pm** and submit again.

## If you finish early

Rustlings (<https://github.com/rust-lang/rustlings>): the `vecs`, `iterators`, `generics`, and `traits` groups. 100 Exercises To Learn Rust (<https://rust-exercises.com/100-exercises/>): chapter 4, *Traits*, and chapter 6, *Ticket Management*. Or start Friday's prep page on errors and `echo`.
