# Week 10 · Locks, Semaphores, and Turning the MMU On

> **Thu Oct 29** `37k_spinlocks`, `38k_semaphores` · **Fri Oct 30** `39k_virtual_memory`
>
> Read **Essentials** before Tuesday: it is what Thursday and Friday assume.
> **Going deeper** is optional and is not on the exam.

[Slides](10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on-slides.html){ .md-button }
[Thursday prep](../prep/10-cs326-2026-10-29-prep-spinlocks-and-semaphores.md){ .md-button }
[Friday prep](../prep/10-cs326-2026-10-30-prep-virtual-memory.md){ .md-button }

## This week { #this-week }

In `40k` the whole filesystem sits behind one lock, and from `43k` on every
address the kernel uses passes through a page table. Both rest on one change
this week: the kernel stops assuming nothing else is looking.

On Thursday something else is: another hart, or an interrupt, arriving between
two of your instructions. You build a spinlock from one atomic instruction and
a counting semaphore on it, and the kernel gets a heap. On Friday the
hardware looks: you identity-map the kernel, pack `satp`, and install the
table. `33k` came before Midterm 1 and the break, so Friday's part opens with a
recap.

By Friday night the kernel has a lock, a semaphore two owners share through
`Arc`, and a page table of its own in `satp`.

---

## Essentials { #essentials }

### Thursday · `37k` Spinlocks { #thu-37k }

In `46k` the shell's `ls`, `cd` and `mkdir` each take the filesystem's lock.
`37k_spinlocks` builds that lock from one atomic instruction.

#### A race, built by hand { #37k-race }

Your `32k` allocator pops a page: read the head, then move the head to that
page's link. On two harts, pages named by their last four hex digits:

```text
      hart A               hart B               head
1     reads head: 3000                          3000
2                          reads head: 3000     3000
3     head = its link                           2000
4                          head = its link      2000
      both return page 3000
```

Nothing keeps B out of A's gap. The result depends on how A and B interleave:
a **race condition**. Code that must not run in two
flows at once is a **critical section**, and keeping it to one flow is
**mutual exclusion**. One hart is no cure: an interrupt can land in the gap.

#### One indivisible step { #37k-cas }

The hardware closes the gap with an **atomic** read-modify-write: a load, a
decision and a store nothing can split. Here is **compare-and-exchange**
(CAS) on a one-shot flag:

```rust
use core::sync::atomic::{AtomicUsize, Ordering::Relaxed};
const NOBODY: usize = usize::MAX;
static FIRST: AtomicUsize = AtomicUsize::new(NOBODY);

match FIRST.compare_exchange(NOBODY, hart, Relaxed, Relaxed) {
    Ok(_) => report("first"),            // we turned NOBODY into our id
    Err(winner) => report_after(winner), // it already held another id
}
```

Read `compare_exchange(NOBODY, hart, ..)` as "if `FIRST` still holds `NOBODY`,
make it `hart`, in one step". So exactly one hart ever sees `Ok`. A **spinlock** claims a flag this way, and a loser tries again until
the holder lets go.

Compilers and CPUs reorder memory accesses. Take a lock with **Acquire**, so no later access moves above it; give it back
with **Release**, so no earlier access moves below it. Paired, they carry one
holder's writes to the next. `FIRST` guards no data, so `Relaxed` suffices.

#### Shared, yet mutable: `UnsafeCell`, `Send` and `Sync` { #37k-cell }

A plain `static` is read-only: `TOTAL += 1` on `static TOTAL: u64` fails with
"cannot assign to immutable static item". **`UnsafeCell<T>`** is the way
through: its safe `get(&self)` returns a `*mut T` from a plain `&`, which is
**interior mutability**. The cell enforces nothing; a lock beside it keeps the
writers to one.

A `static` must be **`Sync`**, safe to share by `&` between threads; **`Send`**
means safe to move to another thread. Wrap an `UnsafeCell` in a `static`, and
rustc refuses:

```rust
pub struct Mailbox { slot: UnsafeCell<u64> }
static INBOX: Mailbox = Mailbox { slot: UnsafeCell::new(0) };
// error[E0277]: `UnsafeCell<u64>` cannot be shared between threads safely
```

The answer is a signed promise, `unsafe impl Sync for Mailbox {}`. A generic
lock signs only for `T: Send`, or a hart could clone an `Rc` out of it and
carry it off, and `Rc`'s count is not atomic.

