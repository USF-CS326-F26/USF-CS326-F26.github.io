# Week 4 · Collections, Traits, Errors, and Your First Command

> **Thu Sep 17** `06r_collections`, `07r_traits` · **Fri Sep 18** `08r_errors`, `10c_echo`
>
> Taught Tue Sep 15. **Essentials** is what Thursday and Friday assume.
> **Going deeper** is optional and is not on the exam.

[Slides](04-cs326-2026-09-15-collections-traits-errors-and-echo-slides.html){ .md-button }
[Thursday prep](../prep/04-cs326-2026-09-17-prep-collections-and-traits.md){ .md-button }
[Friday prep](../prep/04-cs326-2026-09-18-prep-errors-and-echo.md){ .md-button }
[In-class slides](../inclass/week04-slides.html){ .md-button }

## This week { #this-week }

In `36k` one scheduler loop runs any policy, and in `40k` every filesystem
call can fail and must say how. In December your kernel runs commands you
wrote in September. This week builds the Rust under all three.

[Midterm 1](../assignments/midterm-1.md) (Thu Oct 15) covers this week's
scope: arrays, slices, `Vec` and fixed tables; traits, generics and
monomorphization; `Result`, `?` and error enums; and why `write_all` exists.

By Friday night you have a table that never allocates, code written once
against a trait, an error path that ends in one integer, and `echo`.

---

## Essentials { #essentials }

### Thursday · `06r` Arrays, slices, and fixed tables { #thu-06r }

In `34k` the kernel keeps its processes in a table of 64 slots, and in `50k`
each process keeps its open files in another. `06r_collections` asks why each
is an array.

#### Arrays, slices, and `Vec` { #06r-containers }

An **array**, `[T; N]`, is one block of N values, and N is written into its
type; `[0; 4]` builds four zeros. A **slice**, `&[T]` or `&mut [T]`, is a view
into elements stored elsewhere, carried as two words: where they start and how
many. The count travels with the view, so `busiest` takes four harts or four
hundred:

```rust
const NHART: usize = 4;
let ticks = [0u64; NHART];      // one counter per hart; nothing allocates
fn busiest(ticks: &[u64]) -> u64 { … }
busiest(&ticks);                // the whole array, as a slice
busiest(&ticks[1..3]);          // harts 1 and 2 only
```

Read `&ticks[1..3]` as "elements 1 and 2, borrowed in place". A **`Vec<T>`**
owns a growable block on the **heap**, memory requested at run time:
`Vec::new()` starts empty, `push` appends, and `&v` lends a slice.

Rust checks every index against the length: inside `busiest`, `ticks[9]`
panics with "index out of bounds: the len is 4 but the index is 9", and a
constant `ticks[9]` on the array does not even compile. In rv6 a panic stops
the machine, so a number from user space is checked against `len()` first.

#### Loops that read, loops that write { #06r-iterating }

`iter()` yields a shared `&T` per element, enough to look. `iter_mut()` yields
an exclusive `&mut T`, and `*` reaches the element behind it:

```rust
fn age(ticks: &mut [u64]) {
    for t in ticks.iter_mut() {
        *t /= 2;                // halve the counter t points at
    }
}
```

Read `*t /= 2` as "change the element, not the reference". A `&[u64]`
parameter only lends reading, so `iter_mut` on it fails with E0596,
"cannot borrow `*ticks` as mutable, as it is behind a `&` reference".
`.enumerate()` adds a counter from 0 beside each element.

Iterator **adapters** take a **closure**, an unnamed function written
`|args| body` that may use the variables around it:

```rust
let limit = 100;
let first = ticks.iter().position(|&t| t > limit);           // Option<usize>
let hot = (0..NHART).filter(|&h| ticks[h] > limit).count();  // usize
```

Read `|&h| ticks[h] > limit` as "a test on one index, reading `ticks` and
`limit` from outside". `position` answers with an index or `None`, never −1.

