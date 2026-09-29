# Week 2 · Ownership and Borrowing

> **Thu Sep 3** `02r_ownership` · **Fri Sep 4** `03r_borrowing`
>
> Taught Tue Sep 1. **Essentials** is what Thursday and Friday assume.
> **Going deeper** is optional and is not on the exam.

[Slides](02-cs326-2026-09-01-ownership-and-borrowing-slides.html){ .md-button }
[Thursday prep](../prep/02-cs326-2026-09-03-prep-ownership.md){ .md-button }
[Friday prep](../prep/02-cs326-2026-09-04-prep-borrowing.md){ .md-button }
[In-class slides](../inclass/week02-slides.html){ .md-button }

## This week { #this-week }

In `32k` your kernel hands out 4096-byte pages of RAM. If one page is ever out
to two callers at once, each overwrites the other's data, and nothing crashes
until much later. In `37k`, reading a lock's data without holding the lock
stops compiling. Both rest on this week's two ideas.

On Thursday every value gets exactly one owner, and handing it over kills the
old name. On Friday you lend values instead, and the compiler checks every
loan. [Midterm 1](../assignments/midterm-1.md) (Oct 15) tests both, and
[Practice Set 1](../assignments/practice-set-01.md) Part A practices them. By
Friday night you can say which lines the borrow checker will refuse, and why,
before you compile.

---

## Essentials { #essentials }

### Thursday · `02r` Ownership and moves { #thu-02r }

In `32k` the free list must never hold a page that someone is using.
`02r_ownership` models that rule with moves alone, so the compiler enforces it.

#### No `free()`, and no collector { #02r-owner }

C releases heap memory only when you call `free`, and no compiler checks those
calls. Release a block twice, or read it afterwards, and you are using bytes
the allocator may have handed to someone else. Java and Python add a **garbage
collector**, a runtime service that itself runs on an operating system, which
a kernel does not have.

Rust decides release at compile time. Each value has a single **owner**, the
binding that answers for it; ownership can pass along but is never shared.
When the owner's scope ends, the value is **dropped** and its memory goes back
at that brace:

```rust
{
    let motd = String::from("welcome");   // motd owns 7 heap bytes
    println!("{motd}");
}                                          // motd is dropped here
```

Read the closing brace as the `free()` you never write: it runs exactly once,
and never while the value is in use.

#### A move copies the handle, not the buffer { #02r-moves }

A `String` or a `Vec` is a 24-byte **handle** on the stack (pointer, length,
capacity) and a buffer on the **heap**, allocated at run time:

```text
stack                                  heap
queue: [ ptr | len 3 | cap 3 ] ──────▶ [ 4 | 8 | 15 ]
```

Assignment copies the handle. Two live handles would free the buffer twice, so
assignment is a **move**: the new binding takes over, and the old name is dead:

```rust
let queue = vec![4, 8, 15];
let backlog = queue;            // the handle is copied; queue is dead
println!("{}", queue.len());
```

```text
error[E0382]: borrow of moved value: `queue`
2 |     let queue = vec![4, 8, 15];
  |         ----- move occurs because `queue` has type `Vec<i32>`, which does not implement the `Copy` trait
3 |     let backlog = queue;
  |                   ----- value moved here
4 |     println!("{}", queue.len());
  |                    ^^^^^ value borrowed here after move
```

Read E0382 as a use-after-free, found before the program runs.

#### Moving through a call, and handing it back { #02r-calls }

Passing a value to a function moves it into the parameter:

```rust
fn archive(entries: Vec<String>) {
    println!("archived {}", entries.len());
}                               // entries is dropped here

let log = vec![String::from("boot")];
archive(log);                   // log moves into entries
println!("{}", log.len());      // E0382
```

Until Friday, a callee hands a value back only by returning it. `+` on a
`String` does exactly that:

```rust
let file = String::from("notes");
let file = file + ".txt";       // the old file is consumed
println!("{file}");             // notes.txt
```

Read the second `let file` as a new binding that **shadows** the dead one. Two
results travel as a **tuple**: `let (sum, wrapped) = 250u8.overflowing_add(10);`
binds 4 and `true`. Threading values back out gets old fast; Friday removes
most of it.

A parameter is a binding, so changing one takes `mut`:
`fn median(mut samples: Vec<u32>) -> u32` may call `samples.sort()`. Without
the `mut`, that call is E0596.

#### `Copy` types stay put { #02r-copy }

