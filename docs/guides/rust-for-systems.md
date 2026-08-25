# Rust for Systems Programming

This is the Rust reference for CS 326. It is written for the moment mid-exercise
when you know what you want the machine to do but the compiler will not let you
say it — and for the week before the midterm, when you need the Rust half of the
material in one place. Every rule here is illustrated with a line from the rv6
sources you are building, not with a toy example, because the toy examples are
never the ones that bite. Module 1 (`00r`–`21r`) teaches these ideas one at a
time in the `warmup` crate; this page is where they live afterwards. For the
`unsafe`, raw-pointer, and `no_std` half of the language, see
[Unsafe Rust and no_std](rust-unsafe-nostd.md).

## The map

Each Module 1 Rust exercise exists because one kernel exercise cannot be written
without it. If you are stuck on a kernel exercise, the row tells you which
warmup to reread.

| Module 1 | Idea | First kernel exercise that needs it |
|---|---|---|
| `02r_ownership` | ownership, moves, `Copy`, drop | `32k` — the physical page allocator |
| `03r_borrowing` | `&`, `&mut`, the aliasing rule, lifetimes | `37k` — spinlock guards |
| `04r_structs_impl` | `struct`, `impl`, `const fn`, newtypes, `repr` | `33k` `Pte`, `35k` `Context` |
| `05r_enums_match` | `enum`, `Option`, exhaustive `match` | `34k` `ProcState`, `40k` `InodeKind` |
| `06r_collections` | arrays, slices, `Vec`, iteration | the `PROCS` table, the fd table |
| `07r_traits` | traits, generics, `impl Trait`, dispatch | `36k` `Scheduler`, `46k` `Out` |
| `08r_errors` | `Result`, `?`, error enums | `40k` `dirlookup`, `49k` `exec` |
| `21r_unsafe_bridge` | `unsafe`, raw pointers, MMIO | `31k` onward — see [Unsafe Rust and no_std](rust-unsafe-nostd.md) |

All rv6 code is Rust **edition 2021**. Line references below are to the
reference kernel sources (`rv6/src/*.rs`); your files will differ by a few lines
once you have written your own bodies, but the shapes are identical.

---

## 1. Ownership and moves

### The rule

1. Every value has exactly one **owner** — the binding responsible for it.
2. There is one owner at a time.
3. When the owner goes out of scope the value is **dropped** and its resources
   are released, right there, at a line you can point to.

There is no garbage collector and no `free()`. The compiler works out where
each value dies and inserts the cleanup. This is why Rust is the language rv6
is written in: the bug that destroys allocators is handing the same page to two
callers, and rule 2 is that bug stated as a compiler error.

### Moving

Assigning a value, passing it to a function, or returning it **moves** it. The
old binding is dead from that point on, and using it is error `E0382`.

```rust
let free = new_free_list(64);
let (free, page) = take_page(free);   // `free` moved in, a new one moved back out
```

A move is not a memcpy of the data — for a `Vec` it copies three machine words
(pointer, length, capacity) and marks the source dead. The heap buffer never
moves. Moves are free at run time; the whole cost is at compile time.

### `Copy` types do not move

A type that is `Copy` is duplicated instead of moved, so the original stays
alive. Everything that is a plain bit pattern with no cleanup can be `Copy`:
integers, `bool`, `char`, raw pointers, shared references, and any struct whose
fields are all `Copy` and that says so. rv6 uses this deliberately for its small
table entries:

```rust
#[derive(Clone, Copy)]
pub struct File {          // file.rs:39
    pub kind: FileKind,
    pub inum: usize,
    pub off: usize,
    pub readable: bool,
    pub writable: bool,
}
```

Because `File` is `Copy`, the per-process file table is a plain array and
`getfile` can hand back a *copy* of the entry rather than a borrow:

```rust
unsafe fn getfile(p: *mut Proc, fd: usize) -> Option<File> {   // syscall.rs:312
    if fd >= NOFILE { return None; }
    let f = (*p).ofile[fd];        // a copy — no borrow of `*p` outlives this line
    if f.kind == FileKind::None { None } else { Some(f) }
}
```

That copy is what lets `sys_read` mutate the stored offset a few lines later
(`(*p).ofile[fd].off += n;`, syscall.rs:505) without the borrow checker
objecting. If `File` were not `Copy`, `getfile` would have to return a borrow
and `sys_read` would be stuck. The same trick appears in `fs.rs:195`, where
`unlink` copies the `DirEnt` out of the array before mutating two different
inodes through `&mut self`.

`Pte` (vm.rs:26), `Context` (swtch.rs:6), `ProcState` (proc.rs:18) and
`DirEnt` (fs.rs:30) are all `Copy` for the same reason.

### Drop

When an owner goes out of scope, `Drop::drop` runs if the type has one. rv6 has
exactly one interesting `Drop`, and it is the point of the spinlock:

```rust
impl<T> Drop for SpinLockGuard<'_, T> {   // spinlock.rs:71
    fn drop(&mut self) {
        self.lock.unlock();
    }
}
```

You never call `unlock()`. The lock is released when the guard's owner goes out
of scope — including on an early `return`, which is where hand-written
lock/unlock pairs go wrong. If you want it released sooner, `drop(guard)` ends
the scope by hand; the shell does this at `shell.rs:102` so it is not holding
the filesystem lock while it allocates a `String`.

### Where ownership stops

Below a certain level there are no owners, only addresses the hardware gave
you. The page allocator is that level. `kalloc` hands out a `*mut u8` — a raw
pointer, which is `Copy`, carries no ownership, and is never dropped:

```rust
pub unsafe fn kalloc() -> *mut u8 {   // kalloc.rs:40
    let r = FREELIST;
    if !r.is_null() {
        FREELIST = (*r).next;
    }
    r as *mut u8
}
```

