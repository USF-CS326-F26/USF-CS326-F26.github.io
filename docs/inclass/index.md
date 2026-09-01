# In Class

The lecture page makes the argument. This is the part we **run**, on screen,
while you run it too.

Each week's in-class material is a deck plus a small Cargo project of programs
that print addresses, sizes, and error messages. The programs are the point: an
argument about ownership is abstract until you watch `push` move a buffer and
print a different address than it did a line earlier.

Everything lives in the course's
[inclass repository](https://github.com/USF-CS326-F26/inclass). Clone it once
and pull before each session:

```sh
git clone git@github.com:USF-CS326-F26/inclass.git
cd inclass/week02/examples
cargo run --bin 01_scalars
```

Nothing here is graded, and none of it is a substitute for the lecture page or
for the Prep page of the exercise session that follows — both are linked from
the [schedule](../index.md).

---

## Week 02 · September 1 — Rust: Types, Ownership, and Borrowing

[Open the slides](week02-slides.html){ .md-button }

Companion to [L03 Ownership, Borrowing, and Lifetimes](../lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md).
Where the lecture derives the rules, this session runs them: ten programs, one
idea each, and seven programs that must *not* compile.

### The ten programs

Run them in order. Read the printed **addresses**, not just the text.

| Program | The one idea | The line to watch |
|---|---|---|
| `01_scalars` | a value is its bits; `usize` is an address | the PTE decoded from a `u64` |
| `02_compound` | structs, arrays, and enums are plain layouts | `size_of::<Option<&u8>>() == 8` |
| `03_stack_and_heap` | the handle is not the buffer | `push` printing a *new* buffer address |
| `04_move` | a move copies 3 words, not the data | 8 MiB "moved", same pointer afterwards |
| `05_copy_types` | `Copy` XOR `Drop` | two independent `Pte` copies, different addresses |
| `06_drop` | `free()` became a scope | `kfree` lines in reverse declaration order |
| `07_borrow_shared` | many readers, no ownership | three references printing one buffer address |
| `08_borrow_mut` | `&mut` means *exclusive* | `split_at_mut` — two writers, provably disjoint |
| `09_slices` | pointer + length, bounds-checked | one `checksum` over an array, a `Vec`, and a slice |
| `10_how_to_pass` | choosing `T` / `&T` / `&mut T` | the mini `PageAlloc` with `&self` and `&mut self` |

### The seven failures

These are in `broken/` and are deliberately not part of the package, so
`cargo build` still succeeds. Walk all seven, pausing at each:

```sh
./show-errors.sh
./show-errors.sh e0502     # or jump to one
```

| File | Error | The fix |
|---|---|---|
| `e0382_use_after_move.rs` | use of moved value | use the new binding, `clone()`, or borrow |
| `e0499_two_mut_borrows.rs` | two `&mut` at once | sequence them, or `split_at_mut` |
| `e0502_shared_and_mut.rs` | `&` and `&mut` overlap | finish the read first, or copy the value out |
| `e0505_move_while_borrowed.rs` | move while borrowed | use the reference before the move |
| `e0507_move_out_of_index.rs` | move out of a `Vec` index | borrow, `clone()`, or `remove()` |
| `e0596_immutable_borrow.rs` | not declared mutable | add `mut` |
| `e0106_dangling_reference.rs` | missing lifetime | return the value, or borrow from a parameter |

Try to predict each error before it scrolls by, then fix each broken file two
different ways. If a message still does not make sense, run
`rustc --explain E0502` and bring the ones that survive that to the next
session.

**Next:** exercises `02r_ownership` (Thursday) and `03r_borrowing` (Friday).
