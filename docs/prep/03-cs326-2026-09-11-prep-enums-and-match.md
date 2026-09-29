# Prep: Enums and match — 05r

**Session:** Friday Sep 11, 1h30 · **Exercises:** `05r_enums_match` · **Prep time:** ~25 min · **Lecture:** [Week 3 · Structs, `impl`, Enums, and `match`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md)

## What you will build

A process's state diagram, turned into code. You are given a `ProcState` enum whose variants carry data (a sleeper remembers its channel), an `Event` enum, and a table of legal transitions. You write the `match` that walks a process along the arrows, answers `None` for any pair not in the table, and lets a wakeup reach only a sleeper on that exact channel. The tests drive one full lifecycle from `Unused` back to `Unused`, confirm a wrong-channel wakeup leaves a sleeper asleep, and confirm an impossible event changes nothing.

## Concepts you need

- **Enums are sum types** — exactly one of a fixed set — [Week 3 · An enum is one of a fixed set](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-enums) · [Rust for Systems: Enums are tagged unions](../guides/rust-for-systems.md#enums-are-tagged-unions)
- **Variants that carry data** — building them, binding fields back out — [Week 3 · An enum is one of a fixed set](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-enums), [`match`, and the arms you cannot forget](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-match) · [Rust for Systems: Variants can carry data](../guides/rust-for-systems.md#variants-can-carry-data)
- **`Option<T>`** — absence with its own type — [Week 3 · `Option`: an answer that may be missing](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-option), [A sentinel, or `Option`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#exam-sentinel) · [Rust for Systems: `Option<T>`](../guides/rust-for-systems.md#optiont)
- **Exhaustive `match`** — arms, `|`, `{ .. }`, `E0004`, the `_` trap — [Week 3 · `match`, and the arms you cannot forget](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-match), [What `_` costs](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#exam-wildcard) · [Rust for Systems: `match` is exhaustive](../guides/rust-for-systems.md#match-is-exhaustive)
- **Guards, tuple patterns, fall-through** — an `if` on an arm — [Week 3 · Guards, and matching two values](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-guards)
- **`if let`** — a one-arm `match` — [Week 3 · `Option`: an answer that may be missing](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#05r-option) · [Rust for Systems: `match` is exhaustive](../guides/rust-for-systems.md#match-is-exhaustive)

## Read before class

| What | Time |
|---|---|
| [Week 3 · Friday · `05r` Enums and `match`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#fri-05r), all four sections | 7 min |
| [Week 3 · Problem 5: Trace guards and fall-through](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#problem-5) | 5 min |
| [Week 3 · For the exam: A sentinel, or `Option`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#exam-sentinel) and [What `_` costs](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#exam-wildcard). Not needed today; on Midterm 1 | 2 min |
| [Rust for Systems: Enums, `Option`, exhaustive `match`](../guides/rust-for-systems.md#4-enums-option-exhaustive-match) | 6 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Rustlings [`08_enums` and `12_options`](https://github.com/rust-lang/rustlings) drill today's patterns. In [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/), chapter 5 covers enums, `match`, variants with data, `if let`, and `Option`. Or start next Thursday's prep page, [Collections and traits](04-cs326-2026-09-17-prep-collections-and-traits.md).