Nothing in that function is checked by the borrow checker. Calling `kfree` twice
on the same page corrupts the free list exactly the way C would. This is honest
and it is the point: `unsafe` is where you take over the proof obligation, and
everything above `kalloc` — page tables, processes, the filesystem — gets to be
safe *because* this one module is not. See
[Unsafe Rust and no_std](rust-unsafe-nostd.md) for the rules that apply inside
those blocks.

> **Where you need this:** `32k` — the physical page allocator (`kalloc.rs`).

---

## 2. Borrowing: `&`, `&mut`, the aliasing rule, lifetimes

### Two kinds of borrow

- `&T` — a **shared** borrow. Read-only. Any number may exist at once.
- `&mut T` — an **exclusive** borrow. Read and write. While it exists it is the
  *only* live path to the value.

Read `&mut` as *exclusive*, not "mutable". What the compiler enforces is not
that you may write; it is that nobody else may even look.

### The aliasing rule

> At any point in the program, for any value: either any number of `&T`, or
> exactly one `&mut T`. Never both.

That single sentence is the borrow checker. Every `E0499` and `E0502` you will
see is this rule, restated for your specific code.

A borrow lasts from where it is created to its **last use**, not to the end of
the block (this is non-lexical lifetimes, and it is why moving a `println!`
around can make an error appear or vanish). The kernel filesystem is written
around it. `dircreate` looks like it holds a borrow of `self.inodes[dir]` across
a call to `self.alloc()`, which needs `&mut self` — but it does not, because
each statement finishes its borrow before the next begins:

```rust
let mut slot = None;
for i in 0..NDIRENT {
    if !self.inodes[dir].entries[i].used {   // fs.rs:134 — borrow ends on this line
        slot = Some(i);
        break;
    }
}
let slot = slot.ok_or(FsError::DirFull)?;    // fs.rs:139 — `slot` is a usize, not a borrow
let inum = self.alloc(kind)?;                // fs.rs:141 — free to take &mut self
```

Had the loop written `let e = &mut self.inodes[dir].entries[i];` and kept `e`
alive across line 141, that is `E0499` and there is no way around it except the
rewrite above. **Store an index, not a reference**, is the single most useful
habit for kernel code in Rust.

### Slices are borrows

`&[T]` is a shared borrow of a contiguous run of elements: a pointer and a
length, two machine words, no copy. `&mut [T]` is the exclusive version. The
kernel's copy routines are written entirely in these terms:

```rust
pub unsafe fn copyin(table: *mut Pte, dst: &mut [u8], mut srcva: usize) -> Result<(), ()>   // vm.rs:291
pub unsafe fn load_segment(table: *mut Pte, image: &[u8]) -> Result<(), ()>                 // vm.rs:196
```

`load_segment` cannot accidentally write to the program image; `copyin` cannot
accidentally read past the end of the caller's buffer, because `dst.len()` came
with the slice. Both facts are free.

### Lifetimes

A lifetime is a compile-time name for "how long this borrow is valid". You
almost never write one, because of **elision**: in `fn puts(&mut self, s: &str)`
the compiler fills them in. You must write one when a *struct* holds a
reference, because there is no rule to guess from. That is exactly the spinlock
guard:

```rust
pub struct SpinLockGuard<'a, T> {   // spinlock.rs:54
    lock: &'a SpinLock<T>,
}
```

Read it as: a `SpinLockGuard<'a, T>` may not outlive the `SpinLock<T>` it
points at. Omit the `'a` and you get `E0106`. The lock method connects the two:

```rust
pub fn lock(&self) -> SpinLockGuard<'_, T> { ... }   // spinlock.rs:22
```

`'_` means "the anonymous lifetime the compiler already inferred" — here, the
lifetime of `&self`. It is not a placeholder for "any"; it is a request that the
compiler write the obvious one for you. The result is that this cannot compile:

```rust
let guard = {
    let lock = SpinLock::new(0i64);
    lock.lock()          // E0597: `lock` does not live long enough
};                       // lock dropped here, guard would dangle
```

`'static` is the lifetime of things that live for the whole program: string
literals (`&'static str`) and statics. The program table uses both:

```rust
pub struct Program {          // exec.rs:564
    pub name: &'static str,
    pub image: &'static [u8],
}
```

The images are `.rodata` baked into the kernel image, so `'static` is the truth,
not a workaround.

### The guard pattern

Put together, the three ideas make the lock:

```rust
impl<T> Deref for SpinLockGuard<'_, T> {      // spinlock.rs:58
    type Target = T;
    fn deref(&self) -> &T { unsafe { &*self.lock.data.get() } }
}
impl<T> DerefMut for SpinLockGuard<'_, T> {   // spinlock.rs:65
    fn deref_mut(&mut self) -> &mut T { unsafe { &mut *self.lock.data.get() } }
}
```

`Deref`/`DerefMut` make the guard behave like the data it protects, and the
lifetime `'a` means a reference obtained through the guard cannot outlive it.
So a use-after-unlock is a compile error rather than a 3 a.m. debugging session:

```rust
pub fn try_wait(&self) -> bool {   // semaphore.rs:16
    let mut count = self.count.lock();   // SpinLockGuard<'_, i64>
    if *count > 0 {                      // Deref
        *count -= 1;                     // DerefMut
        true
    } else {
        false
    }
}                                        // guard dropped -> unlock()
```

```text
  lock()                                          drop(guard)
    │                                                  │
    ├── locked = true ────────────────────────────────►├── locked = false
    │                                                  │
    └──[ guard alive: *count reads and writes here ]───┘
              ^ any &mut i64 taken here is tied to 'a
```

> **Where you need this:** `37k` — spinlocks and their guards (`spinlock.rs`),
> then `38k` semaphores and every `FS.lock()` in the filesystem.

---

## 3. Structs, `impl`, methods, `const fn`, newtypes, `#[repr(C)]`

### Structs and `impl` blocks

