# Prep: Errors, and Your First Command — 08r · 10c

**Session:** Fri Sep 18, 1h30 · **Exercises:** `08r_errors` `10c_echo` · **Prep time:** ~40 min · **Lecture:** [Traits, Generics, and the `ulib` Façade](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md) · [Buffers, Bytes, and Line-Oriented I/O](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md)

## What you will build

First, a chain of fallible steps over a toy directory: a scan that reports **absence** with `Option`, a call that turns absence and an over-long name into **failure** with your own error enum, steps glued together with `?`, and a boundary where the `Result` collapses into one Unix-style integer — a byte count, or minus an `errno` number. Second, `echo`, your first command, against the `ulib` façade: arguments in as byte slices, bytes out through `write_all` on fd 1, exit status `0`. The tests check that each bad name yields the right error variant (never a panic), and that `echo` emits byte-exact output for zero, one, several, and empty arguments.

## Concepts you need

- **Absence vs failure: `Option` vs `Result`** — [L06 §6.1](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#61-option-for-absence-result-for-failure) · [Rust for Systems §4](../guides/rust-for-systems.md#4-enums-option-exhaustive-match)
- **Your own error enum; `.ok_or()` is the policy line** — [L06 §6.2](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#62-your-own-error-type)
- **`?`, and where a `Result` becomes a number** — [L06 §6.3](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#63-and-the-desugaring-you-should-know) · [L06 §6.5](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#65-where-a-result-becomes-a-number)
- **A command: argv, fd 1, exit status, one façade** — [L07 §1](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#1-the-narrowest-waist-in-computing) · [L06 §7](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#7-ulib-one-seam-two-implementations)
- **Arguments are bytes, not strings** — [L07 §5](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#5-bytes-char-and-utf-8) · [ulib guide, Portability rules](../guides/ulib-and-commands.md#portability-rules-a-command-must-follow)
- **`write_all`, never bare `write`** — [L07 §3](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#3-short-writes-and-why-write_all-exists) · [ulib guide, The complete API surface](../guides/ulib-and-commands.md#the-complete-api-surface)
- **A separator is not a terminator** — [L07 §7](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#7-five-commands-one-idea)

## Read before class

| What | Time |
|---|---|
| L06 §6 Errors as Values (§6.1–6.3, §6.5) | 15 min |
| L06 §7.3 Testing through the seam | 3 min |
| L07 §1, §3, §5 (last two paragraphs), §7 (`echo` paragraph) | 12 min |
| ulib guide: The complete API surface, Portability rules | 10 min |

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
2. Printing items `x`, `` (empty), `y` with a space **separator**: how many spaces, and what would "a space after every item" give instead? <details><summary>Answer</summary>Two, giving `x  y` — the empty item still counts. "After every item" is a terminator and leaves a trailing space. `n` items need `n − 1` separators; the newline goes once, after the loop.</details>
3. Why `write_all` and never `write`, when the tests pass either way? <details><summary>Answer</summary>`write` may accept fewer bytes than offered and only says so in its count. The host harness accepts everything, so bare `write` is green on your laptop and truncates on rv6 in December. `write_all` loops until every byte is out.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Monday 11:59 pm** and submit again.

## If you finish early

Rustlings `error_handling` and `options` groups: <https://github.com/rust-lang/rustlings>. 100 Exercises To Learn Rust, chapter 5 (enums, fallibility, `Result`, `?`): <https://rust-exercises.com/100-exercises/>. Then start Thursday's prep page on `cat`.
