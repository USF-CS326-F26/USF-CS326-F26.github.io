# In Class

The lecture page makes the argument. This is the part we **run**, on screen,
while you run it too.

Each week's in-class material is a small Cargo project of programs that print
addresses, sizes, and error messages. Weeks 2 to 4 also have a deck of their
own; from week 5 on, the Tuesday deck is the one on the lecture page. The programs are the point: an
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

Each week also has a **Code and output** page: every program beside the output
it printed, one section per row, with each output line linked to the `println!`
that printed it. Clicking a section's number copies a link to that section, so a
link your instructor sends you opens exactly the rows being discussed. On those
pages you can also edit a program and run it. Pressing
**Run** sends that code to the [Rust Playground](https://play.rust-lang.org/),
which the classroom network allows; **Revert** puts the original back. Your
exercise work still belongs in your own repository, where the test harness can
see it.

From week 6 on, the programs are bare-metal RISC-V and run under QEMU, which
no browser can do. Those pages show the output captured under QEMU, with no
editor; run the programs yourself with `cargo run`, the same QEMU line
`oslings run` uses.

Nothing here is graded, and none of it is a substitute for the lecture page or
for the Prep page of the exercise session that follows — both are linked from
the [schedule](../index.md).

---

## Week 02 · September 1 — Rust: Types, Ownership, and Borrowing

[Open the slides](week02-slides.html){ .md-button } [Code and output](week02-examples.html){ .md-button }

Companion to the [Week 2 lecture](../lectures/02-cs326-2026-09-01-ownership-and-borrowing.md).
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

[Open the slides](week03-slides.html){ .md-button } [Code and output](week03-examples.html){ .md-button }

Companion to the [Week 3 lecture](../lectures/03-cs326-2026-09-08-structs-enums-and-match.md);
its last two programs, on slices and fixed tables, look ahead to the
[Week 4 lecture](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md).
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

---

## Week 04 · September 15 — Collections, Traits, Errors, and Bytes

[Open the slides](week04-slides.html){ .md-button } [Code and output](week04-examples.html){ .md-button }

Companion to the [Week 4 lecture](../lectures/04-cs326-2026-09-15-collections-traits-errors-and-echo.md).
Four exercises come due this week, so each of the four parts of the session
aims at one of them: fourteen programs, one idea each, and nine that must
*not* compile.

### The fourteen programs

Run them in order. Read the printed **counts, sizes, and error messages**, not
just the text.

| Program | The one idea | The line to watch |
|---|---|---|
| `01_array_slice_vec` | one function, three containers | `count_free(&arr)` and `count_free(&v)`: the same `&` |
| `02_iter_mut_and_enumerate` | `*c = None` writes into the array | the `*` |
| `03_slot_search` | an index, or nothing — never −1 | `position(..)` returning `Option<usize>` |
| `04_adapters_and_closures` | three words, three types | `.flatten().copied().collect::<Vec<u16>>()` |
| `05_trait_required_default` | the default was never written by any implementer | `puts` has a body in the trait; no `impl` mentions it |
| `06_generics_and_bounds` | one body, three names | `type_name::<U>()` printed from inside the generic |
| `07_static_vs_dyn` | a fat pointer is two words | `size_of::<&dyn Uart>() = 16` |
| `08_option_vs_result` | absence is a fact, failure is a decision | `first_free(free).ok_or(AllocError::OutOfFrames)` |
| `09_error_enum_and_question_mark` | each `?` is a different exit | the three `?`s in `load` |
| `10_errno_boundary` | the collapse happens in exactly one place | the `match` in `sys_read` |
| `11_bytes_vs_strings` | a string is bytes plus a checked promise | `str::from_utf8(..)` returns a `Result` |
| `12_argv_and_write_all` | the slice is re-pointed, not copied | `buf = &buf[n..]` |
| `13_dispatch_at_run_time` | who names the type: the call site, or the input | `fn open(&mut self, k: Kind) -> &mut dyn Uart` |
| `14_generic_struct_and_guard` | one definition, a type for every T | `impl<T> Lock<T>` beside `impl<T: Uart> Lock<T>` |

One program, `08_option_vs_result`, builds with a single warning on purpose —
the warning is the demo.

### The nine failures

These are in `broken/` and are deliberately not part of the package, so
`cargo build` still succeeds. Walk all nine, pausing at each:

```sh
./show-errors.sh
./show-errors.sh e0506     # or jump to one
```

| File | Error | The fix |
|---|---|---|
| `e0506_assign_while_iterating.rs` | assigning `table[i]` inside `table.iter()` | `iter_mut` and `*slot = …`, or an index loop |
| `e0596_iter_mut_behind_shared_ref.rs` | `iter_mut` on a `&[T]` parameter | change the parameter, not the loop |
| `e0046_missing_required_method.rs` | overrode the default, skipped the required | supply `put`; delete the override |
| `e0599_no_bound_no_method.rs` | a trait method on an unbounded type parameter | add `S: Sink` |
| `e0038_not_dyn_compatible.rs` | a generic method, then `&mut dyn Trait` | `where Self: Sized`, or take a slice, or go generic |
| `e0107_one_type_per_call_site.rs` | `FdTable<S>` used without its type argument | name it, go generic too, or `&'a mut dyn Sink` |
| `e0392_type_parameter_never_used.rs` | a generic struct that never holds its `T` | hold one in a field, `PhantomData<T>`, or drop the parameter |
| `e0308_option_is_not_result.rs` | returned `find`'s `Option` from `lookup` | `.ok_or(e)`, or the two-arm `match` |
| `e0277_question_mark_needs_result.rs` | `?` in a function returning `i64` | `match` at the boundary; `?` only below it |

Try to predict each error before it scrolls by, then fix each broken file two
different ways. If a message still does not make sense, run
`rustc --explain E0506` and bring the ones that survive that to the next
session.

### Four worked examples

Each exercise has a companion project in the same repository — the same shape
as the exercise, in a different domain, complete and passing:

```sh
cd week04/06r_collections_example && cargo run --bin basic_table   && cargo test
cd week04/07r_traits_example      && cargo run --bin basic_trait   && cargo test
cd week04/08r_errors_example      && cargo run --bin basic_result  && cargo test
cd week04/10c_echo_example        && cargo run --bin basic_command -- a b && cargo test
```

Read each `src/lib.rs` beside the exercise skeleton. Every item has a twin
there; if you can say why the twins are the same shape, the exercise is mostly
reading comprehension. The `10c` companion is host-only, on a local façade with
`ulib`'s exact signatures — it shows the ceremony, and it cannot be copied into
`commands/`.

**Next:** exercises `06r_collections` and `07r_traits` (Thursday), `08r_errors`
and `10c_echo` (Friday).

---

## Week 05 · September 22 — Streams of Bytes: cat, wc, and grep

[Code and output](week05-examples.html){ .md-button } [Lecture slides](../lectures/05-cs326-2026-09-22-cat-wc-and-grep-slides.html){ .md-button }

Companion to the [Week 5 lecture](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md).
Each program runs one example from the page: a descriptor table, a short
read, a buffer that decides how often you trap, state carried across reads,
and a line that straddles two of them. Eleven programs and six that must *not*
compile. Every one takes no arguments and no input, so each also runs on the
Playground from its Code and output page.

### The eleven programs

| Program | The one idea | The line to watch |
|---|---|---|
| `01_fd_numbers` | a descriptor is the lowest free slot | the `open` after `close(4)` returning 4, not 6 |
| `02_short_reads` | a short read is normal; only 0 ends it | `buf[3..6]` still saying `"lo\n"` |
| `03_buffer_size_counts_calls` | the buffer's size sets how many times you trap | 2,048 reads beside 1,048,576 |
| `04_read_loop_tr` | listen to both counts, read's and write's | the bare `write` that lost 10 bytes |
| `05_exit_status` | a later success does not erase a failure | `status = 1; // only ever set, never cleared` |
| `06_bytes_chars_str` | `len` counts bytes, not characters | `"año".len() = 4` beside `.chars().count() = 3` |
| `07_state_across_chunks` | state the caller keeps survives the end of a read | the two `<- wrong` rows |
| `08_lines_in_a_fixed_buffer` | an unfinished line slides to the front | `read(fd, &mut buf[6..]) -> 10` |
| `09_while_let` | call, match, and stop at the first miss | `Some("")` for a blank line |
| `10_fenceposts` | the last start is `len - k`, and only `..=` reaches it | `(0..3).contains(&3) = false` for `log` in `syslog` |
| `11_stop_early` | what a program does not read costs nothing | 1,024 bytes read out of 10,000,000,000 |

### The six failures

```sh
./show-errors.sh
./show-errors.sh e0499     # or jump to one
```

| File | Error | The fix |
|---|---|---|
| `e0499_line_held_across_next_line.rs` | a line held across the next `next_line` | finish with each line first, or copy out what you need |
| `e0502_read_buf_while_lines_has_it.rs` | reading `buf[0]` while `lines` has the buffer | read through the line, or after the last use of `lines` |
| `e0506_write_buf_while_lines_has_it.rs` | writing `buf[5]` while `lines` has the buffer | edit a copy, or write after the last use of `lines` |
| `e0277_lines_is_not_an_iterator.rs` | `for line in lines` | `while let Some(line) = lines.next_line()` |
| `e0308_byte_is_not_a_char.rs` | a `u8` compared with the char `'\t'` | `b'\t'`, a byte literal |
| `e0599_chars_on_bytes.rs` | `.chars()` on a `&[u8]` | stay in bytes, or `from_utf8` first |

### The worked example

`week05/12c_wc_vec_example` is the obvious `wc`, in plain `std`: read
everything, split it, count the pieces. It is the version rv6 cannot run, and
its README says why the exercise streams instead:

```sh
cd week05/12c_wc_vec_example && cargo test && cargo run -- src/main.rs Cargo.toml
```

**Next:** exercises `11c_cat` (Thursday), `12c_wc` and `13c_grep` (Friday), and
the extra-credit `14c_head`.

---

## Week 06 · September 29 — Below Rust: Assembly, unsafe, and no_std

[Code and output](week06-examples.html){ .md-button } [Lecture slides](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std-slides.html){ .md-button }

Companion to the [Week 6 lecture](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md).
The first week off the host: every program is a bare-metal RISC-V binary that
QEMU loads at `0x8000_0000` with no firmware and no OS, and it reaches the world
only through device registers. Thirteen programs, grouped by the exercise they
serve, and seven that must *not* compile.

```sh
cd inclass/week06/examples
cargo run --bin 01_registers      # boots it under QEMU; Ctrl-A then x quits if it hangs
```

You need what `oslings doctor` already checks: the `riscv64gc-unknown-none-elf`
target and QEMU. The Code and output page shows what each program printed under
QEMU on the instructor's machine; it has no **Edit and run**.

### The thirteen programs

| Program | The one idea | The line to watch |
|---|---|---|
| `01_registers` | `sp` and `ra` are ordinary registers you can read | `ra = main + 0x…`: right after the `call` |
| `02_calling_assembly` | `extern "C"` is the whole bridge, and the signature is a promise | `fn find_byte(s: *const u8, b: u8) -> *const u8` |
| `03_lb_vs_lbu` | `lb` sign-extends, `lbu` zero-extends | `0xe9: lb … = -23   lbu … = 233` |
| `04_repr_c` | `repr(C)` is what makes the assembly's offsets true | `span_end = 0x80000007` after a field was inserted |
| `05_add_wraps` | the hardware `add` drops the carry; Rust's `+` checks | `… len 0x1) = 0x0` |
| `06_prologue_and_s0` | a caller saves `ra`; a user of `s0` saves `s0` | `keeper(rude) -> s1 = 0x63` |
| `07_a_ret_that_lands_elsewhere` | `ret` goes wherever `ra` says, on whatever stack `sp` says | `landing: nobody called me` |
| `08_mmio_clock` | a device register is an address, read through a raw pointer | `MTIMECMP.add(3) = 0x2004018` |
| `09_volatile_matters` | plain device accesses get merged, dropped, or hoisted | `the UART received: B` |
| `10_unsafe_does_not_turn_off` | `unsafe` unlocks five operations and turns nothing off | `pub fn end_of(s: &Span) -> u64` |
| `11_what_core_still_has` | `no_std` removes the OS, not the language | `write!` into a 48-byte buffer on the stack |
| `12_who_calls_main` | `no_main`: the program names its own first instruction | `_entry 0x80000000` |
| `13_the_panic_handler` | every `no_std` program says what a panic does, once | `fn panic(info: &PanicInfo) -> !` |

### The seven failures

They compile for the same bare-metal target, one at a time:

```sh
./show-errors.sh
./show-errors.sh e0133     # or jump to one
```

| File | Error | The fix |
|---|---|---|
| `e0463_forgot_no_std.rs` | the target has no `std` to link | `#![no_std]`, with the `!` |
| `e0601_forgot_no_main.rs` | rustc wants a `main` nobody will call | `#![no_main]`, not an empty `fn main` |
| `panic_handler_required.rs` | a `no_std` program with nowhere for a panic to go | one `#[panic_handler]` returning `!` |
| `e0152_two_panic_handlers.rs` | "exactly one" holds across the whole program | delete one |
| `e0133_raw_deref_needs_unsafe.rs` | reading through a raw pointer outside `unsafe` | `unsafe { read_volatile(MTIME) }`, or an `unsafe fn` |
| `e0308_unsafe_keeps_types.rs` | a `u64` register read into a `u32` | take the register's type, or say `as u32` |
| `e0433_vec_needs_alloc.rs` | `Vec` is in `alloc`, not `core` | a fixed array and a count, until there is a heap |

**Next:** exercises `20a_asm_bridge` (Thursday), `21r_unsafe_bridge` and
`30k_kernel_basics` (Friday).