A `struct` is data; an `impl` block is the functions that go with it. Methods
take `self` in one of four ways, and the choice is the API:

| Receiver | Means | rv6 example |
|---|---|---|
| `&self` | read the value | `Pte::pa(self)`, `FileSystem::dirlookup` |
| `&mut self` | read and write it, exclusively | `FileSystem::write_at`, `RoundRobin::pick_next` |
| `self` | consume it (only sensible for `Copy` or when finishing with it) | `Pte::flags(self)` — `Pte` is `Copy`, so this copies |
| none | an **associated function**, called as `Type::name()` | `Proc::new()`, `File::console()`, `SpinLock::new()` |

`Proc::new()` and `File::none()` are associated functions, not methods: they
build a value, so there is no `self` yet. Rust has no constructors; `new` is
just a convention.

### `const fn`

A `const fn` can be evaluated by the compiler at compile time. Kernels need this
constantly, because a `static` must be fully initialized before the machine
starts running any code:

```rust
static mut PROCS: [Proc; NPROC] = [const { Proc::new() }; NPROC];    // proc.rs:65
pub static FS: SpinLock<FileSystem> = SpinLock::new(FileSystem::new());  // fs.rs:277
```

There is no startup code that fills those in. `Proc::new()` (proc.rs:49),
`FileSystem::new()` (fs.rs:73), `SpinLock::new()` (spinlock.rs:15),
`Context::zero()` (swtch.rs:25) and `File::none()` (file.rs:54) are all `const
fn` for this one reason: the process table and the filesystem are laid out in
`.bss`/`.data` by the linker, and the kernel boots with them already correct.

Rules of thumb: a `const fn` may do arithmetic, call other `const fn`s, and
construct values. It may not allocate, call trait methods in general, or do
anything the compiler cannot simulate. `RoundRobin::new()` (sched.rs:14) is
`const fn`; `Semaphore::new()` (semaphore.rs:10) is not, and does not need to
be, because semaphores are built at run time.

The `[const { Proc::new() }; NPROC]` syntax is the *inline const* form of an
array repeat. The plain form `[expr; N]` requires the element type to be `Copy`;
`Proc` is not `Copy` (64 of them, each with a 16-entry file table, is not
something you want copied by accident), so the inline const block tells the
compiler to evaluate `Proc::new()` once at compile time and stamp out 64 copies
of the resulting bit pattern.

### The newtype pattern

A newtype is a one-field struct wrapping another type, to give it a name and a
set of operations. `Pte` is the example the whole paging exercise hangs on:

```rust
#[repr(transparent)]
#[derive(Clone, Copy)]
pub struct Pte(pub usize);        // vm.rs:25

impl Pte {
    pub const fn new(pa: usize, flags: usize) -> Pte { Pte(((pa >> 12) << 10) | flags) }
    pub const fn pa(self) -> usize { (self.0 >> 10) << 12 }
    pub const fn flags(self) -> usize { self.0 & 0x3ff }
    pub const fn is_valid(self) -> bool { self.0 & PTE_V != 0 }
}
```

A page table entry *is* a `usize`, but it is a `usize` with a very specific
layout: physical page number in bits 53:10, flags in bits 9:0. The `>> 12 << 10`
shuffle in `Pte::new` is where a bare `usize` version of this code goes wrong.
Wrapping it means the shuffle is written once and the type system stops you
passing a physical address where an entry is wanted. Field `.0` is the wrapped
value, and it is `pub` here so the raw entry can still be inspected.
See [Sv39 Paging](sv39-paging.md) for what the bits mean.

`#[repr(transparent)]` promises that `Pte` has *exactly* the same layout as a
`usize` — same size, same alignment, same ABI. That is what makes `*mut Pte`
usable as a pointer into a real hardware page table.

### `#[repr(C)]` and why layout matters

By default Rust makes no promise about struct field order; it may reorder fields
to reduce padding. That is fine until something outside the compiler reads your
struct. Then you need a `repr`:

| Attribute | Promise | rv6 use |
|---|---|---|
| `#[repr(C)]` | fields in declaration order, C alignment rules | `Context` (swtch.rs:5), `Trapframe` (usermode.rs:33), `Run` (kalloc.rs:6) |
| `#[repr(transparent)]` | identical layout to the single field | `Pte` (vm.rs:25) |
| default (`Rust`) | no promise at all | everything else |

`Context` is the case to remember, because assembly reads it by offset:

```rust
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Context {   // swtch.rs:5
    pub ra: usize,
    pub sp: usize,
    pub s0: usize,
    ...
    pub s11: usize,
}
```

```asm
swtch:
    sd ra,  0(a0)        # swtch.rs:50 — offset 0 is `ra`
    sd sp,  8(a0)        #               offset 8 is `sp`
    sd s0,  16(a0)
    ...
    sd s11, 104(a0)
```

Fourteen `usize` fields, eight bytes each, offsets 0 through 104. Without
`#[repr(C)]` the compiler would be free to put `s11` at offset 0 and `swtch`
would restore the wrong registers into the wrong places — a bug that will not
show up as a compile error and will not show up as a clean crash either. The
`Trapframe` (usermode.rs:33) is the same deal at a larger scale: `uservec` in
the trampoline stores `ra` at offset 40 and `a7` at 168, and those numbers are
correct only because of one attribute.

> **Where you need this:** `33k` — the `Pte` newtype and the Sv39 walk
> (`vm.rs`); `35k` — the `Context` struct that `swtch` reads by offset
> (`swtch.rs`).

---

## 4. Enums, `Option`, exhaustive `match`

### Enums are tagged unions

A Rust `enum` is a value that is exactly one of a fixed set of alternatives, and
the compiler knows which. Most kernel state that would be a `#define`d integer
in C is an enum in rv6:

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum ProcState {   // proc.rs:18
    Unused,
    Runnable,
    Running,
    Sleeping,
    Zombie,
}
```

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum InodeKind { Free, File, Dir }   // fs.rs:11
```