#### The guard unlocks for you { #37k-guard }

Close a valve by hand, and one early `return` leaves it open. **RAII** ties
the close to a value: `valve.open()` returns an `Open`, whose `Drop` runs on
every path out of the scope:

```rust
pub struct Open<'a> { valve: &'a Valve }
impl Drop for Open<'_> {
    fn drop(&mut self) { self.valve.close(); }
}

let _open = valve.open();    // the valve stays open while _open lives
fill_tank();                 // close() runs at the brace, on every way out
```

A lock's **guard** is this shape: `lock()` returns one, `Deref` and `DerefMut`
make `*g` the data, and its `Drop` unlocks. Read `let _open` as "alive until
the closing brace". Write `let _ = valve.open();` and `_` binds nothing: the
valve closes at the semicolon, before `fill_tank`, without a warning. In rv6
a panic aborts, so no guard drops.

#### Interrupts off while you hold it { #37k-interrupts }

On one hart, a spinning waiter and the holder cannot both run:

```text
kernel code   takes lock L and starts its critical section
interrupt     the hart jumps to the handler, mid-section
handler       tries L: held, so it spins
              L's holder resumes only when the handler returns: never
```

Hence the rule: **a lock an interrupt handler also takes is held with
interrupts off.** xv6 turns them off under every lock. rv6 survives without,
because no handler takes one: `45k`'s console passes bytes through a ring with
no lock.

> **The one thing to get right:** the banner prints, then silence, then a QEMU
> timeout blaming the stack, which the banner rules out. The test holds the
> lock and tries again, expecting a refusal; a try that waits spins forever on
> its own hart's lock.

### Thursday · `38k` Semaphores and the heap { #thu-38k }

In `46k` the shell keeps its directory in a `Vec` and each line in a `String`,
both on a heap. `38k_semaphores` counts permits on your lock and turns the heap on.

#### Permits: P and V { #38k-permits }