> **The one thing to get right:** ``error[E0506]: cannot assign to `ticks[_]`
> because it is borrowed``, at `ticks[0] += *t` inside
> `for t in ticks[1..].iter()`, with `ticks: &mut [u64]`. The iterator's borrow
> covers the whole table, even slot 0, until the loop ends: while it lives,
> the table is reachable only through it.

#### Why the kernel's tables are arrays { #06r-fixed }

rv6's process table, `PROCS`, is a `static` array of 64 slots, for three
reasons:

1. **No heap exists yet.** The table is needed long before `38k` adds a
   heap, and a `static` array needs none: the linker gives it a fixed place,
   in `.bss`.
2. **The trap path must not allocate.** Interrupts and system calls touch the
   table, and an allocation there could fail with nobody to tell, or wait on
   a lock the interrupted code holds.
3. **A hard limit fails honestly.** The 65th `fork` gets an error on the
   spot, and a test can provoke it. A growing `Vec` fails inside the
   allocator, at whichever call next needs memory.

On a host, with an allocator underneath, `Vec` is fine.

### Thursday · `07r` Traits and generics { #thu-07r }

In `36k` the scheduler runs whatever policy it is handed, and in `46k` a shell
command prints without knowing where its bytes go. Both call methods on a
value whose type they never learn; `07r_traits` practices that.

#### A trait: what a type promises { #07r-traits }

A **trait** is a contract: a type that signs it must supply certain methods.
A method declared with `;` in place of a body is **required**; one the trait
fills in itself is a **default**, and may call the required ones:

```rust
pub trait Clock {
    fn now(&mut self) -> u64;                   // required: no body
    fn since(&mut self, start: u64) -> u64 {    // default
        self.now() - start
    }
}
```

Read `since` as "whatever `now` means for this type, minus `start`". A type
signs up in a second kind of `impl` block:

```rust
pub struct Stepper { pub t: u64, pub step: u64 }    // a clock for tests
impl Clock for Stepper {
    fn now(&mut self) -> u64 { self.t += self.step; self.t }
}
```

Read `impl Clock for Stepper` as "Stepper keeps Clock's promise". It writes
`now` and inherits `since`. (`&mut self`
lets a clock change when read.) Leave `now` out and rustc refuses with E0046,
"not all trait items implemented, missing: `now`".

#### Generic functions and their bounds { #07r-generics }

A **generic** function names a placeholder type, such as `C`, filled in at
each call. Left alone, the body can do almost nothing with a `C`: it must
compile for types not yet written. A **trait bound** narrows the
placeholder:

```rust
pub fn deadline<C: Clock>(clock: &mut C, budget: u64) -> u64 {
    clock.now() + budget
}
```

Read `<C: Clock>` as "`C` is some type that keeps `Clock`'s promise", and
every caller must pass such a type. `where C: Clock` and
`clock: &mut impl Clock` say the same. Each parameter takes its own bound, so
`fn race<A: Clock, B: Clock>` can mix two clock types.

> **The one thing to get right:** ``error[E0599]: no method named `now` found
> for mutable reference `&mut C` in the current scope``, with the help line
> "items from traits can only be used if the type parameter is bounded by the
> trait". rustc checks a generic body once, before any caller exists, so only
> calls the bound promises pass.

#### Static and dynamic dispatch { #07r-dispatch }

rustc emits one copy of `deadline` per type actually used, such as
`deadline::<Stepper>`, and each copy calls its `now` directly. That is
**monomorphization**, or **static dispatch**: it costs code size, not time.

The alternative is a **trait object**, `&mut dyn Clock`: a **fat pointer** to
the value and to its type's **vtable**, a compiler-built table of its methods.
One variable can then hold whichever clock the program picks at run time:

```rust
pub struct Frozen(pub u64);                          // a clock stopped at .0
impl Clock for Frozen { fn now(&mut self) -> u64 { self.0 } }
let (mut f, mut s) = (Frozen(100), Stepper { t: 0, step: 10 });
let clock: &mut dyn Clock = if paused { &mut f } else { &mut s };
```

Without `: &mut dyn Clock`, rustc says E0308, "`if` and `else` have
incompatible types". rv6's shell passes one `&mut dyn Out` to every command.