The `derive` list is doing real work and is worth reading:

| Derive | Gives you | Needed because |
|---|---|---|
| `Clone`, `Copy` | duplication instead of moves | these live inside `Copy` table entries |
| `PartialEq`, `Eq` | `==` and `!=` | `states[i] == ProcState::Runnable` (sched.rs:24) |

Without `PartialEq` on `ProcState`, the round-robin scheduler cannot be written
at all.

### Variants can carry data

This is the part with no C equivalent. A variant may hold values, and the
compiler will not let you read them without first checking which variant you
have:

```rust
pub enum RunOutcome {        // usermode.rs:192
    Exited(isize),           // ... and this is the exit status
    Faulted(usize),          // ... and this is scause
    TimedOut,                // ... and there is nothing more to say
}
```

`RunOutcome::Faulted(c)` cannot be confused with `RunOutcome::Exited(c)` even
though both wrap an integer, and you cannot get at `c` without a `match`.

### `Option<T>`

`Option<T>` is just an enum in the standard library:

```rust
enum Option<T> { None, Some(T) }
```

It is how rv6 says "there might not be one". There is no null return value to
forget to check, because you cannot use the `T` without unwrapping:

| rv6 function | Signature | `None` means |
|---|---|---|
| `RoundRobin::pick_next` | `fn(&mut self, &[ProcState]) -> Option<usize>` | nothing is runnable (sched.rs:20) |
| `uart::getc` | `fn() -> Option<u8>` | no byte in the receive register (uart.rs:53) |
| `console::try_getc` | `fn() -> Option<u8>` | the input ring buffer is empty (console.rs:31) |
| `exec::lookup` | `fn(&str) -> Option<Program>` | no program by that name (exec.rs:594) |
| `syscall::getfile` | `unsafe fn(*mut Proc, usize) -> Option<File>` | fd out of range or not open (syscall.rs:312) |
| `SpinLock::try_lock` | `fn(&self) -> Option<SpinLockGuard<'_, T>>` | somebody else holds the lock (spinlock.rs:33) |

Compare `kalloc`, which returns a raw `*mut u8` and uses null as its "nothing"
value (kalloc.rs:40). Every caller has to remember `if page.is_null()`. That is
the C convention, kept deliberately because the allocator lives below the safe
layer — and the contrast is the argument for `Option` everywhere above it.

### `match` is exhaustive

A `match` must cover every variant. Add a variant to `ProcState` and the
compiler lists every `match` that no longer covers everything. This is the
feature that makes a kernel refactor survivable.

```rust
match self.inodes[inum].kind {              // fs.rs:232
    InodeKind::Free => return Err(FsError::NotFound),
    InodeKind::Dir  => return Err(FsError::IsADirectory),
    InodeKind::File => {}                   // the case we actually want
}
```

Note the empty arm: "this case is fine, fall through". That is idiomatic and it
is not the same as omitting the arm.

Forms you will use:

```rust
// a catch-all arm
match cmd {                                 // shell.rs:47
    "pwd" => self.cmd_pwd(out),
    "ls"  => self.cmd_ls(out),
    _ => { out.puts(cmd); out.puts(": command not found\n"); }
}

// a match guard: an extra condition on an arm
match getfile(p, fd) {                      // syscall.rs:471-472
    Some(f) if f.readable => f,
    _ => return -1,
}

// `if let` — one arm you care about
if let Some(b) = try_getc() { return b; }   // console.rs:49

// `while let` — loop until it stops matching
while let Some(b) = uart::getc() { push(b); }   // console.rs:73

// match as an expression producing a value
let inum = match fsg.dirlookup(dir, name.as_bytes()) {   // shell.rs:144
    Ok(i) => i,
    Err(_) => { out.puts("cat: no such file\n"); return; }
};
```

The system call dispatcher is one big `match` on a number (syscall.rs:34), which
is the one place the enum-less form is right: the numbers come from user mode
and must match xv6's.

> **Where you need this:** `34k` — `ProcState` and the process table
> (`proc.rs`); `40k` — `InodeKind` and `FsError` in the filesystem (`fs.rs`).

---

## 5. Arrays, slices, `Vec`, iteration

### Three ways to hold a run of values

| Type | Where the data lives | Size known at | Grows? |
|---|---|---|---|
| `[T; N]` | inline, in the struct or static | compile time | no |
| `&[T]` / `&mut [T]` | somewhere else — this is a borrow | run time (`.len()`) | no |
| `Vec<T>` | the heap | run time | yes |

Kernels prefer the first. A fixed array cannot fail to allocate, cannot
fragment, and its size is a number you can reason about at 3 a.m.:

```rust
static mut PROCS: [Proc; NPROC] = [const { Proc::new() }; NPROC];   // proc.rs:65, NPROC = 64
pub ofile: [File; NOFILE],                                          // proc.rs:39, NOFILE = 16
inodes: [Inode; NINODE],                                            // fs.rs:69,   NINODE = 64
```

"Out of processes" is `allocproc` scanning 64 slots and finding none free
(proc.rs:108) — an ordinary `null` return, not an allocation failure deep inside
a heap. The cost is a hard limit, and rv6 accepts it, as every real kernel does
for its core tables.

`Vec` is available only after `38k` installs the kernel heap
(`kheap.rs` registers a `#[global_allocator]`, which is what turns on
`Box`/`Vec`/`String`). The kernel shell uses it because a command line is
genuinely unbounded:

```rust
pub struct Shell { stack: Vec<(String, usize)> }   // shell.rs:23 — the cwd path
let args: Vec<&str> = words.collect();             // shell.rs:267
```

### Slices

