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

---

## Week 03 · September 8 — Structs, Enums, and Fixed Tables

[Open the slides](week03-slides.html){ .md-button }

Companion to [L04 Structs, `impl`, and `const fn`](../lectures/02-cs326-2026-09-03-structs-impl-and-const-fn.md)
and [L05 Arrays, Slices, and Fixed Tables](../lectures/03-cs326-2026-09-08-collections-slices-and-fixed-tables.md).
Two exercises come due this week, so the first three parts of the session aim
squarely at them: twelve programs, one idea each, and seven that must *not*
compile.

### The twelve programs

Run them in order. Read the printed **sizes and offsets**, not just the text.

| Program | The one idea | The line to watch |
|---|---|---|
| `01_structs` | a struct is its fields, back to back | `size_of::<Console>()` with no header |
| `02_impl_and_self` | `.` is a method, `::` is an associated function | `Stats::new()` beside `s.record_read()` |
| `03_derive_and_copy` | `Copy` makes assignment stop *moving* | the same by-value method called twice |
| `04_newtype` | same bits, a genuinely different type | an alias accepting the swap a newtype rejects |
| `05_const_fn` | arithmetic the compiler already did | a `static` table with no start-up loop |
| `06_repr_c` | layout is a promise only `#[repr(C)]` makes | `flag` at offset 10, then at offset 0 |
| `07_drop_guard` | release became a closing brace | "release" printed on a path with no call |
| `08_enums` | exactly one of these, and nothing else | `size_of::<Option<&u8>>() == 8` |
| `09_match` | the compiler lists what you forgot | the careful column vs. the `_` column |
| `10_option` | absence with a type of its own | `Ok(1)` and `Err(-1)` side by side |
| `11_slices` | pointer + length, bounds-checked | `&[u8]` is 16 bytes, `&[u8; 8]` is 8 |
| `12_tables_and_iterators` | a fixed table, searched lazily | the closure running twice, not eight times |

### The seven failures

These are in `broken/` and are deliberately not part of the package, so
`cargo build` still succeeds. Walk all seven, pausing at each:

```sh
./show-errors.sh
./show-errors.sh e0004     # or jump to one
```

| File | Error | The fix |
|---|---|---|
| `e0004_non_exhaustive.rs` | a variant was added; a `match` was not | add the arm, or `_` and lose the check |
| `e0308_newtype_mismatch.rs` | a raw integer where a newtype belongs | wrap it, or unwrap it visibly |
| `e0382_method_moved_it.rs` | a by-value `self` consumed the value | derive `Copy`, or take `&self` |
| `e0184_copy_with_drop.rs` | `Copy` on a type with a destructor | drop one of the two |
| `e0015_non_const_in_const.rs` | a non-`const fn` in a const context | make the callee `const fn` |
| `e0507_move_out_of_self.rs` | moving a field out of `&self` | return a borrow, or `clone()` |
| `e0080_const_index.rs` | a constant index past the end | fix the index, or use `get()` |

Try to predict each error before it scrolls by, then fix each broken file two
different ways. If a message still does not make sense, run
`rustc --explain E0004` and bring the ones that survive that to the next
session.

### Two worked examples

Each exercise has a companion project in the same repository — the same shape
as the exercise, in a different domain, complete and passing:

```sh
cd week03/04r_structs_impl_example && cargo run --bin basic_struct && cargo test
cd week03/05r_enums_match_example  && cargo run --bin basic_enum   && cargo test
```

Read `04r_structs_impl_example/src/lib.rs` beside the exercise skeleton. Every
item has a twin there; if you can say why the twins are the same shape, the
exercise is mostly reading comprehension.

**Next:** exercises `04r_structs_impl` (Thursday) and `05r_enums_match` (Friday).