| | `<C: Clock>`, `impl Clock` | `&mut dyn Clock` |
|---|---|---|
| Method found | at compile time | at run time, in the vtable |
| Copies of the code | one per type used | one |
| One variable, either type, picked at run time | no | yes |

### Friday · `08r` Errors as values { #fri-08r }

In `40k` a filesystem call can fail eight ways, and each failure must reach
the program that asked. `08r_errors` builds that path.

#### Absence is not failure { #08r-absence }

An exception unwinds to a handler, and a system call has none above it: it
runs mid-trap, with no caller frames, and a panic halts the machine. So
failure comes back as a value, in one of two enums:

```rust
enum Option<T>    { Some(T), None }     // absence: nothing, and that's fine
enum Result<T, E> { Ok(T),   Err(E) }   // failure: E says what went wrong
```

Which hart first passed the limit? Perhaps none: an answer, not an error, so
`Option<usize>`. A packet too short to decode? That call failed, and the
caller needs the reason: `Result`.

Drop a `Result` unread and rustc warns, "unused `Result` that must be used":
the type carries `#[must_use]`. `let _ = …;` records that you dropped it on
purpose.

#### An error enum, and where absence becomes failure { #08r-error-enum }

Choose `E` yourself: an enum with a variant for each reason the call can
fail:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HdrError { TooShort, BadMagic }
```

Callers branch on the reason, not a number, with patterns such as
`Err(HdrError::TooShort)`. Add a third variant later, and every `match` that
misses it fails with E0004, "non-exhaustive patterns". `unwrap()` hands over
the `Ok` value or panics: fine in tests, not in a kernel.

`pkt.get(0..2)` answers `Option`: a packet may simply be short, and `get`
reports that without judging. `.ok_or(e)` makes it a failure, keeping a
present value as `Ok` and swapping `None` for `Err(e)`:

```rust
let magic = pkt.get(0..2).ok_or(HdrError::TooShort);
```

Read `pkt.get(0..2)` as "the first two bytes, if there are two". `get` cannot
know this caller needs both; the `.ok_or` line says so, and names the failure
`TooShort`. Return `pkt.get(2).copied()` where a `Result<u8, HdrError>` is due
and rustc says E0308, "expected `Result<u8, HdrError>`, found `Option<u8>`".

#### `?`, and where a `Result` becomes a number { #08r-question-mark }

Put `?` after a `Result`. An `Ok(v)` becomes plain `v` and the line carries
on; an `Err(e)` ends the function on the spot, returning `Err(e)`:

```rust
pub fn version(pkt: &[u8]) -> Result<u8, HdrError> {
    let magic = pkt.get(0..2).ok_or(HdrError::TooShort)?;
    if magic != b"RV" { return Err(HdrError::BadMagic); }
    let v = pkt.get(2).ok_or(HdrError::TooShort)?;
    Ok(*v)
}
```

Read each `?` as "or leave now, carrying this error"; longhand, it is a
`match` whose `Err` arm returns.

Types stop at the trap: the user program finds one integer in `a0`, so
the kernel converts its `Result` once, in the function that answers the call.
Zero and up is success; negative is failure. Linux returns minus an `errno`
code, such as −22 for `EINVAL`; rv6 answers every failure with −1.

> **The one thing to get right:** ``error[E0277]: the `?` operator can only be
> used in a function that returns `Result` or `Option` …``, at a `?` in a
> function returning `i64`. `?` is an early `return Err(e)`, and a bare
> integer has no `Err` side for it to leave through.

### Friday · `10c` Your first command { #fri-10c }

In December `oslings ship` rebuilds your commands to run at your own rv6
shell's prompt. `10c_echo` is the first.

#### A command: words in, bytes out, a number back { #10c-command }

The shell cuts the line you type at the spaces, runs the program named by the
first piece, and passes every piece, that name included, as **`argv`**;
**`argc`** counts them:

```text
$ sort -r names.txt
argv[0] = "sort"    argv[1] = "-r"    argv[2] = "names.txt"    argc = 3
```

A **command** answers in two ways: bytes on **standard output**, file
descriptor 1, and one small integer, its **exit status**, where 0 means it
worked.

Nobody checks that an argument is valid text: `exec` copies raw bytes, so
ulib's `Args::get` answers `Option<&[u8]>`. A **byte-string literal**, `b"-r"`,
has type `&[u8; 2]` and fits wherever such a slice is expected; the plain
`"-r"` is a `&str`, rejected with E0308, "expected `&[u8]`, found `&str`".

> **The one thing to get right:** a test fails on two strings that look
> identical, and `assert_eq!`'s quotes show a blank just before one `\n`.
> `PATH` puts `:` only *between* directories: a **separator**. A text file puts
> `\n` *after* every line: a **terminator**. A list's output follows exactly
> one rule, and an empty item keeps its place: `/bin::/usr/bin` has three
> entries.

#### `write_all`, and the short write { #10c-write-all }

`write(fd, bytes)` is a request, and its answer is a count that may be smaller
than what you offered. A nearly full disk, or a signal that arrives mid-write,
can take 4 of your 10 bytes and return `Ok(4)`, with no error.
`ulib::write_all` asks again, re-pointing its slice past what went out:

```text
write_all(1, b"hello, os\n")    10 bytes; the device takes at most 4 per call
  write -> Ok(4)   "hell"       6 left
  write -> Ok(4)   "o, o"       2 left
  write -> Ok(2)   "s\n"        0 left: write_all returns Ok(())
