# Prep: Structs, impl, and const fn — 04r

**Session:** Thu Sep 10, 1h45 · **Exercises:** `04r_structs_impl` · **Prep time:** ~35 min · **Lecture:** [Building Your Own Types: Structs, `impl`, `const fn`, and Enums](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md)

## What you will build

Two of the lecture's types, under plain `cargo test`: a half-open region of physical memory that knows its extent and is made from a page count, and the Sv39 page table entry of Lecture §4, a newtype around a 64-bit word whose `const fn` methods pack a physical page number above ten flag bits and pull both back out. One given test already proves the newtype is eight bytes and a `#[repr(C)]` struct keeps source order. The tests check that your packing matches the hardware layout, round-trips an address, and evaluates at compile time.

## Concepts you need

- **Structs and struct literals** — [Lecture §2](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#2-structs-naming-a-bundle-of-values) · [Rust for Systems §3](../guides/rust-for-systems.md#structs-and-impl-blocks)
- **Methods vs associated functions: `.` vs `::`** — [Lecture §3](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#3-impl-giving-a-type-behavior) · [Rust for Systems §3](../guides/rust-for-systems.md#structs-and-impl-blocks)
- **The three receivers and `#[derive(Copy)]`** — [Lecture §3, "The three selves"](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#the-three-selves) · [Rust for Systems §1](../guides/rust-for-systems.md#copy-types-do-not-move)
- **Newtypes, `#[repr(transparent)]`, and bit packing** — [Lecture §4](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#4-the-newtype-pattern) · [Rust for Systems §3](../guides/rust-for-systems.md#the-newtype-pattern)
- **`const fn` and const contexts** — [Lecture §5](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#5-const-fn-arithmetic-the-compiler-does-for-you) · [Rust for Systems §3](../guides/rust-for-systems.md#const-fn)
- **`#[repr(C)]`: layout as a contract** — [Lecture §6](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md#6-reprc-when-something-other-than-rust-reads-your-struct) · [Rust for Systems §3](../guides/rust-for-systems.md#reprc-and-why-layout-matters)

## Read before class

| What | Time |
|---|---|
| Lecture §2–§4 | 15 min |
| Lecture §5–§6 | 10 min |
| Rust for Systems §3 | 10 min |

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

Pack by shifting each field into its slot and ORing; unpack by shifting back and ANDing with a mask. `WaitStatus::exited(3)` goes through the type with `::` because no value exists yet; `st.code()` goes through a dot, and `st.signaled()` after it still compiles because `Copy` copies two bytes rather than moving `st`. Being `const fn`, `OK` is a literal in the binary. Every kernel word (entry, process id, saved registers) wears a type this way, so an entry cannot be passed where an address was wanted, and tables of them exist before any code runs.

## Check yourself

1. In `let s = Slot::empty(); s.is_free();`, which call is a method and which an associated function? <details><summary>Answer</summary>`Slot::empty()` is associated: called through the type with `::`; no value exists yet. `s.is_free()` is a method: called with a dot on a value, so its first parameter is a form of `self`.</details>
2. A by-value `self` method on an eight-byte struct without `Copy` is called twice on one variable. What happens? <details><summary>Answer</summary>The first call moves the value; the second is `E0382`, use after move. Deriving `Copy` makes the call copy eight bytes instead: `Copy` makes assignment stop moving.</details>
3. What does each need: (a) a static array of 64 process records, correct before the first instruction; (b) a saved-register struct that assembly reads at "base plus 8"? <details><summary>Answer</summary>(a) A `const fn` to build one record: the linker lays out a `static`, and nothing has run to fill it. (b) `#[repr(C)]`, or Rust may reorder fields and offset 8 stops being the stack pointer. It fails silently: the symptom is a garbage jump on a context switch.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Thursday 11:59 pm** and submit again.

## If you finish early

- Rustlings ([github.com/rust-lang/rustlings](https://github.com/rust-lang/rustlings)): the `structs` group, then `primitive_types` for tuples.
- 100 Exercises To Learn Rust ([rust-exercises.com/100-exercises](https://rust-exercises.com/100-exercises/)): chapter 3, "Ticket v1," then chapter 4, "Traits," for `Copy` and derive.
- Start reading Friday's prep page, [Enums and match](03-cs326-2026-09-11-prep-enums-and-match.md).
