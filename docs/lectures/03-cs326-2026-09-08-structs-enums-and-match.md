# Week 3 · Structs, `impl`, Enums, and `match`

> **Thu Sep 10** `04r_structs_impl` · **Fri Sep 11** `05r_enums_match`
>
> Taught Tue Sep 8. **Essentials** is what Thursday and Friday assume, and
> [Midterm 1](../assignments/midterm-1.md) tests it.
> **Going deeper** is optional and is not on the exam.

[Slides](03-cs326-2026-09-08-structs-enums-and-match-slides.html){ .md-button }
[Thursday prep](../prep/03-cs326-2026-09-10-prep-structs-and-impl.md){ .md-button }
[Friday prep](../prep/03-cs326-2026-09-11-prep-enums-and-match.md){ .md-button }
[In-class slides](../inclass/week03-slides.html){ .md-button }

## This week { #this-week }

Later this term the kernel leans on types in three places. `33k` packs an
address and its permission bits into one 64-bit word; `34k` keeps a record for
each process; `35k` hands assembly a struct whose fields it finds by byte
offset. To the machine all three are integers; this week you give the compiler
types that tell them apart.

On Thursday you bundle values into structs, give them methods, wrap a bare
integer in a type of its own, and write a value that cleans up after itself.
Friday you write a type whose value is always one case from a closed list, and
a `match` that will not compile until every case has an answer. By Friday night
the compiler checks rules that a C kernel keeps in comments.

---

## Essentials { #essentials }

### Thursday · `04r` Structs, methods, and the guard { #thu-04r }

By `34k` every process is one record that the scheduler reads and the context
switch saves registers into. `04r_structs_impl` builds smaller types of the
same kind and gives them behavior.

#### Structs and `impl` { #04r-impl }

A **struct** gives a group of named values, its **fields**, one type, so they
are created, passed and returned together. Here are the numbers behind `top`'s
CPU line:

```rust
pub struct Cpu {
    pub id: u8,
    busy: u64,     // ticks spent running
    idle: u64,     // ticks with nothing to run
}
```

A field without `pub` is private to its module. A **struct literal** such as
`Cpu { id: 0, busy: 0, idle: 0 }` makes a value, and outside the module that
line is ``error[E0451]: fields `busy` and `idle` of struct `Cpu` are private``.
So outside its module, only `Cpu`'s methods can change the counters.

Behavior lives in an **`impl` block**:

```rust
impl Cpu {
    pub fn new(id: u8) -> Self { Cpu { id, busy: 0, idle: 0 } }
    pub fn tick(&mut self, ran: bool) {
        if ran { self.busy += 1 } else { self.idle += 1 }
    }
    pub fn load(&self) -> u64 { 100 * self.busy / (self.busy + self.idle).max(1) }
}
```

Read `tick` as a **method**: its first parameter is a form of `self`, and you
call it with a dot, `cpu0.tick(true)`. `new` takes no `self`, so it is an
**associated function**, called through the type: `Cpu::new(0)`; `new` is a
convention, not a keyword. `Self` means `Cpu`, and `Cpu { id, … }` is shorthand
for `id: id`.

#### The three selves, and `derive` { #04r-selves }

Each method's receiver is an ownership decision:

| Receiver | The method gets | The caller afterwards |
|---|---|---|
| `&self` | a shared borrow: it may read | still owns the value |
| `&mut self` | the only borrow: it may change fields | still owns it; needs `let mut` |
| `self` | the value itself | has lost it, unless the type is `Copy` |

Give `Cpu` a `retire(self) -> u64`, and the next line cannot use `cpu0` at
all:

```rust
let total = cpu0.retire();
let now = cpu0.load();     // error[E0382]: borrow of moved value: `cpu0`
```