A `u32` has no heap buffer: its four bytes are the whole value. Rust marks
such types **`Copy`**: assignment and by-value calls leave the source alive.
Scalars (integers, `bool`, `char`), shared references, and tuples and arrays of
`Copy` parts are `Copy`; `String` and `Vec` own buffers and are not:

```rust
let pid: u32 = 7;
let cmd = String::from("sh");
let task = (pid, cmd);          // pid is copied in; cmd is moved in
println!("{pid}");              // fine
println!("{cmd}");              // E0382: borrow of moved value: `cmd`
```

Read `Copy` as "owns nothing that needs releasing"; size is not the test.
Friday's `&mut T` is the exception: two copies would be two exclusive loans.

> **The one thing to get right:** E0382 underlines the line that *uses* the
> value, but the mistake is the move before it. The span "value moved here"
> names where the value left. Start there, and ask who owns it now.

### Friday · `03r` Borrowing { #fri-03r }

From `32k` on, kernel code looks at one page many times, and with moves alone
the first look would take it away. `03r_borrowing` lends values instead.

#### Lending: `&` and `&mut` { #03r-borrow }

Writing `&x` **borrows** `x`: the result is a **reference**, an address that
reaches `x` while its owner keeps it. The **borrow checker**, part of rustc,
tracks where each reference came from and which lines still use it. A
reference owns nothing, so dropping one releases nothing.

A **shared** borrow, `&T`, may read, and any number may coexist. An
**exclusive** borrow, `&mut T`, may read and write, and while it lives it is
the only path to the value. Say "exclusive", not "mutable": the promise is that
nobody else is looking.

Write through a loan with `*`:

```rust
fn halve(level: &mut u32) {
    *level /= 2;                // write through the loan
}

let mut level = 40;
halve(&mut level);
halve(&mut level);              // level is now 10
```

Read `*level` as "the `u32` that `level` points at". Without the `*` it is
E0368, and rustc suggests adding one. Method calls borrow for you: `v.len()`
lends `&v`, and `v.push(x)` lends `&mut v`.

#### Slices: a pointer and a length { #03r-slices }

A **slice**, `&[T]`, is a view of consecutive elements in someone else's array
or `Vec`: 16 bytes, a start and a count, with nothing copied. `&mut [T]` is the
exclusive version, and `&str` is a view of UTF-8 text. `&temps` lends a whole
array; `&temps[1..4]` lends part of it:

```rust
fn ends(xs: &[i32]) -> (i32, i32) { (xs[0], xs[xs.len() - 1]) }

let temps = [18, 21, 25, 30, 27];
ends(&temps);                   // (18, 27): the whole array
ends(&temps[1..4]);             // (21, 30): elements 1, 2 and 3
ends(&vec![5, 9]);              // (5, 9): a Vec, lent as a slice
```

#### Aliasing XOR mutation, and when a borrow ends { #03r-aliasing }

The borrow checker enforces one rule:

> **Many readers through `&`, or one writer through `&mut`. Never both at once.**

Two references to one value **alias** it; changing it through either is
**mutation**. Together, a writer can move data a reader still uses: a `Vec`
that outgrows its buffer may move to a new one and free the old:

```rust
let mut tasks = vec![String::from("init"), String::from("sh")];
for t in &tasks {               // a shared loan for the whole loop
    if t == "sh" {
        tasks.push(String::from("login"));   // needs &mut tasks
    }
}
```

That is E0502: the loop still reads when `push` writes. Pass one account as
both arguments of `fn transfer(from: &mut u32, to: &mut u32)` and two writers
collide: E0499. The checker does not compare indexes: `&v[i]` and `&mut v[j]`
collide even when `i != j`, and rustc names the place `v[_]`.

