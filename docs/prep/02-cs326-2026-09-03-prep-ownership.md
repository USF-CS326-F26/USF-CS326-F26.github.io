# Prep: Ownership — 02r

**Session:** Thursday Sep 3, 1 h 45 min · **Exercises:** `02r_ownership` · **Prep time:** ~25 min · **Lecture:** [Ownership, Borrowing, and Lifetimes](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md)

## What you will build

A physical page allocator modeled by hand from a `Vec<usize>` of free page numbers and move semantics. There is no `&` yet, so each piece takes the whole free list *by value* and hands it back in a tuple: build the list at "boot," hand a page out like `kalloc`, take one back like `kfree`, and return a sentinel page number that can never be real when the list runs dry. One small piece shows that a `String` given to a function must be handed back before the caller can use it. The given tests check that no page is handed out twice, that a returned page becomes free again, and that page numbers survive being passed around while the list does not.

## Concepts you need

- **One owner; drop at the closing brace** — [Lecture §2](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#2-ownership-one-owner-always) · [Guide §1 "The rule"](../guides/rust-for-systems.md#the-rule)
- **What a move is: three words copied, old name dead** — [Lecture §2.1](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#21-what-a-move-actually-is) · [Guide §1 "Moving"](../guides/rust-for-systems.md#moving)
- **Moves across a call; returning a value to give it back** — [Lecture §2.2](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#22-moves-at-function-boundaries) · [Guide "E0382"](../guides/rust-for-systems.md#e0382-use-after-move)
- **`Copy` types: page numbers copy, the list moves** — [Lecture §2.3](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#23-copy-values-that-do-not-move) · [Guide §1 "`Copy` types"](../guides/rust-for-systems.md#copy-types-do-not-move)
- **Drop is where `free()` went** — [Lecture §3](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#3-drop-where-free-went) · [Guide §1 "Drop"](../guides/rust-for-systems.md#drop)
- **`Vec` basics, tuples, shadowing** — [Lecture Problem 1](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#problem-1-trace-ownership-through-the-free-list) · [Guide §5](../guides/rust-for-systems.md#three-ways-to-hold-a-run-of-values)
- **Reading E0382 and the missing-`mut` error** — [Lecture §7](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#7-the-four-errors-you-will-actually-hit) · [Guide "Common compiler errors"](../guides/rust-for-systems.md#common-compiler-errors-and-what-they-actually-mean)

## Read before class

| What | Time |
|---|---|
| Lecture §§1–3 (the bug, ownership, moves, `Copy`, drop) | 12 min |
| Lecture §7, the E0382 row and the reading habits | 3 min |
| Guide §1 Ownership and moves | 6 min |
| Guide §5, "Three ways to hold a run of values" | 3 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

[Rustlings](https://github.com/rust-lang/rustlings): `06_move_semantics`, then `05_vecs` and the tuple exercises in `04_primitive_types`. [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/): chapter 3, the Ownership, Stack, Heap, and Destructors sections; chapter 4, `Copy` and `Drop`. Then start Friday's prep page on borrowing, the fix for every "return it so the caller keeps it" line.