A slice is the shape everything else passes around. `&arr` where `arr: [T; N]`
coerces to `&[T]` automatically; `&arr[a..b]` is a window. Indexing a slice
out of range **panics**, and in rv6 a panic prints `OSLINGS:FAIL (panic)` and
halts the machine (main.rs:281) — so range arithmetic is checked, not
undefined, but it is still fatal. Prefer the slice operations that carry their
own lengths:

```rust
buf[..n].copy_from_slice(&node.data[..n]);              // fs.rs:105
self.inodes[inum].data[off..off + data.len()].copy_from_slice(data);   // fs.rs:258
&e.name[..e.len] == name                                 // fs.rs:114 — compare two &[u8]
```

`copy_from_slice` panics if the two slices differ in length, which is why the
`n` above is computed with `core::cmp::min` first (fs.rs:104).

Two conversions you will use constantly at the syscall boundary:

```rust
core::str::from_utf8(&buf[..n])         // &[u8] -> Result<&str, Utf8Error>  (shell.rs:154)
name.as_bytes()                         // &str -> &[u8]                     (fs.rs:114 callers)
usize::from_le_bytes(ptrbuf)            // [u8; 8] -> usize                  (syscall.rs:216)
```

And the one place a slice is conjured from raw parts, because the program images
are linker symbols rather than Rust values:

```rust
unsafe fn image(start: *const u8, end: *const u8) -> &'static [u8] {   // exec.rs:570
    core::slice::from_raw_parts(start, end as usize - start as usize)
}
```

### Iteration

An iterator is anything with a `next()` method; the adapters are lazy and
compile down to the loop you would have written. `RoundRobin::pick_next` is the
densest example in the kernel and repays reading slowly:

```rust
impl Scheduler for RoundRobin {           // sched.rs:19
    fn pick_next(&mut self, states: &[ProcState]) -> Option<usize> {
        let n = states.len();
        (0..n)
            .map(|off| (self.next + off) % n)         // slot numbers, starting after the last
            .find(|&i| states[i] == ProcState::Runnable)  // the first runnable one
            .map(|i| {                                 // remember where to resume, return i
                self.next = (i + 1) % n;
                i
            })
    }
}
```

`find` returns `Option<usize>`, and the second `map` transforms the `Some` case
while leaving `None` alone — so "nothing runnable" flows straight out as `None`
without a branch. The result is a round-robin scan with no index bookkeeping.

The adapters rv6 actually uses:

| Form | Yields | Example |
|---|---|---|
| `for i in 0..NPROC` | each index | proc.rs:75, the table scans |
| `for e in &self.inodes[dir].entries` | `&DirEnt`, borrowed | fs.rs:113 `dirlookup` |
| `.iter().any(\|e\| e.used)` | `bool` | fs.rs:211 `dir_is_empty` |
| `.into_iter().find(...)` | `Option<Program>`, by value | exec.rs:595 `lookup` |
| `.iter().enumerate()` | `(index, &item)` | shell.rs:68 `pwd` |
| `.map(...)` / `.find(...)` | adapted iterator / `Option` | sched.rs:22 |
| `line.split_whitespace()` | `&str` words | shell.rs:40 command parsing |
| `.collect()` | a `Vec` (or any collection) | shell.rs:267 |
| `for b in s.bytes()` | `u8` | uart.rs:64 `puts` |

`iter()` borrows, `into_iter()` consumes, `iter_mut()` borrows exclusively.
Choosing `into_iter()` in `lookup` is what lets it return an owned `Program`
rather than a borrow of a temporary table.

> **Where you need this:** the fixed `PROCS` table in `34k` (`proc.rs`), the
> `states` array the scheduler builds each pass in `36k` (`usermode.rs:285`),
> and the per-process `ofile` fd table in `50k` (`file.rs`, `syscall.rs`).

---

## 6. Traits, generics, `impl Trait`, monomorphization

### Traits

A trait is a named set of methods a type promises to provide. It has no data
and you never build one. rv6's two teaching traits are deliberately tiny:

```rust
pub trait Scheduler {                                              // sched.rs:5
    fn pick_next(&mut self, states: &[ProcState]) -> Option<usize>;
}
```

```rust
pub trait Out {                          // shell.rs:17
    fn puts(&mut self, s: &str);
}
```

Both exist for the same reason: **one implementation for the machine, one for
the test**. The interactive shell writes through `ConsoleOut`, which forwards to
the UART; the automated harness supplies its own `Out` that appends to a buffer
it can then assert on. The shell commands do not know which they have.

```rust
struct ConsoleOut;
impl Out for ConsoleOut {                // shell.rs:335
    fn puts(&mut self, s: &str) { uart::puts(s); }
}
```

A trait may supply **default methods** (a body in the trait definition), which
implementers get for free and may override. `07r` uses this; the kernel's traits
are small enough not to need it.

### Generics and monomorphization

A generic type or function is written once against a type parameter:

```rust
pub struct SpinLock<T> {          // spinlock.rs:7
    locked: AtomicBool,
    data: UnsafeCell<T>,
}
```

At compile time the compiler **monomorphizes**: for every concrete `T` you
actually use, it stamps out a separate copy with `T` substituted. rv6 uses two:

- `SpinLock<i64>` — inside `Semaphore` (semaphore.rs:6)
- `SpinLock<FileSystem>` — the global `FS` (fs.rs:277)

so the compiled kernel contains two complete, separately optimized spinlocks.
Nothing is looked up at run time; `*count -= 1` through a
`SpinLockGuard<'_, i64>` compiles to exactly the instruction it would if you had
written the lock by hand for `i64`. That is the trade: generics cost code size,
not speed.

**Trait bounds** constrain a type parameter. rv6 has one, and it is load-bearing:

```rust
unsafe impl<T: Send> Sync for SpinLock<T> {}   // spinlock.rs:12
```

Read: a `SpinLock<T>` may be shared between threads (`Sync`), provided `T`
itself may be *sent* between them (`Send`). Without this line the compiler
refuses to let `static FS: SpinLock<FileSystem>` exist at all, because statics
must be `Sync`. It is `unsafe impl` because *you* are asserting the mutual
exclusion is real; the compiler cannot check that.

