# Prep: Borrowing and Lifetimes — 03r

**Session:** Fri Sep 4, 1h30 · **Exercises:** `03r_borrowing` · **Prep time:** ~30 min · **Lecture:** [Ownership, Borrowing, and Lifetimes](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md)

## What you will build

Thursday gave every value one owner; today you lend values instead of giving
them away. You will finish a small crate, tested with plain `cargo test` on
your laptop, in which readers take shared slices, a writer takes an exclusive
slice and changes the caller's array in place, one function returns a borrowed
slice and needs a lifetime to say whose, and a small struct holds a `&mut` to
a counter. The tests check the values and the shape of the borrows: shared
borrows of one array coexist, an exclusive borrow ends when its function
returns, and the counter is readable directly again once the struct goes out
of scope.

## Concepts you need

- **`&` shared vs `&mut` exclusive** — [Lecture §4.2](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#42-the-two-kinds) · [Rust for Systems, Two kinds of borrow](../guides/rust-for-systems.md#two-kinds-of-borrow)
- **Slices: a pointer and a length, no copy** — [Lecture §4.1](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#41-slices-are-the-systems-shape) · [Rust for Systems, Slices are borrows](../guides/rust-for-systems.md#slices-are-borrows)
- **Aliasing XOR mutation** — [Lecture §5](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#5-aliasing-xor-mutation) · [Rust for Systems, The aliasing rule](../guides/rust-for-systems.md#the-aliasing-rule)
- **Borrows end at their last use** — [Lecture §5.2](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#52-borrows-end-at-their-last-use) · [Rust for Systems, The aliasing rule](../guides/rust-for-systems.md#the-aliasing-rule)
- **Lifetimes, `'a`, and a struct that holds a reference** — [Lecture §6](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#6-lifetimes) · [Rust for Systems, Lifetimes](../guides/rust-for-systems.md#lifetimes) · [The guard pattern](../guides/rust-for-systems.md#the-guard-pattern)
- **E0499, E0502, E0106** — [Lecture §7](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#7-the-four-errors-you-will-actually-hit) · [Rust for Systems, Common compiler errors](../guides/rust-for-systems.md#common-compiler-errors-and-what-they-actually-mean)

## Read before class

| What | Time |
|---|---|
| [Lecture §4–§7](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#4-borrowing-lending-without-giving-away) | 20 min |
| [Rust for Systems §2](../guides/rust-for-systems.md#two-kinds-of-borrow) | 10 min |

## Mental model

A borrow is a loan with a receipt. The owner keeps the value; the receipt says
who may look, whether anyone may write, and when the loan is over.

```rust
let mut line = [b'h', b'i', 0, 0];       // `line` is the owner
let head = &line[..2];                   // shared loan: pointer + length, no copy
let zeros = count_zeros(head);           // last use of `head`: the loan ends here
upcase(&mut line);                       // exclusive loan, begins and ends on this line
struct Cursor<'a> { text: &'a [u8], at: usize }
let cur = Cursor { text: &line, at: 0 }; // `cur` may not outlive `line`
println!("{zeros} {}", cur.text[cur.at]);
```

It compiles because no two loans overlap illegally: the shared loan ends before
the exclusive one starts, and `Cursor<'a>` records that it points into
something it does not own. Kernels run on this shape: pages, disk blocks, and
console buffers travel as slices, and the spinlock guard in `37k_spinlocks` is
a struct holding a reference, so "touch the data only while you hold the lock"
becomes a compiler check.

## Check yourself

1. `let a = &mut page; let b = &mut page; use_both(a, b);` is rejected; with `&page` it is fine. Why? <details><summary>Answer</summary>Aliasing XOR mutation: any number of shared borrows may coexist, but a `&mut` must be the only live path to the value. Two live `&mut` borrows is E0499.</details>
2. `fn shorter(a: &str, b: &str) -> &str` does not compile. What is missing, and what does adding `<'a>` to it promise? <details><summary>Answer</summary>The result borrows from an input and the signature does not say which (E0106). `'a` states a relationship: both inputs live at least through region `'a`, and the result is valid no longer than that.</details>
3. A struct holds a `&mut u64` to a variable `n`. While that struct value is alive, may the function that owns `n` read `n` directly? <details><summary>Answer</summary>No: the exclusive borrow makes the struct the only path to `n`, so a direct read is E0502. After the struct's last use the borrow is over and `n` is usable directly again.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Monday, Sep 7, 11:59 pm** and submit again.

## If you finish early

- [Rustlings](https://github.com/rust-lang/rustlings): `06_move_semantics`, then `16_lifetimes`.
- [100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/): chapter 3, the ownership and references sections; chapter 6, the slices sections.
- Lecture [Practice Problem 4](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#problem-4-find-the-borrow-error-fix-it-without-cloning) and [Problem 5](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md#problem-5-choose-the-right-lifetime-signature): same skills, no tests to lean on.