**A borrow ends at its last use.** A loan runs from the line that creates it
to the last line that uses it, not to the closing brace:
{ #03r-last-use }

```rust
let mut name = String::from("init");
let r = &name;                  // loan opens
name.push_str("-v2");           // E0502: r is read again below
println!("{r}");
```

Swap the last two lines and it compiles: the loan closes before the write
takes its `&mut`. Scope decides when a value is dropped; the last use decides
when a loan ends.

#### Lifetimes name a relationship { #03r-lifetimes }

A reference is good only while the value behind it exists; that stretch of
code is its **lifetime**. A returned reference must say which input it borrows
from. With one reference input rustc assumes that one; with two, it makes you
say:

```rust
fn after(line: &str, prefix: &str) -> &str {
    &line[prefix.len()..]       // assumes line starts with prefix
}
```

That is ``error[E0106]: missing lifetime specifier``: the signature does not
say whether the result borrows from `line` or `prefix`. Name a lifetime on the
input it comes from:

```rust
fn after<'a>(line: &'a str, prefix: &str) -> &'a str
```

Read `'a` as "the result is good only while `line` is". It extends nothing:
rustc holds every caller to that claim, and `prefix`, with no `'a`, may be
dropped once the call returns.

When the result may come from either input, put `'a` on both, as in
`fn either<'a>(x: &'a str, y: &'a str) -> &'a str`. The result is then good
only while both are.

A reference kept in a struct field is a stored loan, so the struct's type
carries the lifetime:

```rust
struct Setting<'a> {
    key: &'a str,               // text owned elsewhere
    value: &'a str,
}
```

Read `Setting<'a>` as "good only while the text behind its fields is". With
plain `&str` fields and no `'a`, each is E0106; outlive the text and it is
E0597. A field can be a `&mut` too: until the struct's last use, even the owner
may not read the value.

#### The errors you will actually hit { #03r-errors }

| Code | rustc says | Read it as |
|---|---|---|
| E0382 | borrow of moved value (or use of moved value) | Given away, then used |
| E0596 | cannot borrow `x` as mutable, as it is not declared as mutable | A change without `mut` |
| E0499 | cannot borrow `x` as mutable more than once at a time | Two writers at once |
| E0502 | cannot borrow `x` as mutable because it is also borrowed as immutable | A write while a reader looks |
| E0505 | cannot move out of `x` because it is borrowed | A move while lent out |
| E0106 | missing lifetime specifier | Borrowed from what? |

For each, ask two questions: who owns this, and who is looking at it now?

> **The one thing to get right:** E0502 lands on a line that looks harmless.
> The loan it collides with began earlier and is used *later*, at the span
> marked "later used here". The cure is nearly always order: finish reading
> before you write.

### For the exam { #exam }

*Not needed on Thursday or Friday. On Midterm 1.*

**What survives a move** · *Midterm 1.* Given numbered lines, say which compile
and name each move. Work top to bottom and keep a list of dead names.
Assignment, a by-value call and placing a value in a tuple each kill a
non-`Copy` name; a `Copy` name survives any number of copies. The usual
slip is accepting a later `x.len()` "because it only reads": reading still needs
`x` to exist. [Problem 1](#problem-1) has this shape.
{ #exam-moves }

**Fix a borrow error without `clone()`** · *Midterm 1.* Name the rule, quote
the two conflicting borrows, and give the smallest edit. Two cures cover most
cases: reorder, so the first loan's last use comes before the second loan; or
copy a `Copy` value out, so no reference is left alive. `clone()` compiles too,
but on a `String` or `Vec` it builds a second heap value when you only needed
to read, and early in a kernel there is no allocator to build it with. On a
`Copy` value it is the copy-out cure spelled longer, and it hides that you
never needed a reference. [Problem 3](#problem-3) has this shape.
{ #exam-fix }

**Lifetimes by example** · *Midterm 1.* Given a signature, say which input the
result borrows from, then whether a call site is accepted. In
`fn f<'a>(x: &'a str, y: &str) -> &'a str` the result may outlive `y` but
not `x`. With `'a` on both inputs, it is bounded by whichever dies first.
[Problem 4](#problem-4) has this shape.
{ #exam-lifetimes }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday or Friday, and nothing here is on
the exam.*

### See the handle move { #deeper-handle }

Print a `Vec`'s buffer address before and after a move, then after a `push`
that outgrows it:

```rust
let a = vec![7u64; 4];                   // len 4, cap 4
println!("a     buffer {:p}", a.as_ptr());
let mut b = a;                           // a move
println!("b     buffer {:p}", b.as_ptr());
b.push(8);                               // full, so the buffer must grow
println!("push  buffer {:p}  cap {}", b.as_ptr(), b.capacity());
```

```text
a     buffer 0x1013c9d70
b     buffer 0x1013c9d70
push  buffer 0x1013c9dd0  cap 8
```

The addresses change from run to run; the pattern does not. The move left the
buffer where it was, and only the 24-byte handle changed hands. The `push`
allocated a larger buffer, copied four elements across, and freed the old one.
A reference into the old buffer would now point at freed memory, which is
exactly the loan E0502 refuses.

### Why a kernel cares most { #deeper-kernel }

Aliasing plus mutation sits under three of the worst bug classes in systems
code. **Iterator invalidation** is the dangling reference above. **Optimizer
hazards** come next: C must assume two pointers of one type may name the same
memory, which is why C99 added `restrict`, and why a wrong `restrict`
miscompiles in silence. **Concurrent corruption** is two CPUs updating one
table at once.

A kernel is concurrent even on one CPU. An interrupt can arrive between any two
instructions, run a handler that touches your data, and return, and your code
never knows. The console in `45k` has that shape: a handler adds typed bytes to
a buffer that a reader drains. No borrow describes two agents with no call
between them, so that buffer is a `static mut` reached through `unsafe`, and the
proof that it is safe is written by hand.

### Elision, and one name where two belong { #deeper-elision }

You rarely write lifetimes, because three **elision** rules supply them:

1. Each reference parameter gets a lifetime of its own.
2. With exactly one input lifetime, every output reference gets it.
3. In a method taking `&self` or `&mut self`, outputs get `self`'s lifetime.

Rule 2 is why `fn first_word(s: &str) -> &str` needs nothing. `after` has two
input lifetimes and no `self`, so rule 1 applies but no rule gives the result a
lifetime.

rustc's own suggestion for `after`'s E0106 puts `'a` on both parameters. That
compiles, but `after`'s result comes from `line` alone, so it claims more than
is true: the result is now bounded by
whichever input dies first, and a caller who drops `prefix` early is refused:

```rust
let line = String::from("hz=100");
let value;
{
    let key = String::from("hz=");
    value = after(&line, &key);         // 'a on both parameters
}
println!("{value}");                    // key is gone
```

That is ``error[E0597]: `key` does not live long enough``. With `'a` on `line`
alone, the same code compiles and prints `100`. One name where two belong
over-constrains, and rejects programs that were correct.

### Two writers, provably apart { #deeper-split }

The rule is about overlap, not about how many `&mut` a line mentions.
`split_at_mut` hands back two exclusive slices that cannot overlap:

```rust
let mut lanes = [10, 20, 30, 40];
let (left, right) = lanes.split_at_mut(2);   // [10, 20] and [30, 40]
left[0] += right[1];                          // two &mut at once
right[0] += left[1];
println!("{lanes:?}");                        // [50, 20, 50, 40]
```

Write `&mut lanes[0]` and `&mut lanes[2]` side by side instead and you get
E0499: the checker does not compare index values, so any two might be equal.
`split_at_mut` is safe to call because its body checks the split point once and
then uses `unsafe` inside the standard library. That is week 6's pattern: a
small unsafe core under a safe signature.

### Where this goes: a lock you cannot misuse { #deeper-guard }

In `37k` the lock and the data it protects are one value, so the only way to
name the data is through the lock. Acquiring the lock produces a **guard**, a
struct that borrows the lock the way `Setting<'a>` borrows its text. The
guard's methods lend out the data, and those loans cannot outlast the guard.

Dropping the guard releases the lock; week 3 shows how a drop can run code.
After the release there is no guard left to borrow through, so a late read has
no name to use and does not compile. In xv6's C, code can read a structure
after `release()` and nothing objects.

### Where the rules run out { #deeper-limits }

In `32k` the free list lives inside the free pages: each free page's first
bytes point at the next one. That is aliasing and mutation by design, over
addresses the hardware handed out, with no Rust value in sight. Safe Rust cannot
say it, so the allocator uses raw pointers and `unsafe` (week 6). `unsafe` does
not switch off the borrow checker; it permits a few extra operations and makes
you, not the compiler, answer for them.

| | xv6 (C) | Linux (C) | rv6 (Rust) |
|---|---|---|---|
| Who owns memory | a comment | a comment | the type system |
| Use-after-free | possible anywhere | possible anywhere; KASAN catches some while running | only inside `unsafe` |
| What to audit | everything | everything | the `unsafe` blocks |

Microsoft and the Chromium project each report that about 70% of the serious
security bugs they fix are memory-safety bugs. Rust does not delete the code
that can have them. It shrinks it, and marks it with a keyword you can search
for.

### Practice problems { #problems }

#### Problem 1: What survives a move { #problem-1 }

Judge each numbered line on its own, as if every failing line were deleted.
Which lines fail, and why?

```rust
fn shout(s: String) -> String { s.to_uppercase() }

let motd = String::from("hi");   // 1
let n = motd.is_empty();         // 2
let loud = shout(motd);          // 3
let again = motd.len();          // 4
let m = n;                       // 5
let pair = (n, loud);            // 6
let first = pair.0;              // 7
println!("{loud}");              // 8
let loud = shout(pair.1);        // 9
println!("{}", pair.0);          // 10
let whole = pair;                // 11
```

<details markdown="1">
<summary>Click to reveal solution</summary>

| Line | Compiles? | Why |
|---|---|---|
| 1 | yes | `motd` owns `"hi"` |
| 2 | yes | `is_empty` borrows `motd`; `n` is a `bool` |
| 3 | yes | `motd` moves into `s`, which dies at `shout`'s brace; `loud` owns the new `String` |
| 4 | **no** | ``E0382: borrow of moved value: `motd` ``, moved on line 3 |
| 5 | yes | `bool` is `Copy` |
| 6 | yes | `n` is copied in; `loud` moves in |
| 7 | yes | `pair.0` is a `bool`, copied out |
| 8 | **no** | `loud` moved into `pair` on line 6 |
| 9 | yes | moves the `String` field out of `pair`; the new `loud` shadows the dead one |
| 10 | yes | only the `String` left; the `bool` field is still there |
| 11 | **no** | ``E0382: use of partially moved value: `pair` ``: moving the whole tuple needs every field |

Lines 9 to 11 show that a tuple's fields are owned one by one. Moving one field
out is a **partial move**: the rest stay usable, but the tuple as a whole does
not.

</details>

#### Problem 2: `Copy` or not { #problem-2 }

Say whether each type is `Copy`, with a one-line reason: (1) `u8`,
(2) `(u32, bool)`, (3) `[u64; 512]`, (4) `String`, (5) `&str`, (6) `&mut u32`,
(7) `(u32, String)`, (8) `Vec<u8>`.

<details markdown="1">
<summary>Click to reveal solution</summary>

1. **Yes.** Plain bits, nothing to release.
2. **Yes.** A tuple of `Copy` types.
3. **Yes.** An array of a `Copy` type is `Copy` at any length. `let b = a;`
   then copies 4 KiB, which is why kernel code passes `&[u64]` instead.
4. **No.** It owns a heap buffer; two copies would drop it twice.
5. **Yes.** A shared reference. Any number may exist, and dropping one frees
   nothing.
6. **No.** Two copies would be two exclusive borrows of one value. Passing a
   `&mut` to a function lends it for the call; it does not duplicate it.
7. **No.** One field is not `Copy`, so the tuple is not: "the trait bound
   `String: Copy` is not satisfied in `(u32, String)`".
8. **No.** For the same reason as `String`.

</details>

#### Problem 3: Fix it without `clone()` { #problem-3 }

For each fragment, give the error code and the two uses that conflict, then the
smallest fix that keeps the intent. `std::mem::swap` exchanges the values behind
two `&mut`.

```rust
// (a) show the name at index 1, then sort
let mut names = vec![String::from("sh"), String::from("init")];
let top = &names[1];
names.sort();
println!("{top}");

// (b) swap the first and last cells
let mut grid = [1, 2, 3];
let a = &mut grid[0];
let b = &mut grid[2];
std::mem::swap(a, b);

// (c) show a report, then shelve it; shelve takes a String
let report = String::from("all clear");
let view = &report;
shelve(report);
println!("{view}");

// (d)
let mut job = (3, String::from("sh"));
let n = job.0;
job = (n + 1, String::from("login"));
println!("{n}");
```

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a) E0502.** `top` is a shared loan into `names`, still used on the last
line, and `sort` needs `&mut names` in between. Copying out does not work here:
a `String` is not `Copy`, and `let top = names[1];` is ``error[E0507]: cannot
move out of index of `Vec<String>` ``. Print before sorting, so the loan ends
first. Storing the index 1 compiles, but after the sort index 1 holds `"sh"`.

**(b) E0499.** Two `&mut` into `grid` are alive at the swap; the checker does
not compare 0 with 2. Use `grid.swap(0, 2);`, one exclusive borrow that does
the two-index work itself, giving `[3, 2, 1]`. `split_at_mut` also works.

**(c) E0505.** `shelve(report)` moves `report` while `view` still borrows it,
and `view` is used afterwards. Move the `println!` above the call.

**(d) Compiles, and prints 3.** `n` is a copy of the `i32` in `job.0`, not a
reference, so no loan is alive when `job` is overwritten. This is the copy-out
cure. Write `let n = &job.0;` instead and the assignment is
``error[E0506]: cannot assign to `job` because it is borrowed``.

</details>

#### Problem 4: Which lifetime? { #problem-4 }

Does each compile as written? If not, give the fixed signature, or say why no
annotation helps. `format!` builds a `String` the way `println!` prints one.
`…` stands for a body that returns part of an input.

```rust
fn trim_nul(buf: &[u8]) -> &[u8] { … }             // (a)
fn value_of(text: &str, key: &str) -> &str { … }    // (b) returns part of text
struct Index { words: Vec<&str> }                   // (c)
fn greeting(name: &str) -> &str {                   // (d)
    let text = format!("hello, {name}");
    &text
}
```

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a) Compiles.** One input lifetime, so by elision rule 2 the result borrows
from `buf`.

**(b) E0106.** Tie the result to `text` alone:
`fn value_of<'a>(text: &'a str, key: &str) -> &'a str`. Putting `'a` on `key`
too compiles, but refuses a caller whose key dies before the result is used.

**(c) E0106** on the `&str` inside the `Vec`. Write
`struct Index<'a> { words: Vec<&'a str> }`: an `Index` is good only while the
text its words point into is. The lifetime goes wherever a reference appears,
even inside another type.

**(d) The signature is fine** by rule 2, but the body is ``error[E0515]: cannot
return reference to local variable `text` ``. `text` is dropped at the closing
brace, and no annotation can make it live longer: a lifetime describes, it
never extends. Return the `String` itself: `fn greeting(name: &str) -> String`.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| Owner | The one binding responsible for a value and its release | `02r`, `32k` |
| Drop | The release of a value when its owner's scope ends | `02r`; `Drop` in `04r`, `37k` |
| Move | Ownership passing to a new binding; the old name is dead | `02r` onward |
| `Copy` | Duplicated bit for bit; owns nothing to release (not `&mut T`) | `02r`, `04r` |
| Reference | A pointer that borrows a value without owning it | `03r` onward |
| `&T` / `&mut T` | Shared (read, many at once) / exclusive (read and write, one) | `03r`, `37k` |
| Slice | A pointer and a length over elements side by side: `&[T]`, `&str` | `03r`, `10c`–`13c` |
| Aliasing XOR mutation | Many readers or one writer, never both | `03r`, `37k` |
| Last use | Where a borrow ends: its final use, not the closing brace | `03r` |
| Lifetime | The stretch of code where a reference stays valid; `'a` names it | `03r`, `37k` |

## Further reading { #reading }

- [Rust for Systems Programming](../guides/rust-for-systems.md#1-ownership-and-moves):
  [the rule](../guides/rust-for-systems.md#the-rule),
  [moving](../guides/rust-for-systems.md#moving),
  [`Copy` types](../guides/rust-for-systems.md#copy-types-do-not-move),
  [two kinds of borrow](../guides/rust-for-systems.md#two-kinds-of-borrow),
  [the aliasing rule](../guides/rust-for-systems.md#the-aliasing-rule),
  [slices](../guides/rust-for-systems.md#slices-are-borrows),
  [three ways to hold a run of values](../guides/rust-for-systems.md#three-ways-to-hold-a-run-of-values)
  (the `Vec` calls `02r` uses),
  [lifetimes](../guides/rust-for-systems.md#lifetimes) and
  [common compiler errors](../guides/rust-for-systems.md#common-compiler-errors-and-what-they-actually-mean).
- The deck as taught on Sep 1: the [in-class slides](../inclass/week02-slides.html)
  and [their runnable examples](../inclass/week02-examples.html), including
  every error in the table above.
- [Exam Prep](../guides/exam-prep.md) and [Practice Set 1](../assignments/practice-set-01.md)
  Part A, for Midterm 1.
- *The Rust Programming Language*, chapter 4, "Understanding Ownership", and
  section 10.3, "Validating References with Lifetimes".
- `rustc --explain E0502`, or any other code: the compiler's long explanation,
  with examples.
- RFC 2094, "Non-lexical lifetimes": why a borrow ends at its last use.
- Microsoft Security Response Center, "A proactive approach to more secure code"
  (2019), and the Chromium project's "Memory safety" page: the 70% figures.