### Static dispatch vs `dyn`

Two ways to use a trait, and rv6 has one of each:

```rust
// static: the concrete type is known, the call is direct, it can inline.
let mut policy = RoundRobin::new();        // usermode.rs:279
match policy.pick_next(&states) { ... }    // usermode.rs:290
```

```rust
// dynamic: `out` is a fat pointer (data pointer + vtable pointer);
// the call goes through the vtable.
pub fn exec(&mut self, line: &str, out: &mut dyn Out) { ... }   // shell.rs:39
```

`&mut dyn Out` is a **trait object**. The shell uses it because `Shell::exec`
and its eleven `cmd_*` methods would otherwise each be monomorphized for every
output sink — a lot of duplicated code in a kernel image, to save one indirect
call per `puts`. The scheduler uses static dispatch because `pick_next` runs on
every context switch and there is exactly one policy.

| | static (`impl Trait` / `<T: Trait>`) | dynamic (`dyn Trait`) |
|---|---|---|
| Type known at | compile time | run time |
| Call | direct, inlinable | through a vtable |
| Code size | one copy per concrete type | one copy total |
| Can store mixed types in one collection | no | yes |
| rv6 | `Scheduler` (sched.rs) | `Out` (shell.rs) |

### `impl Trait` in argument position

`impl Trait` as a parameter type is shorthand for an anonymous generic
parameter — static dispatch, no `dyn`, no name for the type. rv6 uses it to take
a closure:

```rust
pub fn for_each_entry(&self, dir: usize, mut f: impl FnMut(&[u8], InodeKind)) {   // fs.rs:175
    for e in &self.inodes[dir].entries {
        if e.used {
            let kind = self.inodes[e.inum].kind;
            f(&e.name[..e.len], kind);
        }
    }
}
```

`FnMut` is the trait for closures that may mutate what they capture. The shell's
`ls` passes a closure that writes through `out` (shell.rs:80), which is why it
must be `FnMut` and not `Fn`.

### Standard traits rv6 implements

| Trait | Implemented on | Effect |
|---|---|---|
| `Deref` / `DerefMut` | `SpinLockGuard` (spinlock.rs:58, 65) | `*guard` reaches the protected data |
| `Drop` | `SpinLockGuard` (spinlock.rs:71) | unlock on scope exit |
| `Sync` | `SpinLock<T>` (spinlock.rs:12) | may be a `static` |
| `GlobalAlloc` | `KernelHeap` (kheap.rs:22) | turns on `Box`, `Vec`, `String` |
| `Clone`, `Copy`, `PartialEq`, `Eq` | derived on `Pte`, `File`, `ProcState`, `InodeKind`, ... | duplication and `==` |

> **Where you need this:** `36k` — the `Scheduler` trait and `RoundRobin`
> (`sched.rs`); `46k` — the `Out` trait and the shell's `&mut dyn Out`
> (`shell.rs`).

---

## 7. `Result`, `?`, error enums

### `Result<T, E>`

```rust
enum Result<T, E> { Ok(T), Err(E) }
```

A fallible operation returns one. You cannot reach the `T` without handling the
`E` — which is the whole difference from a C function that returns `-1` and
hopes.

rv6 uses two grades of error type, and the choice is deliberate:

```rust
// vm.rs — the caller can do nothing but give up, so the error carries nothing.
pub unsafe fn mappages(...) -> Result<(), ()>            // vm.rs:75
pub unsafe fn load_segment(table: *mut Pte, image: &[u8]) -> Result<(), ()>   // vm.rs:196
pub unsafe fn copyin(table: *mut Pte, dst: &mut [u8], mut srcva: usize) -> Result<(), ()>  // vm.rs:291
```

```rust
// fs.rs — the caller (and the user) wants to know which thing went wrong.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum FsError {          // fs.rs:18
    NotFound, AlreadyExists, NotADirectory, IsADirectory,
    NoFreeInode, DirFull, NameTooLong, FileTooBig,
}
```

```rust
// exec.rs — three genuinely different failures, three different shell messages.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum ExecError { NotFound, NoMem, BadArgs }   // exec.rs:602
```

An error enum is just an enum, so all of section 4 applies: the compiler will
tell you where you stopped handling every case when you add a variant.

### The `?` operator

`expr?` means: if `Ok(v)`, evaluate to `v`; if `Err(e)`, return `Err(e)` from
the enclosing function immediately. It replaces the `if (ret < 0) goto fail;`
ladder that runs through every C kernel.

```rust
pub unsafe fn proc_pagetable(p: *mut Proc) -> Result<(), ()> {   // proc.rs:162
    let pt = (*p).pagetable;
    vm::mappages(pt, TRAMPOLINE, PGSIZE, vm::trampoline_page(), PTE_R | PTE_X)?;
    vm::mappages(pt, TRAPFRAME, PGSIZE, (*p).trapframe as usize, PTE_R | PTE_W)?;
    Ok(())
}
```

Two rules to remember: `?` only works in a function that itself returns `Result`
(or `Option`), and the error types must match — or be convertible. When they do
not match, `map_err` converts:

```rust
vm::mappages(pt, TRAMPOLINE, PGSIZE, vm::trampoline_page(), PTE_R | PTE_X)
    .map_err(|_| ExecError::NoMem)?;                     // exec.rs:680
vm::load_segment(pt, image).map_err(|_| ExecError::NoMem)?;     // exec.rs:684
vm::map_user_stack(pt).map_err(|_| ExecError::NoMem)?;          // exec.rs:685
```

`Result<(), ()>` in, `Result<_, ExecError>` out, one closure per line.

`ok_or` does the same job for an `Option`, turning "there wasn't one" into a
named error:

