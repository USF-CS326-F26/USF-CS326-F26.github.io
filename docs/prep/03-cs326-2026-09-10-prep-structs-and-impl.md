# Prep: Structs, impl, and const fn — 04r

**Session:** Thu Sep 10, 1h45 · **Exercises:** `04r_structs_impl` · **Prep time:** ~30 min · **Lecture:** [Week 3 · Structs, `impl`, Enums, and `match`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md)

## What you will build

Three types, under plain `cargo test`. A half-open region of physical memory that knows its extent, is made from a page count, and can list every whole page inside itself — `kinit` in miniature, on top of a `const fn` that rounds an address up to a page boundary the way xv6's `PGROUNDUP` does. An Sv39 page table entry, a newtype around a 64-bit word whose `const fn` methods pack a physical page number above ten flag bits and pull both back out. And a `PageGuard`: one page taken off that free list, exclusively borrowing the list while it is held, and put back by its `Drop` at the closing brace — 02r's `give_back` with the remembering removed, and the `SpinLockGuard` of exercise 37k with the lock swapped for a page. The three chain together. One given test already proves the newtype is eight bytes and a `#[repr(C)]` struct keeps source order; the rest check that your packing matches the hardware layout, round-trips an address, evaluates at compile time, and that a page comes back exactly once.

## Concepts you need

- **Structs and struct literals** — [Week 3 · Structs and `impl`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-impl) · [Rust for Systems: Structs and `impl` blocks](../guides/rust-for-systems.md#structs-and-impl-blocks)
- **Methods vs associated functions: `.` vs `::`** — [Week 3 · Structs and `impl`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-impl) · [Rust for Systems: Structs and `impl` blocks](../guides/rust-for-systems.md#structs-and-impl-blocks)
- **The three receivers and `#[derive(Copy)]`** — [Week 3 · The three selves, and `derive`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-selves) · [Rust for Systems: `Copy` types do not move](../guides/rust-for-systems.md#copy-types-do-not-move)
- **Newtypes, `#[repr(transparent)]`, and bit packing** — [Week 3 · The newtype, and bits in a word](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-newtype) · [Rust for Systems: The newtype pattern](../guides/rust-for-systems.md#the-newtype-pattern)
- **`const fn` and const contexts** — [Week 3 · Settled before run time: `const fn`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-const-fn) · [Rust for Systems: `const fn`](../guides/rust-for-systems.md#const-fn)
- **`Drop`, RAII, and the guard pattern** — [Week 3 · `Drop`, and the guard](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-drop), [The guard's destination](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#deeper-spinlock) · [Rust for Systems: Drop](../guides/rust-for-systems.md#drop) · [The guard pattern](../guides/rust-for-systems.md#the-guard-pattern)
- **`#[repr(C)]`: layout as a contract** — [Week 3 · Settled before run time: `#[repr(C)]`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-repr-c), [Why assembly needs `#[repr(C)]`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#exam-repr-c) · [Rust for Systems: `#[repr(C)]` and why layout matters](../guides/rust-for-systems.md#reprc-and-why-layout-matters)

## Read before class

| What | Time |
|---|---|
| [Week 3 · This week](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#this-week), then [Thursday · `04r` Structs, methods, and the guard](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#thu-04r) through [The newtype, and bits in a word](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-newtype) | 8 min |
| [Week 3 · Settled before run time: `const fn` and `#[repr(C)]`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-const-fn) and [`Drop`, and the guard](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#04r-drop) | 6 min |
| [Week 3 · For the exam: Why assembly needs `#[repr(C)]`](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md#exam-repr-c). Not needed today; on Midterm 1 | 1 min |
| [Rust for Systems: Structs, `impl`, methods, `const fn`, newtypes, `#[repr(C)]`](../guides/rust-for-systems.md#3-structs-impl-methods-const-fn-newtypes-reprc) | 7 min |
| [Rust for Systems: The guard pattern](../guides/rust-for-systems.md#the-guard-pattern) | 2 min |

## Mental model

A Unix wait status is one 16-bit word: exit code in bits 15..8, signal number in bits 7..0. Give the word a type and the fields methods:

```rust
#[repr(transparent)]
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct WaitStatus(pub u16);

impl WaitStatus {
    pub const fn exited(code: u16) -> WaitStatus { WaitStatus(code << 8) } // no self
    pub const fn code(self) -> u16 { self.0 >> 8 }                         // by value
    pub const fn signaled(self) -> bool { self.0 & 0xff != 0 }
}

const OK: WaitStatus = WaitStatus::exited(0); // compile time
```

Pack by shifting each field into its slot and ORing; unpack by shifting back and ANDing with a mask. `WaitStatus::exited(3)` goes through the type with `::` because no value exists yet; `st.code()` goes through a dot, and `st.signaled()` after it still compiles because `Copy` copies two bytes rather than moving `st`. Being `const fn`, `OK` is a literal in the binary. Kernel values that are easy to confuse wear a type this way (a page-table entry, a block of saved registers), so an entry cannot be passed where an address was wanted, and tables of them exist before any code runs.

## Check yourself

1. In `let s = Slot::empty(); s.is_free();`, which call is a method and which an associated function? <details><summary>Answer</summary>`Slot::empty()` is associated: called through the type with `::`; no value exists yet. `s.is_free()` is a method: called with a dot on a value, so its first parameter is a form of `self`.</details>
2. A by-value `self` method on an eight-byte struct without `Copy` is called twice on one variable. What happens? <details><summary>Answer</summary>The first call moves the value; the second is `E0382`, use after move. Deriving `Copy` makes the call copy eight bytes instead: `Copy` makes assignment stop moving.</details>
3. What does each need: (a) a static array of 64 process records, correct before the first instruction; (b) a saved-register struct that assembly reads at "base plus 8"? <details><summary>Answer</summary>(a) A `const fn` to build one record: the linker lays out a `static`, and nothing has run to fill it. (b) `#[repr(C)]`, or Rust may reorder fields and offset 8 stops being the stack pointer. It fails silently: the symptom is a garbage jump on a context switch.</details>
4. A type holds a page taken from a free list and puts it back in `Drop`. Why can it never `#[derive(Copy)]`, and what breaks if it could? <details><summary>Answer</summary>`error[E0184]`: a type with a destructor cannot be `Copy`. With `Copy`, every bitwise copy is a full value of its own; with `Drop`, every value runs its release when it dies. Together they would run the release once per copy — the page goes back on the free list twice, is handed to two callers, and both write to it. That is the double free from 02r, which is where the rule comes from.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

- Rustlings ([github.com/rust-lang/rustlings](https://github.com/rust-lang/rustlings)): the `structs` group, then `primitive_types` for tuples.
- 100 Exercises To Learn Rust ([rust-exercises.com/100-exercises](https://rust-exercises.com/100-exercises/)): chapter 3, "Ticket v1," then chapter 4, "Traits," for `Copy` and derive.
- Start reading Friday's prep page, [Enums and match](03-cs326-2026-09-11-prep-enums-and-match.md).