```

Read `Ok(())` as "all of it": there is no partial success. A `write` that
returns 0 would spin that loop forever, so `write_all` makes it an error. The
test harness takes every byte in one call, so a bare `write` passes every test
and breaks on the first short write.

#### One file, two targets: the `ulib` seam { #10c-seam }

A command calls only **`ulib`**, a **façade**: one small API, two
implementations. Built for your laptop, each call goes to the host; built for
`riscv64gc-unknown-none-elf`, it is an `ecall` into rv6. The
`#[cfg(target_os = "none")]` that picks lives inside `ulib`, so your command
never chooses a backend itself.

rv6 sets the terms: no heap, an image of at most 64 KiB, and only bytes.
[The portability rules](../guides/ulib-and-commands.md#portability-rules-a-command-must-follow)
list the substitutes.

### For the exam { #exam }

*Not needed on Thursday or Friday. On Midterm 1.*

**A sentinel or an `Option`** · *Midterm 1.* A **sentinel** is an ordinary
value of the return type that means "no answer", such as C's `-1` or a null
pointer. It works only if no real answer can equal it. C's `getchar()` returns
an `int` so that `EOF`, −1, lies outside the bytes 0–255. Store the result in
a `char` and the sentinel breaks: byte `0xFF` looks like end of file, or,
where `char` is unsigned, as on RISC-V, end of file never arrives.
`Option<u8>` puts "no byte" outside the bytes by construction, and the
compiler makes every caller handle `None`. rv6 keeps a few sentinels from
xv6, such as the null pointer `kalloc` returns when memory runs out. Practice
Set 1 Problem 3 (a) asks this about address 0 for "not mapped":
[week 3](03-cs326-2026-09-08-structs-enums-and-match.md#exam-sentinel) works
that case, safe because rv6's RAM starts at `0x8000_0000`.
{ #exam-sentinel }

**Count the copies** · *Midterm 1.* Monomorphization emits one copy of a
generic function per distinct list of type arguments actually used. Calls do
not add copies: a hundred calls with `Stepper` share one. Unused combinations
cost nothing: `race` called with three of the four possible pairs of two clock
types gets three copies, and `(Frozen, Stepper)` is not `(Stepper, Frozen)`. A
`dyn` parameter adds no copies, because `dyn Clock` is one type; the choice
moves into the vtable, and every call pays an indirect jump. Expect a generic
function, its call sites, and "how many, and what changes with `dyn`?";
[Problem 2](#problem-2) has this shape.
{ #exam-copies }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday or Friday, and nothing here is on
the exam.*

### Fat pointers, by the byte { #deeper-fat }

A pointer takes a second word when its target's type leaves something
unknown:

| Type | Bytes | What it holds |
|---|---|---|
| `&u64` | 8 | an address |
| `&[u64; 4]` | 8 | an address; the 4 is in the type |
| `&[u64]` | 16 | an address and a length |
| `&mut dyn Clock` | 16 | an address and a vtable pointer |
| `Vec<u64>` | 24 | a heap pointer, a length and a capacity |
| `[u64; 4]` | 32 | the four values themselves |

`[u64]` alone is **unsized**: it can exist only behind a pointer that knows
its length.

### What `ticks[i]` compiles to { #deeper-bounds }

`rustc -O` for `riscv64gc-unknown-none-elf` turns
`fn tick_of(ticks: &[u64], i: usize) -> u64 { ticks[i] }` into:

```asm
tick_of:                    # a0 = address, a1 = length, a2 = i
    bgeu a2, a1, .LBB3_2    # i >= len, unsigned: go panic
    slli a2, a2, 3          # i * 8
    add  a0, a0, a2
    ld   a0, 0(a0)
    ret
.LBB3_2:                    # ...then call core::panicking::panic_bounds_check
```

The fat pointer arrives in `a0` and `a1`, and the check is one compare and a
rarely taken branch. It is unsigned, so an index
computed from a negative number looks huge and fails too. For a `&[u64; 4]`
the compare is against the constant 3, and a `for t in ticks.iter()` loop has
no bounds check at all.

C checks nothing: `ticks[9]` loads whatever lies 72 bytes in, and
out-of-bounds writes still rank near the top of the CWE list.

### Adapters are lazy { #deeper-lazy }

An adapter is a small struct wrapped around the iterator before it, and it
does nothing until something pulls. In
`ticks.iter().map(|&t| t * 2).position(|d| d > 50)`, `position` asks `map` for
one item, and `map` asks `iter` for one tick. On `[0, 20, 45, 3]` the answer
is `Some(2)` after three pulls; the fourth tick is never read. No list of
doubled ticks ever exists, which is why adapters are legal in a kernel with no
heap.

`collect` must build a container, and must be told which, as in
`collect::<Vec<u64>>()`.

### The vtable, up close { #deeper-vtable }

Calling `now` through a `&mut dyn Clock`, compiled for RISC-V:

```asm
deadline_dyn:               # a0 = data pointer, a1 = vtable, a2 = budget
    ...                     # save ra and s0; s0 = budget
    ld   a1, 24(a1)         # the vtable's slot for now
    jalr a1                 # an indirect call: nothing to inline
    add  a0, a0, s0
```

A vtable holds the type's drop function, size and alignment at offsets 0, 8
and 16, then one slot per method: `now` at 24, and the default `since` at 32.
Linux's `struct file_operations` is the same table built by hand in C.

Not every trait can become `dyn`. Add a method with its own type parameter,
such as `fn now_as<T: From<u64>>(&mut self) -> T`, and `&mut dyn Clock` fails
with E0038, "the trait `Clock` is not dyn compatible". A vtable has one slot
per method, and a generic method would need one per `T`.

### `?` converts: `From` and layered errors { #deeper-from }

`?` hides one more step. Its `Err` arm is `return Err(From::from(e))`, so the
error may change type on the way out. Give the caller a richer error type,
and say how to build one from a `HdrError`:

```rust
pub struct BootError { pub stage: u8, pub cause: HdrError }
impl From<HdrError> for BootError {
    fn from(cause: HdrError) -> BootError { BootError { stage: 1, cause } }
}
```

Now a function returning `Result<u8, BootError>` may write `version(pkt)?`,
and a short packet comes out as
`Err(BootError { stage: 1, cause: HdrError::TooShort })`.
Without the `impl`, rustc says E0277, "`?` couldn't convert the error to
`BootError`".

### Why `target_os`, and not a Cargo feature { #deeper-target-os }

`ulib` could pick its backend with `#[cfg(feature = "rv6")]` and a
`--features rv6` flag. That fails two ways. Forget the flag when building for
RISC-V, and the host backend compiles for a machine with no `std`: the errors
name `std`, never the flag. And Cargo unifies features, so one
crate that enables `rv6` enables it for every crate, host tests included.
`target_os` comes from the `--target` flag itself, so the backend cannot
disagree with the machine. Features should add abilities, never choose
between alternatives.

### Practice problems { #problems }

#### Problem 1: Which loops compile? { #problem-1 }

Say whether each numbered line compiles, and give the error code of any that
does not.

```rust
fn tally(ticks: &[u64], log: &mut Vec<u64>) {
    for t in ticks.iter() { log.push(*t); }              // 1
    for t in ticks.iter_mut() { *t = 0; }                // 2
    for (i, t) in log.iter().enumerate() {
        if *t > 9 { log[i] = 9; }                        // 3
    }
    for t in log.iter_mut() { *t += 1; }                 // 4
    let big = ticks.iter().filter(|&&t| t > 5).count();  // 5
}
```

<details markdown="1">
<summary>Click to reveal solution</summary>

- **1 compiles.** `ticks` is only read, and `log` is a different value,
  borrowed mutably.
- **2 fails: E0596.** `ticks` arrived as `&[u64]`, read-only, and `iter_mut`
  needs `&mut`. The fix is in the signature, not the loop.
- **3 fails: E0502.** `log.iter()` holds a shared borrow for the whole loop,
  and `log[i] = 9` on a `Vec` needs a mutable one. On a slice the same line is
  E0506.
- **4 compiles.** It writes through each element's own `&mut`, the way line 3
  should have.
- **5 compiles.** `filter` passes its closure a `&&u64`, and the pattern
  `&&t` peels off both references.

</details>

#### Problem 2: Count the copies { #problem-2 }

With `Clock`, `Stepper` and `Frozen` as in [Essentials](#07r-traits):

```rust
fn deadline<C: Clock>(clock: &mut C, budget: u64) -> u64 { clock.now() + budget }
fn race<A: Clock, B: Clock>(a: &mut A, b: &mut B) -> bool { a.now() < b.now() }
fn deadline_dyn(clock: &mut dyn Clock, budget: u64) -> u64 { clock.now() + budget }
```

It calls them with `s1` and `s2` as `Stepper`s and `f` as a `Frozen`:

```rust
deadline(&mut s1, 5);  deadline(&mut s2, 9);   deadline(&mut f, 1);
race(&mut s1, &mut f); race(&mut f, &mut s1);  race(&mut s1, &mut s2);
deadline_dyn(&mut s1, 5);  deadline_dyn(&mut f, 5);
```

**(a)** How many machine-code copies of each function exist?
**(b)** `race`'s second parameter becomes `b: &mut dyn Clock`. How many copies
of `race` now?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)**

| Function | Copies | Which |
|---|---|---|
| `deadline` | 2 | `Stepper` and `Frozen`; `s1` and `s2` share a type, so they share a copy |
| `race` | 3 | `(Stepper, Frozen)`, `(Frozen, Stepper)`, `(Stepper, Stepper)` |
| `deadline_dyn` | 1 | it is not generic |

The fourth pair, `(Frozen, Frozen)`, is never called, so it is never built.

**(b)** Two, one per type of `a`. `b` is always `dyn Clock`, and each
`b.now()` becomes an indirect call through the vtable.

</details>

#### Problem 3: Trace the exits { #problem-3 }

A boundary function returns [`version`](#08r-question-mark)'s byte on success,
−1 for `TooShort` and −2 for `BadMagic`.

**(a)** What does it return for `b"RV\x07"`, `b"RV\x00"`, `b"RV"`, `b"R"`,
`b""`, `b"XY\x07"`, `b"rv\x07"` and `b"XY"`?
**(b)** Someone deletes the `?` at the end of `version`'s first line. Which
line does rustc now reject, and why?
**(c)** Why could the boundary function not use `?`?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)**

| Packet | `version` | Boundary |
|---|---|---|
| `b"RV\x07"` | `Ok(7)` | 7 |
| `b"RV\x00"` | `Ok(0)` | 0 |
| `b"RV"` | `Err(TooShort)`: the magic passes, byte 2 is missing | −1 |
| `b"R"`, `b""` | `Err(TooShort)`: `get(0..2)` is `None` | −1 |
| `b"XY\x07"` | `Err(BadMagic)` | −2 |
| `b"rv\x07"` | `Err(BadMagic)`: `b"rv"` is not `b"RV"` | −2 |
| `b"XY"` | `Err(BadMagic)` | −2 |

The second row is why failure is negative: 0 is a real version.

**(b)** The comparison `magic != b"RV"`, with E0308, "expected
`Result<&[u8], HdrError>`, found `&[u8; 2]`". Without `?`, `magic` is still
the whole `Result`, not the two bytes inside it; `?` is what takes them out.

**(c)** `?` is an early `return Err(e)`, and a function returning `i64` has no
`Err` to return: E0277.

</details>

#### Problem 4: Short writes by the numbers { #problem-4 }

A device accepts at most 5 bytes per `write`, and a program sends
`b"stat: ok\n"`, 9 bytes.

**(a)** With one bare `write`, what does it return, and what arrives?
**(b)** With `write_all`, how many `write` calls happen, and what does each
return?
**(c)** The device starts answering `Ok(0)`. What does `write_all` do?
**(d)** Why would the program in (a) pass its tests on your laptop?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)** `Ok(5)`. `"stat:"` arrives and `" ok\n"` never does. Nothing reports
the loss unless the program compares 5 with 9.

**(b)** Two: `Ok(5)` for `"stat:"`, then `Ok(4)` for `" ok\n"`. Then
`write_all` returns `Ok(())`.

**(c)** It returns `Err(Error(-1))` at once, instead of asking forever for
bytes the device will not take.

**(d)** The harness's `write` takes every byte in one call, so a short write
never happens there. A green test proves the logic, not the handling of the
count.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| Array `[T; N]` | N values inline; the length is part of the type | `06r`, `34k`, `50k` |
| Slice `&[T]` | A borrowed view: an address and a length | `06r`, every command |
| `Vec<T>` | A growable buffer that owns heap memory | `06r` (host only), `38k` on |
| Closure | An unnamed function that may use the variables around it | `06r`, every adapter |
| Trait | A contract: methods a type must supply | `07r`, `36k`, `46k` |
| Default method | A trait method with a body, built on the required ones | `07r`, `36k` |
| Trait bound | The traits a type parameter must implement | `07r`, `36k` |
| Monomorphization | One compiled copy per type used: static dispatch | `07r`, `36k` |
| `&mut dyn Trait` | A fat pointer to a value and its vtable: dynamic dispatch | `07r`, `46k` |
| `Result<T, E>` | A `T`, or an `E` saying why not; `#[must_use]` | `08r`, `40k`, `50k` |
| `?` | Return the error now, or unwrap the value | `08r`, `40k`, `49k` |
| `write_all` | Repeats `write` until every byte is out | `10c`–`14c`, `53k` |

## Further reading { #reading }

- [Rust for Systems](../guides/rust-for-systems.md#5-arrays-slices-vec-iteration):
  arrays, slices and iteration;
  [traits and monomorphization](../guides/rust-for-systems.md#6-traits-generics-impl-trait-monomorphization),
  [static dispatch versus `dyn`](../guides/rust-for-systems.md#static-dispatch-vs-dyn),
  and [`Result`, `?` and error enums](../guides/rust-for-systems.md#7-result-error-enums).
- [ulib and the Command Set](../guides/ulib-and-commands.md#the-complete-api-surface):
  the whole API,
  [what `ulib::main!` expands to](../guides/ulib-and-commands.md#ulibmain-what-it-expands-to)
  and [the portability rules](../guides/ulib-and-commands.md#portability-rules-a-command-must-follow).
- [Midterm 1](../assignments/midterm-1.md) and
  [Practice Set 1](../assignments/practice-set-01.md), Part A.
- *The Rust Programming Language*, chapters 8, 9, 10 and 13:
  <https://doc.rust-lang.org/book/>.
- POSIX [`write()`](https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html):
  the specification that allows a short write.