```rust
let prog = lookup(name).ok_or(ExecError::NotFound)?;   // exec.rs:649
let slot = slot.ok_or(FsError::DirFull)?;              // fs.rs:139
```

### The full combinator set rv6 uses

| Form | On | Does |
|---|---|---|
| `?` | `Result` / `Option` | unwrap or return early |
| `.ok_or(e)?` | `Option` | `None` becomes `Err(e)` (exec.rs:649) |
| `.map_err(\|_\| e)?` | `Result` | replace the error type (exec.rs:680) |
| `.is_err()` / `.is_ok()` | `Result` | test without unwrapping (vm.rs:132) |
| `.unwrap_or(d)` | `Option` | a default instead of `None` (shell.rs:45) |
| `let _ = expr;` | `Result` | deliberately ignore (shell.rs:181) |
| `match` | either | handle each case differently |

`let _ = fsg.unlink(dir, name.as_bytes());` (shell.rs:181) is worth calling out:
it says *I have already checked this cannot fail* and silences the unused-result
warning. It is not the same as ignoring an error by accident, and reviewers read
it that way.

### Errors that must not propagate: the syscall boundary

`?` stops at the edge of the kernel. A system call returns an `isize` to a user
program, so somewhere the `Result` has to become a number:

```rust
match crate::exec::exec_into(p, name, rest) {    // syscall.rs:267
    Ok(argc) => argc as isize,
    Err(_) => -1,
}
```

That is the Unix convention and rv6 keeps it. Above that line, errors are typed;
below it, they are `-1` and `errno`-free.

Two more shapes worth recognizing. `dircreate` uses a `match` on a `Result`
purely to *distinguish* one error from the rest:

```rust
match self.dirlookup(dir, name) {          // fs.rs:126
    Ok(_) => return Err(FsError::AlreadyExists),  // it already exists
    Err(FsError::NotFound) => {}                  // good — that is what we wanted
    Err(e) => return Err(e),                      // anything else propagates
}
```

And `touch` in the shell treats one error as success, because that is what real
`touch` does:

```rust
match fsg.dircreate(dir, name.as_bytes(), InodeKind::File) {   // shell.rs:133
    Ok(_) => {}
    Err(FsError::AlreadyExists) => {}      // already there: fine
    Err(_) => out.puts("touch: cannot create file\n"),
}
```

Neither is possible if the error is an `int`.

> **Where you need this:** `40k` — `dirlookup`, `dircreate` and `FsError`
> (`fs.rs`); `49k` — `exec`, `ExecError`, and the `map_err` chain in
> `fill_addrspace` (`exec.rs`).

---

## Common compiler errors and what they actually mean

Four error codes account for most of the pain in this course. Learn to read
them and the borrow checker stops feeling arbitrary.

| Code | rustc says | It actually means | Usual fix in rv6 |
|---|---|---|---|
| `E0382` | borrow of moved value / use of moved value | you gave the value away and then used it | make the type `Copy`, borrow with `&` instead of passing by value, or return it back |
| `E0499` | cannot borrow `x` as mutable more than once at a time | you asked for two exclusive borrows of the same thing | store an **index**, not a `&mut`; finish one borrow before starting the next |
| `E0502` | cannot borrow `x` as mutable because it is also borrowed as immutable | a read borrow is still alive at a point where you write | copy the small value out (it is `Copy`), or end the read borrow first |
| `E0106` | missing lifetime specifier | a struct or return type holds a reference and you did not say how long | add `<'a>` to the struct and `&'a` to the field, or `'_` in a return type |

### `E0382` — use after move

```rust
let free = vec![1usize, 2, 3];
let (_free2, _p) = take_page(free);
println!("{}", free.len());
```

```text
error[E0382]: borrow of moved value: `free`
   |
 8 |     let free = vec![1usize, 2, 3];
   |         ---- move occurs because `free` has type `Vec<usize>`, which does not implement the `Copy` trait
 9 |     let (_free2, _p) = take_page(free);
   |                                  ---- value moved here
10 |     println!("{}", free.len());
   |                    ^^^^ value borrowed here after move
```

Read the three underlines in order: where it was created, where it was moved,
where you touched it afterwards. The fix depends on what you meant:

- you wanted to keep it → change `take_page(free: Vec<usize>)` to
  `take_page(free: &mut Vec<usize>)`;
- you wanted the callee to hand it back → return it, as `02r`'s
  `take_page` does with a tuple;
- the value is small and plain → `#[derive(Clone, Copy)]`, which is exactly why
  `File` and `Pte` are `Copy`.

Ignore the "consider cloning" suggestion. In a kernel it is usually the wrong
answer, and for the types in rv6 there is nothing to clone.

### `E0499` — two mutable borrows

```rust
let a = fs.get(0);     // fn get(&mut self, i: usize) -> &mut u32
let b = fs.get(1);
*a += 1;
```

```text
error[E0499]: cannot borrow `fs` as mutable more than once at a time
  |
7 |     let a = fs.get(0);
  |             -- first mutable borrow occurs here
8 |     let b = fs.get(1);
  |             ^^ second mutable borrow occurs here
9 |     *a += 1;
  |     ------- first borrow later used here
```

The compiler cannot know that slots 0 and 1 are different, so it refuses. Note
the third underline: the error exists *because* `a` is used on line 9. Delete
that line and the code compiles, which is non-lexical lifetimes in action.

In kernel code the fix is nearly always to stop holding references into a table.
`fs.rs` is written this way throughout: `dircreate` records `slot: usize` rather
than `&mut DirEnt` (fs.rs:132–139), and `unlink` copies the entry out —

```rust
let e = self.inodes[dir].entries[i];        // fs.rs:195 — a copy; DirEnt is Copy
if e.used && e.len == name.len() && &e.name[..e.len] == name {
    self.inodes[e.inum] = Inode::new();     // fs.rs:197 — now free to write elsewhere
    self.inodes[dir].entries[i].used = false;
```