`#[derive(...)]` generates a trait from the fields. With `Debug`, `{:?}` can
print the value, and so can a failing `assert_eq!`; `PartialEq` and `Eq` make
`==` compare field by field; `Clone` supplies `.clone()`. **`Copy`** lets
assignment and a by-value `self` leave the original usable: the bits are copied
either way, but the value is not moved. Derive it on small plain data, never on
a type that owns something ([the guard](#04r-drop) says why).

#### The newtype, and bits in a word { #04r-newtype }

A small LCD takes 16-bit RGB565 pixels: five bits of red, six of green, five of
blue. Some controllers want BGR565, with red and blue swapped.
`type Rgb565 = u16;` is an **alias**, a second name for `u16`, so the compiler
accepts either format and a red stop sign comes out blue. A one-field tuple
struct, a **newtype**, is a different type:

```rust
#[repr(transparent)]
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Rgb565(u16);
```

The field has no name, so you write its position: `px.0`. Hand a `Bgr565` to
`fn paint(px: Rgb565)` and rustc stops you: ``error[E0308]: mismatched types``,
``expected `Rgb565`, found `Bgr565` ``. The check costs nothing at run time,
and `#[repr(transparent)]` promises more than equal size: an `Rgb565` is passed
and stored exactly as a bare `u16`, so C code taking a `uint16_t` accepts
one.

Five operators are enough to pack fields into a word and cut them back out:

```text
x << n   bits move up n places             0x0028 << 5       = 0x0500
x >> n   bits move down; the low n drop    0x6D07 >> 5       = 0x0368
a | b    set in either: merges fields      0xF800 | 0x001F   = 0xF81F
a & m    set in both: keeps what m names   0x6D07 & 0x001F   = 0x0007
!m       every bit flipped                 0x6D07 & !0x001F  = 0x6D00
```

A **mask** is a constant whose ones mark a field: `(1 << n) - 1` is n ones, so
`0x1F` covers five bits and `0x3F` six. Built from those:

```rust
impl Rgb565 {
    pub const fn new(r: u16, g: u16, b: u16) -> Rgb565 {
        Rgb565((r << 11) | (g << 5) | b)        // rrrrr gggggg bbbbb
    }
    pub const fn green(self) -> u16 { (self.0 >> 5) & 0x3F }
}
```

Read `green` as two cuts: the shift drops blue off the bottom, and the mask
drops red off the top. For `0x6D07`, which is `new(13, 40, 7)`, an unmasked
`green` returns `0x368`, red still attached. `33k`'s page-table entry is this
shape on a 64-bit word.

The same operators round to a power-of-two boundary. Say each row of pixels
must start on a 16-byte boundary, and a row is 200 bytes, `0xC8`:

```text
row bytes              0xC8    200
add 0xF                0xD7    a partial block crosses its boundary
clear the low 4 bits   0xD0    208, the next multiple of 16
round down instead     0xC0    192, the clear step alone
```

Read "clear the low 4 bits" as "zero the last hex digit", which works only
because 16 is a power of two. An aligned row stays put: adding `0xF` cannot
carry it past its boundary.

#### Settled before run time: `const fn` and `#[repr(C)]` { #04r-const-fn }

rustc can run a **`const fn`** while compiling, whenever its arguments are
known then. `new` above is one, so this constant costs no instructions:

```rust
const WHITE: Rgb565 = Rgb565::new(31, 63, 31);   // rustc computes 0xFFFF
let px = Rgb565::new(r, g, b);                   // r, g, b known only at run time
```

Read `const` as a permission, not a restriction: the second line still runs
`new` at run time. Drop `const` from `new` and the first line fails with
``error[E0015]: cannot call non-const associated function `Rgb565::new` in constants``.
A `const` or `static` item and an array length, including the `N` in `[x; N]`,
all demand their value at compile time.

A kernel needs this because a `static` exists before any code runs, so nothing
can fill one in. `34k`'s table of 64 process records is built by a `const fn`
([week 9](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-table)).

Layout is settled at compile time too: by default rustc may reorder a
struct's fields to save padding. **`#[repr(C)]`** trades that freedom for C's layout
rule: each field follows the one before it, at the first offset its alignment
allows. Here is a sensor reading:
{ #04r-repr-c }

```rust
pub struct Reading { sensor: u8, value: u32, seq: u16 }
```

| Layout | `sensor` at | `value` at | `seq` at | Size |
|---|---|---|---|---|
| default (today's `rustc`) | 6 | 0 | 4 | 8 |
| `#[repr(C)]` | 0 | 4 | 8 | 12 |

The attribute earns its place when the bytes cross a boundary `rustc` does not
control: a device, a disk image, or `35k`'s assembly.
[For the exam](#exam-repr-c) says why forgetting it is silent.

#### `Drop`, and the guard { #04r-drop }

Week 2's free list trusted every caller to hand its page back, and one
forgotten call is a leak. With **`Drop`**, the type says what release means and
rustc decides where it happens. It inserts one call to `drop` at the point the
owner goes away: the last brace of a scope, a `return` halfway down, or the
body of a callee the value was moved into. This type announces its own:

```rust
struct Noisy(&'static str);
impl Drop for Noisy {
    fn drop(&mut self) { println!("drop {}", self.0); }
}
```

You never call the `drop` method yourself (`x.drop()` is
``error[E0040]: explicit use of destructor method``), and it runs once per
value on every path out. C++ names the pattern **RAII**; Rust adds a proof,
since week 2's ownership rules guarantee that no value is dropped twice.

A **guard** is a value whose life is the hold: making it takes the resource,
and its `drop` gives it back. This one keeps a terminal's echo off while a
password is typed:

```rust
pub struct Term { pub echo: bool }
pub struct Quiet<'a> { term: &'a mut Term, was: bool }

impl Drop for Quiet<'_> {
    fn drop(&mut self) { self.term.echo = self.was; }   // put it back
}
```

Read `Quiet<'_>` as "a `Quiet` borrowing something whose lifetime needs no
name". `term.quiet()` hands back a `Quiet` with echo already off; `was`
remembers the old setting. Holding the `&mut Term`, the guard shuts everyone
else out, and every way out of the scope restores echo:

```rust
fn login(term: &mut Term) {
    let _q = term.quiet();          // echo off
    let pw = read_secret();
    if pw.is_empty() { return; }    // _q drops here: echo back on
    check(pw);
}                                   // ...or here
```

A guard can never be `Copy`. A copy would be a second guard for the same
resource, and each would release it as it died: week 2's double free, now
automatic. So `#[derive(Clone, Copy)]` on `Noisy` is
``error[E0184]: the trait `Copy` cannot be implemented for this type; the type has a destructor``.
To release early, pass the value to the standard library's `drop(q)`: its body
is empty, and moving `q` in is the whole trick.

> **The one thing to get right:** `error[E0503]` or `E0502` on a line that
> only reads a field (`E0499` if it calls a `&mut self` method). While a guard
> holds a `&mut T`, week 2's rule lasts as long as the guard: that `&mut`
> excludes every other access, reads included. rustc names both lines: where
> the guard took the `&mut`, and the later use of the old name.

### Friday · `05r` Enums and `match` { #fri-05r }

In `34k` a process is in exactly one of five states, and in `36k` the scheduler
sometimes finds nobody to run. `05r_enums_match` gives both ideas a type rustc
can enforce.

#### An enum is one of a fixed set { #05r-enums }

A struct is this field *and* that one; an **enum** is this case *or* that one.
Each case is a **variant**, and a variant may carry fields of its own. Here is
one slot of a disk-block cache:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Slot {
    Empty,
    Loading(u32),                     // a read of this block is in flight
    Clean { block: u32 },
    Dirty { block: u32, age: u32 },   // age: seconds since the first write
}
```

A `Slot` is one of those four and nothing else. Build a tuple variant like a
call, `Slot::Loading(12)`, and a struct variant like a struct,
`Slot::Dirty { block: 12, age: 0 }`. An `Empty` slot has no `block` to read by
mistake, and there is no fifth value.

#### `match`, and the arms you cannot forget { #05r-match }

`match` tries its **arms** from the top and takes the first whose pattern fits
the value:

```rust
let line = match slot {
    Slot::Empty => String::from("free"),
    Slot::Loading(b) => format!("reading block {b}"),
    Slot::Clean { block } | Slot::Dirty { block, .. } => format!("block {block}"),
};
```

Read `Slot::Dirty { block, .. }` as "a dirty slot: call its block `block` and
ignore the rest". A pattern **binds** fields to names, `|` joins two patterns
in one arm, and `..` skips fields. `match` is an expression, so its value lands
in `line`.

The arms must cover every variant. Add `Pinned { block: u32 }` to `Slot`, and
every `match` that has not decided about it stops compiling:

```text
error[E0004]: non-exhaustive patterns: `Slot::Pinned { .. }` not covered
```

Read E0004 as a search done for you: rustc names the line of every `match`
that has not said what `Pinned` means. A bare
`_` arm fits any value, including variants added next year, so a `match` ending
in `_` never shows up in E0004 again. Save `_` for when every remaining value
really gets one answer, such as a raw number from hardware. When each variant
needs its own answer, name them all.

#### Guards, and matching two values { #05r-guards }

Some decisions depend on a field's value, not just the variant. An `if` after
a pattern, a **match guard** (not Thursday's kind), expresses that:

```rust
fn evict_cost(slot: Slot, limit: u32) -> u32 {
    match slot {
        Slot::Empty | Slot::Clean { .. } => 1,
        Slot::Dirty { age, .. } if age >= limit => 2,   // old: write back, then reuse
        Slot::Dirty { .. } => 5,                        // young: likely written again
        Slot::Loading(_) => 9,                          // mid-read: the worst choice
    }
}
```

Read `Slot::Dirty { age, .. } if age >= limit` as one test: the variant must
fit and the condition must hold. With a limit of 30, a dirty slot of age 10
fails the condition, so rustc tries the next arm, which answers 5.
Exhaustiveness ignores guards, since rustc cannot know when `age >= limit`;
delete the `=> 5` arm and you get
``E0004 … `Slot::Dirty { .. }` not covered``.

A `match` can also test two values at once as a tuple, one pattern per value,
and exhaustiveness covers every combination:

```rust
let plan = match (slot, pinned) {
    (_, true) => "keep",
    (Slot::Dirty { .. }, false) => "flush first",
    (Slot::Loading(_), false) => "wait",
    (Slot::Empty, false) | (Slot::Clean { .. }, false) => "evict",
};
```

Read `(_, true)` as "any slot, if pinned". Inside a pattern, `block: b` binds a
field under a name you choose. You need it when one pattern holds two fields
of the same name: binding `block` twice is
``error[E0416]: identifier `block` is bound more than once in the same pattern``.

> **The one thing to get right:** a test expects `None` and gets `Some`, for an
> input that differs from a legal one only in one field's value. A pattern such
> as `Dirty { .. }` matches every dirty slot, whatever its age. When a value
> decides, the decision is a match guard, and a failed one sends matching on to
> the arms below it.

#### `Option`: an answer that may be missing { #05r-option }

In C, "no answer" is a special value such as a null pointer, which a caller
can use by mistake. Rust gives "maybe a value" its own type, one line in the
standard library:

```rust
enum Option<T> { None, Some(T) }
```

`T` is filled in at each use: `Option<u32>`, `Option<Slot>`.
An `Option<u32>` is not a number, so `x + 1` on one is
``error[E0369]: cannot add `{integer}` to `Option<u32>` ``; you take it apart
first. `Vec::pop` returns one, so an empty vector answers `None`, not garbage:

```rust
match dirty.pop() {
    Some(block) => flush(block),
    None => println!("nothing dirty"),
}
if let Some(block) = dirty.pop() { flush(block); }     // a one-arm match
```

Read `if let PATTERN = VALUE` as a `match` with one arm and an unwritten
"otherwise, nothing". `.unwrap_or(x)` supplies a fallback. `.unwrap()` panics
on `None`, and in a kernel a panic halts the machine. `36k`'s scheduler answers
with an `Option<usize>`, where `None` means nobody is runnable.

### For the exam { #exam }

*Not needed on Thursday or Friday. On Midterm 1.*

**Why assembly needs `#[repr(C)]`** · *Midterm 1.* Assembly reaches a field as
a fixed number, "base plus 16". The default layout promises no order, so only
`#[repr(C)]` makes that number true. Delete the attribute and both the Rust and
the assembly still build. The first symptom comes later and elsewhere: a
register loaded from the wrong field. Worse, an all-`u64` struct usually keeps
its order anyway, so the bug waits for a new field or a new compiler.
{ #exam-repr-c }

**A sentinel, or `Option`** · *Midterm 1.* A **sentinel** is an ordinary value
that means "no answer", such as physical address 0 for "not mapped". It is safe
only if no success can take that value: rv6's RAM starts at `0x8000_0000`, so
no page is ever at 0. Even then the sentinel has the same type as a real
answer, and a caller who forgets to check uses it as one. `Option<usize>` gives
"not mapped" its own type, so the compiler refuses the unchecked use. Practice
Set 1, Problem 3(a), has this shape.
{ #exam-sentinel }

**What `_` costs** · *Midterm 1.* A `match` over an enum ends in `_ => …`, and
a variant is added. The `match` still compiles, and the new variant silently
takes the `_` arm, whether or not that answer fits. Without `_`, the same change
is an `E0004` naming the line. A full answer says both: the compiler stayed
quiet, and nobody chose the new variant's answer. Practice Set 1, Problem 3(b),
asks this; [Problem 4](#problem-4) practices it.
{ #exam-wildcard }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday or Friday, and nothing here is on
the exam.*

### Where rv6 draws the type line { #deeper-type-line }

`mappages()` (`vm.rs`) takes a virtual address, a size, a physical address and
a permission word, and four of its five parameters are `usize`. Swap the two
addresses at a call site and the kernel compiles, boots and maps the wrong
page. rv6 gives page-table entries their own type, `Pte` (`vm.rs`), because
entries and addresses are confused constantly and fatally. Addresses, sizes
and pids stay `usize`, since wrapping every one would bury a teaching kernel in
conversions. Linux draws the same line: on RISC-V its `pte_t` and `pgprot_t`
are one-member C structs, C's nearest thing to a newtype, while `phys_addr_t`
is a plain `typedef`, an alias.

### What an enum costs { #deeper-layout }

An enum is a **discriminant**, a small tag naming the variant, plus room for
its largest payload, rounded up for alignment. `Slot` is 12 bytes: a tag
padded to 4 bytes, then two `u32`s. The compiler also hunts for **niches**,
bit patterns a payload can never hold, and hides a tag there:

```text
size_of::<&Slot>()           8     a reference is never null
size_of::<Option<&Slot>>()   8     so None takes the null pattern
size_of::<Option<u32>>()     8     every u32 is valid, so a tag is added
size_of::<Option<Slot>>()    12    Slot's own tag has unused values
```

So an `Option` around a reference costs nothing. Tony Hoare, who put null
references into ALGOL W in 1965, called them his "billion-dollar mistake" in
2009. Absence was never the problem; giving it the same type as presence was.

### When `_` is right { #deeper-wildcard }

rv6 has `_` arms, and they are right. `dispatch()` (`syscall.rs`) answers a
system-call number it does not know with -1, and `kerneltrap()` (`trap.rs`)
ignores interrupt causes it does not handle. Both match a raw
integer chosen by a user program or by the hardware: that domain is open, and
no list of arms can close it. An enum you defined is closed, so when each
variant needs its own answer, name them.

Two shorthands share `_`'s blind spot. `matches!(slot, Slot::Dirty { .. })`
answers yes or no, and a new variant is silently no.
`let Slot::Loading(b) = slot else { return; };` binds the field or leaves the
function, and a new variant silently leaves.

### Drop order, and who drops a moved value { #deeper-drop-order }

Locals drop in reverse order of declaration, last in, first out. That is the
nesting locks need: take A then B, release B then A. A struct runs its own
`drop` first, then drops its fields in declaration order. A move changes who
drops the value: pass a `Noisy` into a function and it drops at that
function's closing brace, not yours. And `let _ = Noisy("c");` binds nothing, so the value
drops at the semicolon. [Problem 3](#problem-3) traces all of these.

### The guard's destination { #deeper-spinlock }

In `37k` the same shape guards a lock. Locking hands back a `SpinLockGuard`
(`spinlock.rs`) that borrows the lock, lets you reach the protected data
through it, and unlocks in its `Drop`. "Touch the data only while holding the
lock" stops being a rule you remember and becomes one the borrow checker
enforces, since no reference to the data can outlive the guard.
[Week 10](10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-guard)
builds it.

### `const fn`, and what C does instead { #deeper-const }

A C static initializer allows only constant expressions, never a function
call. So C kernels grow `xxx_init()` routines that fill in what the language
could not, each of which must run before anyone reads its table. C++ added
`constexpr` in 2011, and Rust stabilized `const fn` in 2018, in Rust 1.31.

A `const fn` may use arithmetic, `if`, `match`, loops and other `const fn`s,
but may not allocate or call a function that is not `const`. An array repeat
`[x; 64]` normally needs a `Copy` element; a `const { … }` block around the
element lifts that rule, which is how week 9 builds its process table.

### Run it yourself { #deeper-run }

The [in-class examples](../inclass/week03-examples.html) show every program
from Sep 8 beside its output, and seven broken files beside what `rustc` said.
Press `i` on a program to edit and run it. The
[in-class slides](../inclass/week03-slides.html) are the deck shown that day.

### Practice problems { #problems }

#### Problem 1: Which lines compile? { #problem-1 }

With [`Cpu`](#04r-impl) plus `retire(self)`, and the
[`Rgb565`](#04r-newtype) newtype, which numbered lines compile?

```rust
let cpu0 = Cpu::new(0);
let px = Rgb565::new(1, 2, 3);
cpu0.tick(true);            // 1
let g1 = px.green();        // 2
let g2 = px.green();        // 3
let n = cpu0.retire();      // 4
let m = cpu0.load();        // 5
```

Which line breaks if `Rgb565` loses `Copy`?

<details markdown="1">
<summary>Click to reveal solution</summary>

- **1 fails:** ``error[E0596]: cannot borrow `cpu0` as mutable, as it is not declared as mutable``:
  `&mut self` needs `let mut cpu0`.
- **2 and 3 compile:** `Rgb565` is `Copy`, so each by-value call copies it.
- **4 compiles**, moving `cpu0` into `retire`; **5 fails** with `E0382`.

Without `Copy`, line 2 moves `px`, and line 3 is
``error[E0382]: use of moved value: `px` ``.

</details>

#### Problem 2: Pack and unpack by hand { #problem-2 }

With `Rgb565::new` and `green` as in Essentials, and no calculator:

1. What word does `Rgb565::new(31, 32, 0)` hold?
2. A pixel holds `0x07E0`. What are its red, green and blue?
3. `Rgb565::new(0, 64, 0)` holds `0x0800`. What do `green` and red (the word
   shifted right by 11) report, and why?

<details markdown="1">
<summary>Click to reveal solution</summary>

1. `31 << 11` is `0xF800`, and `32 << 5` is `0x0400`. OR them: **`0xFC00`**.
2. `0x07E0` is `0b00000_111111_00000`. Red, `0x07E0 >> 11`, is **0**. Green,
   `(0x07E0 >> 5) & 0x3F`, is **63**. Blue, `0x07E0 & 0x1F`, is **0**: full
   green.
3. 64 is `0b100_0000`, seven bits, so `64 << 5` is `0x0800`: bit 11, red's
   lowest bit. `green` reads `0x40 & 0x3F` = **0**, and red reads **1**.
   Nothing checked the argument; a constructor that refused bad input would
   return `Option<Rgb565>`.

</details>

#### Problem 3: Predict the drop order { #problem-3 }

With `Noisy` from Essentials and
`fn take(n: Noisy) { println!("take {}", n.0); }`, what does `f()` print?

```rust
fn f() {
    let _a = Noisy("a");
    let b = Noisy("b");
    let _ = Noisy("c");
    {
        let d = Noisy("d");
        take(d);
        let _e = Noisy("e");
        println!("inner end");
    }
    drop(b);
    println!("f end");
}
```

<details markdown="1">
<summary>Click to reveal solution</summary>

```text
drop c
take d
drop d
inner end
drop e
drop b
f end
drop a
```

- `let _ =` binds nothing, so `c` drops at its own semicolon. `_a` and `_e`
  are real bindings; the underscore only silences the unused warning.
- `take(d)` moves `d` into `n`, which drops at `take`'s closing brace.
- `drop(b)` moves `b` into an empty function, where it dies; `_a` drops last.

</details>

#### Problem 4: The compiler as code reviewer { #problem-4 }

`Slot` gains `Pinned { block: u32 }`: a slot the kernel holds in memory, which
must never be evicted.

```rust
fn describe(s: Slot) -> String { /* the match in Essentials, unchanged */ }

fn label(s: Slot) -> &'static str {
    match s { Slot::Empty => "free", Slot::Loading(_) => "reading", _ => "cached" }
}

fn evictable(s: Slot) -> bool { !matches!(s, Slot::Loading(_)) }
```

1. Which fail to compile?
2. For each that compiles, is its answer right for `Pinned`?
3. What single change to `label` makes the compiler flag it?

<details markdown="1">
<summary>Click to reveal solution</summary>

1. Only `describe`, with ``error[E0004]: non-exhaustive patterns:
   `Slot::Pinned { .. }` not covered``.
2. `label` calls a pinned slot "cached": true, but only by luck. `evictable`
   answers `true`, which is **wrong**, and the compiler said nothing.
3. Replace `_` with the variants it stood for,
   `Slot::Clean { .. } | Slot::Dirty { .. }`. Adding `Pinned` then breaks the
   build at that line.

Exhaustiveness protects only the matches that allow it. `_`, `matches!` and a
chain of `==` tests all opt out.

</details>

#### Problem 5: Trace guards and fall-through { #problem-5 }

```rust
fn action(slot: Slot, busy: bool) -> &'static str {
    match slot {
        Slot::Dirty { age, .. } if age > 60 => "flush now",
        Slot::Dirty { .. } if !busy => "flush when idle",
        Slot::Clean { .. } | Slot::Empty => "reusable",
        _ => "wait",
    }
}
```

1. What does it return for a dirty slot of age 90 while busy, one of age 10
   while busy, one of age 10 while idle, and `Loading(4)` while idle?
2. Swap the first two arms. Do any of the four answers in (1) change? Which
   dirty slot now gets a different answer?
3. Delete `_ => "wait"`. What does rustc say?

<details markdown="1">
<summary>Click to reveal solution</summary>

1. **"flush now"**: arm 1's guard holds. **"wait"**: arm 1's guard fails, so
   matching goes on; arm 2's fails too (busy), arm 3 does not fit, and `_`
   answers. **"flush when idle"**: arm 2. **"wait"**: only `_` fits `Loading`.
2. None of the four in (1) changes. A dirty slot older than 60 while idle,
   such as age 90, now gets "flush when idle" instead of "flush now". Arms
   are tried top to bottom, and the first whose pattern and guard both succeed
   wins.
3. ``error[E0004]: non-exhaustive patterns: `Slot::Loading(_)` not covered``.
   Add a `Loading` arm and rustc names `Slot::Dirty { .. }` next: a young dirty
   slot on a busy system fails both guards.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| Struct | Named fields bundled into one type | `04r`, `34k` |
| Method / associated function | Called with `.` on a value / with `::` on the type | `04r` onward |
| `Copy` | Assignment and by-value `self` leave the original usable | `04r`, `05r`, `34k` |
| Newtype | One-field tuple struct: a new type, the same bits | `04r`, `33k` |
| Mask | A constant whose ones select a field | `04r`, `33k` |
| `const fn` | A function the compiler can also run | `04r`, `34k` |
| `#[repr(C)]` | Fields in written order, at C's offsets | `04r`, `20a`, `35k` |
| `Drop` / guard | Release at the owner's end; a guard's life is the hold | `04r`, `37k` |
| Enum / variant | Exactly one of a fixed set of cases | `05r`, `34k`, `40k` |
| Exhaustive `match` | Arms cover every variant, or `E0004` | `05r` onward |
| Match guard | An `if` on a `match` arm; if it fails, matching goes on to the next arm | `05r` |
| `Option<T>` | `Some(T)` or `None`: absence with its own type | `05r`, `07r`, `36k` |

## Further reading { #reading }

- [Rust for Systems](../guides/rust-for-systems.md#structs-and-impl-blocks):
  structs and `impl`, [`const fn`](../guides/rust-for-systems.md#const-fn),
  [the newtype pattern](../guides/rust-for-systems.md#the-newtype-pattern),
  [`#[repr(C)]`](../guides/rust-for-systems.md#reprc-and-why-layout-matters),
  [Drop](../guides/rust-for-systems.md#drop) and
  [the guard pattern](../guides/rust-for-systems.md#the-guard-pattern); then
  [enums](../guides/rust-for-systems.md#enums-are-tagged-unions),
  [`Option<T>`](../guides/rust-for-systems.md#optiont) and
  [exhaustive `match`](../guides/rust-for-systems.md#match-is-exhaustive).
- [Midterm 1](../assignments/midterm-1.md) and
  [Practice Set 1](../assignments/practice-set-01.md), Part A.
- [*The Rust Programming Language*](https://doc.rust-lang.org/book/), chapters
  5 and 6.
- *The Rust Reference*: [Type layout](https://doc.rust-lang.org/reference/type-layout.html)
  (what each `repr` promises) and
  [Destructors](https://doc.rust-lang.org/reference/destructors.html) (drop
  order).
- *The Rustonomicon*, [Data Representation in Rust](https://doc.rust-lang.org/nomicon/data.html):
  field reordering and niches.
- C. A. R. Hoare, "Null References: The Billion Dollar Mistake" (QCon London,
  2009).
