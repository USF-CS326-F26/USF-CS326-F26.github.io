# Prep: Errors, and Your First Command — 08r · 10c

**Session:** Fri Sep 18, 1h30 · **Exercises:** `08r_errors`, `10c_echo` · **Prep time:** ~20 min · **Lecture:** [Week 4 · Collections, Traits, Errors, and Your First Command](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md)

## What you will build

First, a chain of fallible steps over a toy directory: a scan that reports **absence** with `Option`, a call that turns absence and an over-long name into **failure** with your own error enum, steps glued together with `?`, and a boundary where the `Result` collapses into one Unix-style integer — a byte count, or minus an `errno` number. Second, `echo`, your first command, against the `ulib` façade: arguments in as byte slices, bytes out through `write_all` on fd 1, exit status `0`. The tests check that each bad name yields the right error variant (never a panic), and that `echo` emits byte-exact output for zero, one, several, and empty arguments.

## Concepts you need

- **Absence vs failure: `Option` vs `Result`** — [Week 4 · Absence is not failure](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#08r-absence), [A sentinel or an `Option`](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#exam-sentinel) · [Rust for Systems: Enums, `Option`, exhaustive `match`](../guides/rust-for-systems.md#4-enums-option-exhaustive-match)
- **Your own error enum; `.ok_or()` turns absence into failure** — [Week 4 · An error enum, and where absence becomes failure](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#08r-error-enum)
- **`?`, and where a `Result` becomes a number** — [Week 4 · `?`, and where a `Result` becomes a number](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#08r-question-mark)
- **A command: argv, fd 1, exit status, one façade** — [Week 4 · A command: words in, bytes out, a number back](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#10c-command), [One file, two targets: the `ulib` seam](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#10c-seam)
- **Arguments are bytes, not strings** — [Week 4 · A command: words in, bytes out, a number back](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#10c-command) · [ulib guide: Portability rules a command must follow](../guides/ulib-and-commands.md#portability-rules-a-command-must-follow)
- **`write_all`, never bare `write`** — [Week 4 · `write_all`, and the short write](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#10c-write-all) · [ulib guide: The complete API surface](../guides/ulib-and-commands.md#the-complete-api-surface)
- **A separator is not a terminator** — [Week 4 · A command: words in, bytes out, a number back](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#10c-command), its "one thing to get right" box

## Read before class

| What | Time |
|---|---|
| [Week 4 · Friday · `08r` Errors as values](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#fri-08r), all three sections | 5 min |
| [Week 4 · Friday · `10c` Your first command](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#fri-10c), all three sections | 4 min |
| [Week 4 · For the exam: A sentinel or an `Option`](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#exam-sentinel). Not needed today; on Midterm 1 | 1 min |
| [ulib guide: The complete API surface](../guides/ulib-and-commands.md#the-complete-api-surface) and [Portability rules a command must follow](../guides/ulib-and-commands.md#portability-rules-a-command-must-follow) | 5 min |

## Mental model

Waking a process by pid — not a filesystem, same three layers:

```rust
enum ProcError { NoSuchPid, NotSleeping }

fn slot_of(table: &[Proc], pid: u32) -> Option<usize> { /* scan */ }

fn wakeup(table: &mut [Proc], pid: u32) -> Result<(), ProcError> {
    let i = slot_of(table, pid).ok_or(ProcError::NoSuchPid)?;   // absence becomes failure HERE
    if table[i].state != State::Sleeping { return Err(ProcError::NotSleeping); }
    table[i].state = State::Runnable;
    Ok(())
}

fn sys_wakeup(table: &mut [Proc], pid: u32) -> i64 {           // the boundary: one integer
    match wakeup(table, pid) { Ok(()) => 0, Err(ProcError::NoSuchPid) => -3, Err(ProcError::NotSleeping) => -22 }
}
```

The scan states a fact; the middle layer decides, and may use `?` only because it returns `Result`; the edge collapses everything into the one register a user program can receive. A kernel has no exception to throw and nothing to unwind into, so every system call you write from `50k` on has this shape.

## Check yourself

1. A directory scan finds no entry for a name. `Option` or `Result`, and where is "missing means the call failed" decided? <details><summary>Answer</summary>The scan returns `Option` — absence is not an error there. The caller that promised to open something converts with `.ok_or(SomeVariant)`; that one line is where the policy lives.</details>
2. Printing items `x`, an empty item, and `y` with a space **separator**: how many spaces, and what would "a space after every item" give instead? <details><summary>Answer</summary>Two, giving `x  y` — the empty item still counts. "After every item" is a terminator and leaves a trailing space. `n` items need `n − 1` separators; the newline goes once, after the loop.</details>
3. Why `write_all` and never `write`, when the tests pass either way? <details><summary>Answer</summary>`write` may accept fewer bytes than offered and only says so in its count. The host harness accepts everything, so bare `write` is green on your laptop and loses bytes the first time a real device takes fewer. `write_all` loops until every byte is out.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 4 · Problem 3: Trace the exits](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#problem-3) and [Problem 4: Short writes by the numbers](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md#problem-4) on paper. Then Rustlings `error_handling` and `options` groups: <https://github.com/rust-lang/rustlings>. 100 Exercises To Learn Rust, chapter 5 (enums, fallibility, `Result`, `?`): <https://rust-exercises.com/100-exercises/>. Or start Thursday's prep page, [Prep: cat](05-cs326-2026-09-24-prep-cat.md).