A **semaphore** is a count of **permits**. **wait** (Dijkstra's P) takes one,
**post** (V) returns one, and the count never goes below zero. Starting at 1
makes a lock, a **binary semaphore**; starting at N meters N interchangeable
things, a **counting semaphore**. Three DMA channels, five transfers:

```text
                  count
start             3
A waits           2      A takes a channel
B waits           1
A posts           2      A is done
C, D wait         0
E waits           0      refused: none left
```

This week's wait never sleeps, since nothing else could run to post: at zero
it refuses ([why](#exam-lost-wakeup)). The count lives behind
your `37k` lock.

#### The heap arrives { #38k-heap }

`Box`, `Vec` and `Arc` come from the `alloc` crate, which a `no_std` kernel
pulls in with `extern crate alloc;`. But `alloc` owns no memory: with no
allocator named, rustc stops with "no global memory allocator found but one is
required". Name one with `#[global_allocator]` on a static whose type
implements `GlobalAlloc`. rv6's given `KernelHeap` (`kheap.rs`) answers every
request with a whole `kalloc` page, so the page allocator must exist before
the first `Box`:

| You write | Bytes requested | What you get |
|---|---|---|
| `Box::new(7u64)` | 8 | a page, 4,088 bytes idle |
| `Arc::new(x)`, `x` 16 bytes | 32: two counts, then `x` | a page |
| `Vec::<u8>::with_capacity(5000)` | 5,000 | null, then a panic |

#### `Arc`: one value, many owners { #38k-arc }

**`Arc<T>`**, atomically reference-counted, shares one heap value among owners
until the last lets go:

```rust
let a = Arc::new(Gauge::new());          // one Gauge on the heap; count 1
let panel = Panel { g: Arc::clone(&a) }; // count 2
let log = Arc::clone(&a);                // count 3, still one Gauge
drop(a);                                 // count 2: the first owner is not special
let n = Arc::strong_count(&log);         // n == 2
drop(panel); drop(log);                  // count 0: Gauge dropped, page freed
```

Read `Arc::clone(&a)` as "one more pointer, one more on the count": nothing is
copied. `Arc` hands out only `&T`, so
`a.level += 1` fails with "cannot assign to data in an `Arc`". Shared data that
changes needs a lock inside.

> **The one thing to get right:** the third wait succeeds too:
> `[fail] no permits should remain after taking both`. The count went to −1: a
> permit that never existed was handed out.

### Friday · `39k` Turning the MMU on { #fri-39k }

From `43k` on, every kernel access goes through a page table, and in `48k`
each program gets its own. `39k_virtual_memory` builds the kernel's table.

#### The next fetch is translated { #39k-paradox }

In `33k`, on Oct 9, only software read your tree: building a table takes only
stores, and using one is the hardware's job. Once `satp` names
the root, the MMU
[walks](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#33k-walk) the tree
on every access and enforces the leaf's R, W and X.

Hence the **bootstrap paradox**, like renaming the streets while you drive
them: the instruction after the switch is fetched through the new table, at
the same `pc` and `sp`. If `pc`'s page is not mapped executable there, that
fetch faults.

The way out is an **identity map**, `va == pa` for every page the kernel uses:
translation is on, but each answer equals its question. Map anything the
kernel will fetch, load or store after the switch, devices included: whatever
you leave out stops existing. Give each region a start and a length, not an
end.

#### `satp` by hand { #39k-satp }

**`satp`** has three fields. MODE sits in bits 63..60 (8 is Sv39, 0 is off),
and an address-space ID in 59..44 (0 in rv6). Bits 43..0 hold the root's
**page number**: its physical address without the low 12 bits, as in a
[PTE](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#33k-encode). For a
root at `0x8052_1000`:

```text
root table at            0x0000_0000_8052_1000
drop the low 12 bits     0x0000_0000_0008_0521   the PPN: three hex digits gone
MODE 8 in bits 63..60    0x8000_0000_0000_0000
both fields together     0x8000_0000_0008_0521   the value to install
```

Read it upward to decode, as
[Week 7](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#exam-satp) did for
`0x8000_0000_0008_7FFF`. MODE 0 is legal, "translate nothing", so a wrong mode
never faults.

#### Two instructions, and the TLB { #39k-tlb }

The switch is two given instructions:

```asm
csrw  satp, t0           # the value above; the next fetch is translated
sfence.vma zero, zero    # discard every cached translation
```

The second is for the **TLB**, the MMU's cache of recent translations, which
spares most accesses the walk. It is not coherent with memory:
rewrite a PTE and the cached copy can stay. **`sfence.vma`** discards cached
translations and orders earlier page-table stores before later walks:

```text
load 0x8000_2F00    miss: walk, cache page 0x8000_2000 -> 0x8000_2000
leaf now names page 0x8060_0000; load again: may hit, still 0x8000_2F00
sfence.vma; load again: miss, walk, 0x8060_0F00
```

Fence after writing `satp`, and after changing an entry the hardware may have
used. A table built before it is installed needs none. From `48k` the
trampoline's switch between two live tables fences on both sides.

#### Silence, and checking first { #39k-verify }

A wrong table fails in silence: even the report of the failure needs the
translation that broke.

A pilot runs the checklist on the ground, not after takeoff, and `39k`'s test
does the same: it inspects your table with translation still off, so a mistake
prints a `[fail]` line instead of going dark. When a failure would be silent, check before the
dangerous step.

`39k` runs in machine mode, which translation never touches, so the table
carries nothing yet; from `43k`, in supervisor mode, it carries every access.

> **The one thing to get right:** every mapping checks out, then
> `[fail] make_satp: wrong root page number`. The low 44 bits hold a page
> number, not an address. An address there names a root 4,096 times higher,
> about 8 TiB up, where there is no memory at all.

### For the exam { #exam }

*Not needed on Thursday or Friday. On Midterm 2.*

**Test-and-set versus CAS** · *Midterm 2.* Test-and-set always writes `true`
and returns the old value; CAS writes only on a match, so it works beyond
flags. Spinning test-and-set writes every try,
bouncing one cache line between spinners. **Test-and-test-and-set**
spins on a plain load until the flag reads free, then tries the atomic. A
separate atomic load and store still leave a gap.
{ #exam-tas }

**Deadlock** · *Midterm 2.* It needs mutual exclusion, hold-and-wait, no
preemption and a circular wait. Opposite lock orders on two harts close the
circle; one global order breaks it. On one hart, a
lock and a [handler](#37k-interrupts) can close it; interrupts off break that.
{ #exam-deadlock }

**The lost wakeup** · *Midterm 2.* A blocking wait that tests "count is 0",
then sleeps, has a gap: a post landing there wakes nobody, and the
waiter sleeps beside a free permit. The cure: test under a lock,
become `Sleeping` before releasing it, and retest in a `while`. rv6's
`try_wait` refuses at zero and never sleeps: no gap.
{ #exam-lost-wakeup }

**Bounded buffers** · *Midterm 2.* N slots: `empty` = N, `full` = 0,
`mutex` = 1; `empty + full` = N between operations.
{ #exam-bounded }

```text
producer   P(empty)  P(mutex)  put   V(mutex)  V(full)
consumer   P(full)   P(mutex)  take  V(mutex)  V(empty)
```

Take the counting semaphore first: a producer blocked on `empty`, holding
`mutex`, stalls every consumer.

**Megapages, and 66 pages** · *Midterm 2.* Identity-mapping 128 MiB in 4 KiB
pages takes 32,768 leaves in 64 level-0 tables, plus a level-1 table and the
root: 66 pages. A level-1 leaf maps a 2 MiB **megapage**, so the root and one
level-1 table of 64 leaves suffice: 2 pages.
{ #exam-megapages }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday or Friday, and nothing here is on
the exam.*

### What a CAS compiles to { #deeper-atomics }

`riscv64gc` includes the A extension, with two kinds of atomic. An **AMO**, such
as `amoor.w`, reads a word, combines it with a register and writes it back in
one instruction, returning the old value. **LR/SC** is a pair: `lr.d` loads and
reserves an address, and `sc.d` stores only if nothing touched it since.

Compile the one-shot `FIRST` with `-O` for `riscv64gc-unknown-none-elf`, and it
becomes an `lr.d`, `bne`, `sc.d`, `bnez` retry loop. A CAS from `false` to
`true` on an `AtomicBool` becomes one `amoor.w.aq` instead, `.aq` for
Acquire: OR-ing in a bit
already set changes nothing, so on a bool, CAS *is* test-and-set. It works on
the containing word, with shifts around it, because RV64A has no byte-wide
AMOs.

CAS compares values, so a word that went A → B → A between your read and your
CAS looks untouched: the **ABA problem**, and why lock-free lists carry version
counters.

### Ordering on one hart { #deeper-ordering }

RISC-V's memory model lets one hart's stores reach other harts out of order.
A single hart sees its own accesses in order, yet the compiler still moves
loads and stores it sees no reason to keep, and an interrupt handler sees the
result. A `Release` store compiles to `fence rw, w`, then the store. A losing
CAS changed nothing, so its failure ordering owes the data nothing. And any
"is it held?" check is stale the instant it returns: a plain `load` of the
flag followed by a `store` rebuilds the race out of an atomic.

### What the heap costs { #deeper-heap }

More than a page fails, and "memory allocation of 5000 bytes failed" never
shows: the test's panic handler prints only `OSLINGS:FAIL (panic)`.

Push ten `u64`s onto a `Vec`, and its capacity grows 4, 8, 16, taking three
pages in turn. Each growth allocates the new block, copies, then frees the old,
so two pages are live at that instant; the final block is 128 bytes of a page.
A real allocator is a project of its own: Linux carves objects out of
buddy-allocated pages with SLUB, and xv6 has no kernel heap at all. rv6's is
also unsafe on two harts, since `kalloc`'s free list has no lock and two
allocations could return [the same page](#37k-race). The cure is to put the
free list in a `SpinLock`.

### What a table costs { #deeper-kernel-map }

A page table's size follows how scattered its pages are, not how many there
are. Two 4 KiB pages in one 2 MiB region share a level-0 table. Two pages in
different 2 MiB regions need two level-0 tables, and two pages in different
1 GiB regions need two level-1 tables as well. A few device pages spread
across the low gigabyte can cost more tables than a contiguous megabyte of RAM.

A hardened kernel also splits RAM by permission: code R X, data R W, so no
page is both writable and executable. That is **W^X**, and each split costs
one more region boundary, placed from a linker symbol. xv6 pays for one
(below).

### When you must flush { #deeper-flush }

RISC-V needs `sfence.vma` after writing `satp`, after changing an entry the
hardware may have used, and even after making an invalid entry valid: a hart
may remember that an address was unmapped. rv6 never fences while building a
table, correctly, by an invariant: a table is complete before it is installed.
Add lazy allocation or copy-on-write and every edit needs a fence. QEMU never
remembers a failed walk, so a missing fence after adding a page passes every
test here and can fail on a real board.

### Reading the silence { #deeper-silence }

When the kernel goes quiet after the switch, attach GDB and read four
registers. `satp` starting with 8 says the switch happened. `scause` 12 is an
instruction page fault, the table refusing a fetch. `stval` holds the address,
and a `pc` stuck at 0 means the fault trapped to an unset vector and faulted
again. The spec says a root that points at no memory gives an access fault,
`scause` 1; QEMU 10 reports that case as 12 too, so check `satp` itself before
blaming a mapping. [QEMU and GDB](../guides/qemu-gdb.md#diagnostic-playbook)
has the playbook.

### How xv6 and Linux do it { #deeper-others }

xv6 splits its kernel map at `etext`, the end of `.text`: code R X, the rest
R W. That is W^X for one extra mapping. Linux runs at a high virtual address
but is loaded wherever the bootloader chose, so the fetch after its switch
cannot translate to itself. On RISC-V it points `stvec` at the high address of
that next instruction first: the fetch faults, and the trap lands exactly
there. Linux also tags TLB entries with ASIDs, so a process switch need not
flush, and asks other harts to flush by interrupt, since `sfence.vma` reaches
only its own.

### Practice problems { #problems }

#### Problem 1: Lost updates, counted { #problem-1 }

Two harts share `static mut HITS: u64 = 0` with no lock, and each runs
`HITS += 1` twice. Each increment compiles to `ld`, `addi`, `sd`.

(a) Which final values are possible? (b) Give an interleaving for the
smallest. (c) Which fixes it: an `AtomicU64` read with `load` and written with
`store`, `fetch_add(1, ..)`, or a lock around each increment?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)** 2, 3 or 4. Each lost update costs one.

**(b)** A's stale last store erases both of B's increments:

```text
A: ld 0, addi, sd 1, ld 1, addi          HITS = 1, A holds 2
B: ld 1, addi, sd 2, ld 2, addi, sd 3    HITS = 3
A: sd 2                                  HITS = 2
```

**(c)** `fetch_add`, one `amoadd.d` with no gap inside, and the lock, which makes
the three steps a critical section. An atomic `load` then an atomic `store` is
two indivisible steps with a gap between them: the same race, with atomics.

</details>

#### Problem 2: When does the guard drop? { #problem-2 }

`std::sync::Mutex` has a guard like this week's. The mutex starts at 0.

```rust
fn tally(m: &Mutex<u32>) -> bool {
    *m.lock().unwrap() += 1;          // B
    let n = *m.lock().unwrap();       // C
    let mut g = m.lock().unwrap();    // D
    *g += n;                          // E
    drop(g);                          // F
    let _held = m.lock().unwrap();    // G
    m.try_lock().is_ok()              // H
}
```

(a) When is the mutex released each time? What does `tally` return, and what
does the mutex hold? (b) Change G to `let _ = m.lock().unwrap();`. What
happens, and what would happen with a guard of your own type?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)** B's guard is a temporary, dropped at B's semicolon. C copies the `u32`
out, so its guard also drops at the semicolon, with `n` = 1. D's guard lives
until F; E makes the value 2. G's lives to the end, so H finds the mutex held:
`tally` returns `false`, and the mutex holds 2.

**(b)** It does not compile. rustc's `let_underscore_lock` lint, an error by
default, says "non-binding let on a synchronization lock". The lint knows only
the standard library's locks: with your own guard type the line compiles
silently, the guard drops at once, and H returns `true`.

</details>

#### Problem 3: A bounded buffer of two { #problem-3 }

Use the [bounded buffer](#exam-bounded) with N = 2 and a blocking P.

(a) The producer offers three items; then one consumer runs once. Give `empty`
and `full` after each step, and say where the third production waits.

(b) Start over, empty. A consumer's first two lines are swapped to
`P(mutex); P(full)`, and it runs before any producer. Show the deadlock.

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)**

| After | `empty` | `full` |
|---|---|---|
| production 1 | 1 | 1 |
| production 2 | 0 | 2 |
| production 3 | waits in `P(empty)`, holding nothing | 2 |
| the consumption | 1, taken at once by production 3 | 1 |
| production 3 finishes | 0 | 2 |

The third producer waits before `mutex`, so the consumer can still get in, and
its `V(empty)` is exactly what the producer needed.

**(b)** The consumer takes `mutex`, then waits on `full` = 0 while holding it.
The producer passes `P(empty)` and waits on `mutex`. Each needs what only the
other can give: a circular wait. Consumers, too, take the counting semaphore
first.

</details>

#### Problem 4: `satp` both ways { #problem-4 }

(a) A root sits at `0x8043_7000`. What goes in `satp`? (b) Decode
`0x8000_0000_0008_7FC2`: is the root in RAM? (c) Decode
`0x0000_0000_0008_0437`: what happens once it is installed? (d) Decode
`0x8000_0000_8043_7000`: where does the hardware look for the root?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)** `0x8043_7000 >> 12` is `0x8_0437`; with 8 at bit 60,
`0x8000_0000_0008_0437`.

**(b)** MODE 8, Sv39. The low 44 bits are `0x8_7FC2`, so the root is at
`0x87FC_2000`, inside `0x8000_0000..0x8800_0000`: yes.

**(c)** MODE 0, Bare: QEMU translates nothing, so the kernel runs on and
nothing says the table was never used. (The current privileged spec asks for
zeros beside MODE 0 and leaves this pattern UNSPECIFIED.)

**(d)** The low 44 bits hold `0x8043_7000`, an address where a page number
belongs. Three zero digits appended put the root at `0x804_3700_0000`, about
8 TiB up, where there is nothing: the first translated access fails inside the
walk.

</details>

#### Problem 5: Count the tables { #problem-5 }

A small kernel identity-maps RAM from `0x8000_0000` to `0x8040_0000` in 4 KiB
pages, plus one device page at `0x2000_0000`. (a) How many page-table pages,
root included? (b) How many if RAM uses 2 MiB megapages, and why not the
device page? (c) How many for just the pages `0x801F_F000` and `0x8020_0000`?

<details markdown="1">
<summary>Click to reveal solution</summary>

**(a)** 6. RAM's 1,024 pages fill two level-0 tables below one level-1 table,
under root entry 2. The device is under root entry 0, level-1 entry 256: one
level-1 and one level-0 table. With the root, 1 + 3 + 2 = 6.

**(b)** 4. RAM becomes two level-1 leaves, and its level-0 tables vanish. The
device keeps a 4 KiB page, since a 2 MiB leaf would also map every device
register beside it.

**(c)** 4: the root, a level-1 table and two level-0 tables. The pages are
adjacent but straddle a 2 MiB boundary, level-1 entries 0 and 1.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| Race condition | A result that depends on how two flows interleave | `37k`, Midterm 2 |
| Critical section | Code that must not run in two flows at once | `37k`, `40k` |
| Compare-and-exchange | Change a value only if it still holds what you expect, in one step | `37k` |
| Acquire / Release | The pair that carries one holder's writes to the next | `37k` |
| Interior mutability | A `&mut` from a `&`, through `UnsafeCell` | `37k`, `38k` |
| `Send` / `Sync` | Safe to move / safe to share between threads | `37k` |
| RAII guard | A value whose `Drop` releases what it holds | `37k`, `40k`, `46k` |
| Semaphore | A count of permits: P takes, V returns, never below zero | `38k` |
| `#[global_allocator]` | Names the `GlobalAlloc` behind `Box`, `Vec` and `Arc` | `38k`, `46k` |
| Identity map | `va == pa`, so turning translation on changes no address | `39k`, `43k` |
| `satp` | MODE in bits 63..60, the root's page number in 43..0 | `39k`, `48k` |
| TLB, `sfence.vma` | The MMU's cache of translations, and the fence that clears it | `39k`, `48k` |

## Further reading { #reading }

- [Unsafe Rust and no_std](../guides/rust-unsafe-nostd.md#unsafecell):
  `UnsafeCell`, [`Send` and `Sync`](../guides/rust-unsafe-nostd.md#send-and-sync)
  and [`core`, `alloc`, and `std`](../guides/rust-unsafe-nostd.md#core-alloc-and-std).
- [Rust for Systems: the guard pattern](../guides/rust-for-systems.md#the-guard-pattern).
- [Sv39 Paging: the `satp` register](../guides/sv39-paging.md#the-satp-register)
  and [`sfence.vma` and the TLB](../guides/sv39-paging.md#sfencevma-and-the-tlb).
- [QEMU and GDB: diagnostic playbook](../guides/qemu-gdb.md#diagnostic-playbook).
- [Midterm 2](../assignments/midterm-2.md), and
  [Practice Set 2](../assignments/practice-set-02.md) Parts B and C.
- Mara Bos, [*Rust Atomics and Locks*](https://marabos.nl/atomics/), chapters
  1–4.
- [The xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf),
  chapters 3 and 6.
- Arpaci-Dusseau and Arpaci-Dusseau,
  [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/),
  chapters 19 and 28–32.
