# Prep: Enums and match — 05r

**Session:** Friday Sep 11, 1h30 · **Exercises:** `05r_enums_match` · **Prep time:** ~30 min · **Lecture:** [Building Your Own Types: Structs, `impl`, `const fn`, and Enums](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md)

## What you will build

The state diagram in §7 of the lecture, turned into code. You are given a `ProcState` enum whose variants carry data (a sleeper remembers its channel), an `Event` enum, and a table of legal transitions. You write the `match` that walks a process along the arrows, answers `None` for any pair not in the table, and lets a wakeup reach only a sleeper on that exact channel. The tests drive one full lifecycle from `Unused` back to `Unused`, confirm a wrong-channel wakeup leaves a sleeper asleep, and confirm an impossible event changes nothing.

## Concepts you need

- **Enums are sum types** — exactly one of a fixed set — [L04 §7](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#7-enums-exactly-one-of-these) · [Rust for Systems §4](../guides/rust-for-systems.md#enums-are-tagged-unions)
- **Variants that carry data** — building them, binding fields back out — [L04 §7](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#variants-that-carry-data) · [Rust for Systems §4](../guides/rust-for-systems.md#variants-can-carry-data)
- **`Option<T>`** — absence with its own type — [L04 §7](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#optiont-no-null) · [Rust for Systems §4](../guides/rust-for-systems.md#optiont)
- **Exhaustive `match`** — arms, `|`, `{ .. }`, `E0004`, the `_` trap — [L04 §8](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#8-match-exhaustiveness-and-guards) · [Rust for Systems §4](../guides/rust-for-systems.md#match-is-exhaustive)
- **Guards, tuple patterns, fall-through** — an `if` on an arm — [L04 §8](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#guards)
- **`if let`** — a one-arm `match` — [L04 §8](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#guards) · [Rust for Systems §4](../guides/rust-for-systems.md#match-is-exhaustive)

## Read before class

| What | Time |
|---|---|
| [L04 §7–§8](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#7-enums-exactly-one-of-these) | 15 min |
| [L04 Practice Problem 5](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#problem-5-tracing-guards-and-fall-through) | 5 min |
| [Rust for Systems §4](../guides/rust-for-systems.md#4-enums-option-exhaustive-match) | 10 min |

## Mental model

A console driver deciding whether a byte from the UART is worth keeping:

```rust
enum Rx { Byte(u8), Overrun, Idle }

fn accept(rx: Rx, room: usize) -> Option<u8> {
    match (rx, room) {
        (Rx::Byte(b), n) if n > 0 && b != 0 => Some(b),   // guard: room, and not a NUL
        (Rx::Byte(_), _) | (Rx::Idle, _)    => None,      // a failed guard lands here
        (Rx::Overrun, _)                    => None,      // its own arm: no `_`
    }
}
if let Some(b) = accept(uart.read(), ring.free()) { ring.push(b); }
```

The tuple pattern tests two values at once. A guard is not an `if` inside the body: when it fails, the `match` keeps looking, so the "no" case is written once, below. Returning `Option<u8>` rather than `u8` with zero meaning "nothing" forces the caller to take it apart. A kernel is mostly this shape: fixed states, fixed events, a table of legal pairs. Add `Rx::Break` and the compiler lists every `match` that has not decided, unless someone hid the variants behind `_`.

## Check yourself

1. A `match` over `ProcState` covers `Unused`, `Runnable`, `Running`, and `Sleeping { .. }`, and nothing else. What does the compiler say, and what is the fix? <details><summary>Answer</summary>`error[E0004]: non-exhaustive patterns: ProcState::Zombie { .. } not covered`. Add a `Zombie { .. }` arm. Do not reach for `_`; it silences the check for every variant ever added.</details>
2. In the mental model, `Rx::Byte(0)` arrives with `room == 5`. Which arm answers, and why not the first? <details><summary>Answer</summary>The first arm's *pattern* matches, but its guard `b != 0` is false, so matching continues; `(Rx::Byte(_), _)` matches and the result is `None`. A failed guard falls through; it never leaves the `match`.</details>
3. Why should a function answering "what state comes next" return `Option<ProcState>` rather than `ProcState` with an extra `Invalid` variant? <details><summary>Answer</summary>`Option<ProcState>` is a different *type*: the caller must unwrap it with `match` or `if let`, so "no legal transition" cannot be mistaken for a real state and stored into a process table slot. An `Invalid` variant is just another value the compiler cannot flag.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Rustlings [`08_enums` and `12_options`](https://github.com/rust-lang/rustlings) drill today's patterns. In [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/), chapter 5 covers enums, `match`, variants with data, `if let`, and `Option`. Or start Thursday's prep page on collections and traits.
