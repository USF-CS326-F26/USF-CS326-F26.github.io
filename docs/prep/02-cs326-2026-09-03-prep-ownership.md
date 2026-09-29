# Prep: Ownership — 02r

**Session:** Thu Sep 3, 1h45 · **Exercises:** `02r_ownership` · **Prep time:** ~25 min · **Lecture:** [Week 2 · Ownership and Borrowing](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md)

## What you will build

A physical page allocator modeled by hand from a `Vec<usize>` of free page numbers and move semantics. There is no `&` yet, so each piece takes the whole free list *by value* and hands it back in a tuple: build the list at "boot," hand a page out like `kalloc`, take one back like `kfree`, and return a sentinel page number that can never be real when the list runs dry. One small piece shows that a `String` given to a function must be handed back before the caller can use it. The given tests check that no page is handed out twice, that a returned page becomes free again, and that page numbers survive being passed around while the list does not.

## Concepts you need

- **One owner; drop at the closing brace** — [Week 2 · No `free()`, and no collector](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-owner) · [Rust for Systems: The rule](../guides/rust-for-systems.md#the-rule)
- **What a move is: three words copied, old name dead** — [Week 2 · A move copies the handle, not the buffer](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-moves) · [Rust for Systems: Moving](../guides/rust-for-systems.md#moving)
- **Moves across a call; returning a value to give it back** — [Week 2 · Moving through a call, and handing it back](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-calls) · [Rust for Systems: `E0382`, use after move](../guides/rust-for-systems.md#e0382-use-after-move)
- **`Copy` types: page numbers copy, the list moves** — [Week 2 · `Copy` types stay put](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-copy), [What survives a move](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#exam-moves) · [Rust for Systems: `Copy` types do not move](../guides/rust-for-systems.md#copy-types-do-not-move)
- **Drop is where `free()` went** — [Week 2 · No `free()`, and no collector](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-owner) · [Rust for Systems: Drop](../guides/rust-for-systems.md#drop)
- **`Vec` basics, tuples, shadowing** — [Week 2 · Moving through a call, and handing it back](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-calls), [Problem 1: What survives a move](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#problem-1) · [Rust for Systems: Three ways to hold a run of values](../guides/rust-for-systems.md#three-ways-to-hold-a-run-of-values)
- **Reading E0382 and the missing-`mut` error** — [Week 2 · A move copies the handle, not the buffer](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#02r-moves), [The errors you will actually hit](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#03r-errors) · [Rust for Systems: Common compiler errors](../guides/rust-for-systems.md#common-compiler-errors-and-what-they-actually-mean)

## Read before class

| What | Time |
|---|---|
| [Week 2 · This week](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#this-week), then [Thursday · `02r` Ownership and moves](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#thu-02r), all four sections | 7 min |
| [Week 2 · For the exam: What survives a move](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#exam-moves). Not needed today; on Midterm 1 | 1 min |
| [Week 2 · The errors you will actually hit](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#03r-errors), the E0382 and E0596 rows | 1 min |
| [Rust for Systems: Ownership and moves](../guides/rust-for-systems.md#1-ownership-and-moves) | 6 min |
| [Rust for Systems: Three ways to hold a run of values](../guides/rust-for-systems.md#three-ways-to-hold-a-run-of-values) | 3 min |

## Mental model

A function that takes an owned value, changes it, and gives it back, plus a number riding along:

```rust
fn stamp(mut msg: String, n: u32) -> (String, u32) {
    msg.push('!');                 // legal only because the parameter says `mut`
    (msg, n + 1)                   // hand the String back
}

let msg = String::from("boot");
let n = 7;
let (msg, total) = stamp(msg, n);  // moved in, moved back out into a new `msg` (shadowing)
assert_eq!(n, 7);                  // `u32` is Copy: the original survives
assert_eq!((msg.as_str(), total), ("boot!", 8));
```

While `stamp` runs it is the *only* owner of that `String`. The kernel's allocator needs that: while "hand out a page" runs it owns the whole free list, so the page it returns cannot still be on it. Ownership is that invariant, checked by the compiler.

## Check yourself

1. After `let b = a;` where `a: String`, what happens at run time, and what at compile time? <details><summary>Answer</summary>Run time: three machine words (pointer, length, capacity) are copied; the heap buffer is untouched. Compile time: `a` is marked dead; naming it again is E0382, a use-after-free caught early.</details>
2. Which of these are `Copy`: `usize`, `bool`, `String`, `Vec<usize>`, `(usize, usize)`? <details><summary>Answer</summary>`usize`, `bool`, and the tuple; not `String` or `Vec<usize>`. The line is not size but resources: a type with cleanup (`Drop`) cannot be `Copy`, or cleanup would run once per copy.</details>
3. A function takes a `Vec<usize>` by value and calls `.push` on it; the caller needs the list afterward. Without `&`, what must it do? <details><summary>Answer</summary>Write `mut` before the parameter name (or `.push` is E0596), and return the `Vec`, usually in a tuple. The caller rebinds with `let (list, x) = f(list);`, shadowing the dead `list`.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 2 · Problem 1: What survives a move](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#problem-1) and [Problem 2: `Copy` or not](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md#problem-2) on paper (Midterm 1 material). [Rustlings](https://github.com/rust-lang/rustlings): `06_move_semantics`, then `05_vecs` and the tuple exercises in `04_primitive_types`. [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/): chapter 3, the Ownership, Stack, Heap, and Destructors sections; chapter 4, `Copy` and `Drop`. Then start Friday's prep page, [Prep: Borrowing and Lifetimes](02-cs326-2026-09-04-prep-borrowing.md), on borrowing: the fix for every "return it so the caller keeps it" line.