If you genuinely need two exclusive borrows into one array, `split_at_mut` is
the standard-library answer — but in this course, reach for the index first.

### `E0502` — mixing a read borrow with a write

```rust
let mut states = vec![1u8, 2, 3];
let first = &states[0];
states.push(4);
println!("{}", first);
```

```text
error[E0502]: cannot borrow `states` as mutable because it is also borrowed as immutable
  |
3 |     let first = &states[0];
  |                  ------ immutable borrow occurs here
4 |     states.push(4);
  |     ^^^^^^^^^^^^^^ mutable borrow occurs here
5 |     println!("{}", first);
  |                    ----- immutable borrow later used here
```

This is not pedantry: `push` may reallocate, and `first` would dangle. The
standard fixes are to copy the value out (`let first = states[0];` — it is a
`u8`) or to move the write after the last read. In rv6 you meet this most often
inside `FileSystem` methods, where a loop reads `self.inodes[...]` and the body
wants to write `self.inodes[...]`; the answer is the same as for `E0499`.

You will also meet it with a lock guard: `FS.lock()` borrows nothing of yours,
but a value you pulled out of the guard borrows the guard. `drop(fsg)`
(shell.rs:102) ends that borrow explicitly.

### `E0106` — missing lifetime specifier

```rust
struct Guard<T> { lock: &SpinLock<T> }
```

```text
error[E0106]: missing lifetime specifier
  |
2 | struct Guard<T> { lock: &SpinLock<T> }
  |                         ^ expected named lifetime parameter
  |
help: consider introducing a named lifetime parameter
  |
2 | struct Guard<'a, T> { lock: &'a SpinLock<T> }
  |              +++             ++
```

Take the suggestion — it is right, and it is precisely `spinlock.rs:54`. The
error appears whenever a struct field, or a returned reference with no
unambiguous input to borrow from, holds a `&`. Elision has no rule to apply, so
you must supply the name. In a return type where the source is obvious, `'_` is
enough: `fn lock(&self) -> SpinLockGuard<'_, T>` (spinlock.rs:22).

### A few more you will meet

| Code | Means | Fix |
|---|---|---|
| `E0507` | cannot move out of borrowed content | the type is not `Copy`; borrow it, clone it, or `derive(Copy)` |
| `E0596` | cannot borrow as mutable — the binding is not `mut` | `let mut x = ...` |
| `E0597` | value does not live long enough | the borrow outlives the owner; restructure so the owner outlives it |
| `E0133` | this operation is unsafe | wrap in `unsafe { }` and justify it — see [Unsafe Rust and no_std](rust-unsafe-nostd.md) |
| `E0308` | mismatched types | usually `usize` vs `u64` at the trapframe boundary; add an explicit `as` |

### Reading rustc at all

Three habits that save the most time:

1. **Fix the first error only, then rebuild.** Later errors are often the first
   one echoing.
2. **Read the underlines, not just the message.** The three-line form
   (created / moved / used) tells you which line to change; the message alone
   does not.
3. **`rustc --explain E0499`** prints a page of prose with a worked example.
   `cargo test` and `oslings` pass the code through in their output for exactly
   this reason.

---

## Habits that carry you through Module 2

- **Store an index, not a reference,** into any kernel table. `usize` sidesteps
  `E0499` and `E0502` and matches how the hardware thinks anyway.
- **Make small plain structs `Copy`.** `Pte`, `File`, `Context`, `DirEnt`,
  `ProcState` all are, and each one buys you a class of borrow errors you never
  see.
- **Let the guard do the unlocking.** If you find yourself wanting an
  `unlock()` call, you want a smaller scope or a `drop()`.
- **Name your errors.** `Result<(), ()>` is fine when the caller can only give
  up; the moment there are two distinct recoveries, write the enum.
- **`const fn` anything a `static` needs,** or the kernel will not link.
- **Reach for `unsafe` last, and confine it.** `kalloc.rs` and the MMIO drivers
  are unsafe so that `fs.rs` and `sched.rs` do not have to be.

## Practice beyond the exercises

The in-class exercises are deliberately short. If you finish early, or want more
reps on an idea before it shows up in the kernel, two free collections cover the
same ground and are recommended, not required:

- [Rustlings](https://github.com/rust-lang/rustlings) — small compiler-driven
  exercises, one file each, run with `rustlings run`. Many of you met it in
  CS 272.
- [100 Exercises to Learn Rust](https://rust-exercises.com/100-exercises/) —
  a longer sequence with a test per exercise, closer in shape to OSlings.

The mapping to Module 1:

| Rustlings sections | OSlings exercises |
|---|---|
| `variables`, `functions`, `if`, `primitive_types` | `00r_hello_rust`, `01r_control_flow` |
| `move_semantics` | `02r_ownership`, `03r_borrowing` |
| `structs`, `enums`, `options` | `04r_structs_impl`, `05r_enums_match` |
| `vecs`, `traits`, `generics`, `error_handling` | `06r_collections`, `07r_traits`, `08r_errors` |

Rustlings has no `unsafe` or `no_std` track; for `21r_unsafe_bridge` and the
kernel, the reference is [Unsafe Rust and no_std](rust-unsafe-nostd.md).

## See also

- [Unsafe Rust and no_std](rust-unsafe-nostd.md) — raw pointers, `static mut`,
  `volatile`, `#[repr]` in anger, and what `#![no_std]` removes.
- [rv6 Architecture](rv6-architecture.md) — how the modules cited here fit
  together.
- [Sv39 Paging](sv39-paging.md) — what the bits inside `Pte` mean.
- [Cheatsheet](cheatsheet.md) — the one-page version of this page.
- [Exam Prep](exam-prep.md) — what the midterm asks about this material.
- [Using OSlings](oslings-usage.md) — running the Module 1 exercises with
  `cargo test`.
