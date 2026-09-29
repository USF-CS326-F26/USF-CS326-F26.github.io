# Week 6 · Below Rust: Assembly, `unsafe`, and `no_std`

> **Thu Oct 1** `20a_asm_bridge` · **Fri Oct 2** `21r_unsafe_bridge`, `30k_kernel_basics`
>
> Read **Essentials** before Thursday: it is what Thursday and Friday assume.
> **Going deeper** is optional and is not on the exam.

[Slides](06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std-slides.html){ .md-button }
[Thursday prep](../prep/06-cs326-2026-10-01-prep-asm-bridge.md){ .md-button }
[Friday prep](../prep/06-cs326-2026-10-02-prep-unsafe-and-kernel-basics.md){ .md-button }

## This week { #this-week }

In exercise `35k` your kernel stops one process and resumes another, and in
`31k` it boots on a machine with nothing else on it. Neither can be written in
ordinary Rust. The first needs instructions Rust has no words for; the second
needs a program that assumes no operating system at all.

This week you build the floor under both. On Thursday you call your own RISC-V
assembly from Rust and run it under QEMU. Thursday is the QEMU deadline, so run
`oslings doctor` now, not Thursday morning. On Friday you reach a device through
a raw pointer, with `cargo test` still watching, and then take the standard
library away. By Friday night you have assembly running on the bare machine and
a kernel crate that compiles with no OS beneath it.

---

## Essentials { #essentials }

### Thursday · `20a` The assembly bridge { #thu-20a }

In `35k` one function call returns into a different process, on a different
stack. No Rust statement names `ra` or `sp`, so in `20a_asm_bridge` you write
that part in assembly and call it from Rust.

#### Registers have jobs { #20a-registers }

RV64 has 32 registers, `x0` to `x31`, but everyone uses their **ABI names**,
which carry each register's job:

| Name | Job |
|---|---|
| `zero` | Always 0; writes vanish |
| `ra` | Return address |
| `sp` | Stack pointer |
| `a0`–`a7` | Arguments; `a0` is also the result |
| `t0`–`t6` | Temporaries |
| `s0`–`s11` | Saved registers |

`ra` is an ordinary register. `call f` puts the return address in `ra` and
jumps; `ret`, shorthand for `jalr zero, 0(ra)`, jumps to whatever `ra` holds.

The stack grows down, and `sp` must be a multiple of 16 at every call.

#### Caller-saved and callee-saved { #20a-saved }

Registers sit on two sides of a bargain. **Caller-saved** ones (`t0`–`t6`,
`a0`–`a7`, `ra`) are fair game for any function you call: after a `call`, treat
them as garbage unless you stashed them. **Callee-saved** ones (`s0`–`s11`,
`sp`) belong to your caller: borrow `s2` and you owe it back before `ret`.

That bargain makes a context switch cheap. A switch is entered by an ordinary
`call`, so the compiler already saved the `t` and `a` values it needs. That
leaves `s0`–`s11`, `sp` and `ra`: 14 registers in `35k`, not 31. `ra` is there
because the switch is about to replace it.

#### The calling convention { #20a-convention }

`extern "C"` selects the **calling convention**: `a0` through `a7` carry the
arguments in order, and `a0` carries the result. A pointer or `u64` fills
one register.

A **leaf function** calls nothing, so its `ra` survives. If it also sticks to
`a` and `t` registers, it needs no stack [frame](#exam-prologue).

#### Loads, stores, and local labels { #20a-memory }

Only loads and stores touch memory. `ld` and `sd` move 8 bytes; `lb`, `lbu` and
`sb` move one ([`lb` versus `lbu`](#exam-lb-lbu)). In `off(rs)` the address is
`rs + off`, and `off` is a signed 12-bit constant (−2048 to 2047) welded into
the instruction, never a register.

Labels share one namespace, so assembly has **local labels**: `1:` may
repeat, `1b` means the nearest `1:` behind, and `2f` the nearest `2:` ahead.
This leaf stops at a sentinel byte:

```asm
find_byte:               # a0 = string, a1 = byte wanted
1:  lbu  t0, 0(a0)       # load a byte
    beq  t0, a1, 2f      # found: exit
    beqz t0, 2f          # the NUL: exit too
    addi a0, a0, 1       # next byte
    j    1b              # back to the top
2:  ret                  # a0 = match or NUL
```

Read `beq t0, a1, 2f` as "if equal, jump ahead to 2". The loop keeps no count:
hand it bytes with no 0 and no match, and it reads on through memory.

#### The bridge: `global_asm!`, `extern "C"`, `#[repr(C)]` { #20a-bridge }

`core::arch::global_asm!` passes a raw string, `r#"…"#`, straight to the
assembler; `.globl` exports a name the linker can resolve from Rust:

```rust
core::arch::global_asm!(r#"
.globl span_end
span_end:                # a0 = *const Span
    ld   t0, 0(a0)       # t0 = start
    ld   t1, 8(a0)       # t1 = len
    add  a0, t0, t1      # a0 = start + len
    ret
"#);
```

The Rust side declares the symbol and pins the struct:

```rust
#[repr(C)]
pub struct Span { pub start: u64, pub len: u64 }   // start at 0, len at 8
extern "C" { fn span_end(s: *const Span) -> u64; }
```

Read the `extern` line as a claim Rust cannot check: "`span_end` exists and
follows the C rules". Declare the parameter as `u64` instead, and
`unsafe { span_end(7) }` compiles; the assembly then loads from address 7. So
every call is `unsafe`, and the signature is your promise.

Rust's default layout may reorder fields; `repr(C)` keeps declaration order, so
the `0` and `8` in `span_end` stay true. Insert a field ahead of `len` and it
still compiles, but adds the wrong number.

#### A `ret` that lands somewhere else { #20a-resume }

`ret` jumps to whatever `ra` holds *now*. Load a new `ra` first and the function
returns elsewhere; load a new `sp` too, and you have resumed a different
computation on its own stack:

```asm
resume:                  # a0 = *const Resume: sp at 0, ra at 8
    ld   sp, 0(a0)       # the saved stack
    ld   ra, 8(a0)       # the saved return address
    ret                  # "return" into it
```

Read `resume` as a one-way door: nothing recorded where its caller was. It is
C's `longjmp`; `setjmp` is the half that records "where I am".

> **The one thing to get right:** ten seconds of nothing, then "QEMU timed
> out", and the output stops after the last `[ok]`, with no `[fail]`: a `ret`
> went somewhere wrong. `ret` keeps no memory of its own; it trusts `ra` at the
> instant it runs. Before any `ret`, know which instruction last wrote `ra`.

#### Running under QEMU { #20a-qemu }

`oslings run 20a_asm_bridge` builds for `riscv64gc-unknown-none-elf`, boots it
in `qemu-system-riscv64` with no firmware and no OS, and reads the serial
output. `OSLINGS:PASS` is a pass; a `[fail]` line names the check that said no.

Silence, then "QEMU timed out", means control never came back, whatever the
message says about "the stack setup". To quit a QEMU you started, press
`Ctrl-A`, then `x`; `Ctrl-C` does nothing.

### Friday · `21r` Raw pointers, `unsafe`, and volatile { #fri-21r }

From `31k` on, every character your kernel prints is one byte stored at a
device address. `21r_unsafe_bridge` practices that pointer work under
`cargo test`, where each mistake names itself in a failing assertion.

#### Memory you cannot borrow: MMIO and raw pointers { #21r-pointers }

On QEMU's `virt` board the CLINT timer answers at `0x0200_0000`. A store to a
device address reaches a chip: **memory-mapped I/O** (MMIO). No reference fits:
the borrow checker vouches for a `&u64` only because it watched the value being
created, and no code of yours created the timer.

A **raw pointer**, `*const T` or `*mut T`, is an address with a type and no
guarantees. Creating one from an integer is safe: the cast reads and writes
nothing, and the claim about what lives there comes when you use it:

```rust
const MTIMECMP: *mut u64 = 0x0200_4000 as *mut u64;  // one alarm per hart
let hart3 = unsafe { MTIMECMP.add(3) };               // 0x0200_4018
```

Read `.add(3)` as "three `u64`s along": 24 bytes, not 3. `.add` is an
`unsafe fn`, because leaving the pointer's object is already undefined
behavior.

#### What `unsafe` unlocks, and what it does not { #21r-unsafe }

`unsafe` permits operations the compiler cannot check: (1) dereference a raw
pointer, (2) call an `unsafe fn`, including `extern` functions, and (3) touch a
`static mut`. Two rarer ones make five.

It turns nothing off: borrow, type and bounds checks all still run, so two
`&mut` borrows of one element fail with `E0499` even inside `unsafe { }`. It is
a signed claim: an **`unsafe fn`** hands it to the caller, and an `unsafe` block
says "checked here".

Wrap a small unsafe core in a **safe wrapper**:

```rust
pub fn end_of(s: &Span) -> u64 {
    // promise: s is live, aligned, and 16 bytes long
    unsafe { span_end(s) }
}
```

The `&Span` is the proof: a reference is always non-null, aligned and alive. No
safe call can break `end_of`, which makes it **sound**. When no type can carry
the proof, the wrapper checks at run time and refuses what fails.

#### Volatile: the load that never repeats { #21r-volatile }

The optimizer assumes only your program changes memory; devices break that
assumption. `mtime`, the CLINT's clock, ticks ten million times a second:

```rust
const MTIME: *const u64 = 0x0200_BFF8 as *const u64;
unsafe fn wait_until(deadline: u64) {
    while *MTIME < deadline {}      // a plain load
}
```

Nothing in the loop writes `*MTIME`, so an optimized build loads it once. If
the deadline has not passed, the loop spins forever. Stores fail the
opposite way: of two plain stores to one register, the first is deleted.

Write `core::ptr::read_volatile(MTIME)` in place of `*MTIME` and the load is
**volatile**: the compiler must perform it as written, on every pass.
`write_volatile(p, v)` is the volatile store. Ask where the address points: a
chip gets volatile; RAM gets a plain `*p`.

> **The one thing to get right:** every test is green and the kernel boots, yet
> an optimized build loses a byte or hangs. The tests' "device" is an array, and
> `oslings` builds without optimization, so plain and volatile pass alike.
> Choose by the rule, not the test.

### Friday · `30k` Leaving `std` { #fri-30k }

From `31k` on, your code starts with no loader, no C runtime and no OS.
`30k_kernel_basics` tells the compiler so, and passes once the kernel compiles.

#### What `std` is, and why a kernel cannot have it { #30k-std }

The standard library is three layers:

```text
std     needs an OS     println!, files, threads, HashMap
alloc   needs a heap    Box, Vec, String
core    needs nothing   Option, Result, slices, iterators, core::ptr, PanicInfo
```

A kernel cannot have `std`, because a kernel is what `std` calls; its target,
`riscv64gc-unknown-none-elf`, even names its OS `none`. `std` re-exports `core`,
so `std::ptr::write_volatile` *is* `core::ptr::write_volatile`, and most of
Module 1 survives.

#### The bare-metal skeleton { #30k-skeleton }

Every bare-metal Rust binary carries these lines, each answering an error:

```rust
#![no_std]      // link core, not std
#![no_main]     // no generated main
#[panic_handler]
fn panic(_: &PanicInfo) -> ! { … }
```

| Leave out | `rustc` says |
|---|---|
| `#![no_std]` | ``error[E0463]: can't find crate for `std` `` |
| the panic handler | `` `#[panic_handler]` function required, but not found `` |
| `#![no_main]` | ``error[E0601]: `main` function not found in crate …`` |

Without `std`, the panic handler is yours. Its return type, the **never type**
`!`, promises it never returns: the panicking code cannot go on, and there is
no caller to unwind to. So its body loops forever or calls another `!` function.

No C runtime calls a `main`, so the **linker script** names the entry symbol;
rv6's is `_entry`. It carries `#[no_mangle]` to keep its name exact for the
linker, and `extern "C"` to fix how it is called.

> **The one thing to get right:** you add `no_std` at the top and still get
> ``can't find crate for `std` ``, beside a warning to "add an exclamation mark".
> Without the `!`, `#[no_std]` decorates only the item below it; the `!` makes an
> attribute speak for the whole crate.

### For the exam { #exam }

*Not needed on Thursday or Friday. On Midterm 1.*

**`lb` versus `lbu`** · *Midterm 1.* `lb` sign-extends, copying the byte's top
bit into all 56 bits above it; `lbu` zero-extends. The byte `0xE9` loads as
`0xFFFF_FFFF_FFFF_FFE9` (−23) under `lb` and as `0xE9` (233) under `lbu`. Below
`0x80` the two agree. Load data bytes, such as characters and sizes, with `lbu`:
under `lb`, each byte of `0x80` or more counts 256 too small.
{ #exam-lb-lbu }

**Stack frames** · *Midterm 1.* A function that calls must save `ra`, because
its own `call` overwrites it. Any function, leaf or not, must save each `s`
register it uses. Its prologue moves `sp` down by a multiple of 16, and its
epilogue undoes exactly that:
{ #exam-prologue }

```asm
    addi sp, sp, -16     # claim 16 bytes; sp stays 16-byte aligned
    sd   ra, 8(sp)       # we call, so save ra
    sd   s0, 0(sp)       # we use s0, so save the caller's s0
    ...                  # the body
    ld   s0, 0(sp)       # the epilogue: the prologue, backwards
    ld   ra, 8(sp)
    addi sp, sp, 16
    ret
```

Skip the `s0` save and a unit test can still pass, because its tiny caller keeps
nothing in `s0`. A real caller does, and it breaks later, somewhere else.

**Trace the registers** · *Midterm 1.* Given a short routine and its inputs,
give each register's value at marked points and say where `ret` goes. Keep one
row per point; update only the register each instruction writes. Know the
pseudo-instructions: `li` loads a constant, `mv` copies a register, and
`beqz`/`bnez` branch when a register is zero/nonzero. Watch sign extension;
`ret` uses `ra` as it is at that moment. [Problems 1 and 4](#problems) have
this shape.
{ #exam-trace }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday or Friday, and nothing here is on
the exam.*

### The same few places, in every kernel { #deeper-places }

A kernel keeps its assembly in the same few places:

| Place | Why it cannot be Rust | Exercise |
|---|---|---|
| Boot trampoline | Rust needs a valid `sp` before its first instruction | `31k` |
| Context switch | It names 14 registers and returns to a different `ra` | `35k` |
| Trap vectors | Entered between any two instructions, with every register live | `43k` |
| Return to user mode | It switches page tables and keeps running | `48k` |

None of it is an optimization: Rust cannot express it at all, and no compiler
will change that.

### What the compiler actually emits { #deeper-emitted }

Four functions, compiled by `rustc -O` for `riscv64gc-unknown-none-elf`, with
`MTIME` and `MTIMECMP` as in Essentials:

```rust
unsafe fn plain_wait(d: u64)     { while *MTIME < d {} }
unsafe fn volatile_wait(d: u64)  { while read_volatile(MTIME) < d {} }
unsafe fn plain_rearm(t: u64)    { *MTIMECMP = u64::MAX; *MTIMECMP = t; }
unsafe fn volatile_rearm(t: u64) { write_volatile(MTIMECMP, u64::MAX);
                                   write_volatile(MTIMECMP, t); }
```

```asm
plain_wait:                     volatile_wait:
    lui  a1, 8204                   lui  a1, 8204
    ld   a1, -8(a1)             .LBB5_1:
    bgeu a1, a0, .LBB3_2            ld   a2, -8(a1)
.LBB3_1:                            bltu a2, a0, .LBB5_1
    j    .LBB3_1                    ret
.LBB3_2:
    ret

plain_rearm:                    volatile_rearm:
    lui  a1, 8196                   lui  a1, 8196
    sd   a0, 0(a1)                  li   a2, -1
    ret                             sd   a2, 0(a1)
                                    sd   a0, 0(a1)
                                    ret
```

`lui a1, 8204` builds `0x0200_C000`, and `-8(a1)` is `0x0200_BFF8`: the 12-bit
offset is signed, so the compiler rounded up and subtracted. `plain_wait` loads
once, above the loop, and if the deadline has not passed it runs `j .LBB3_1`, a
branch to itself. That is loop-invariant code motion, legal because nothing said
this memory could change. `volatile_wait` keeps it inside.

`plain_rearm` stores once: the `u64::MAX` store was dead, so it vanished. On RAM
that is a free win; on a timer it is a skipped step. Elsewhere,
`MTIMECMP.add(hart)` compiles to `slli a0, a0, 3`, the multiply by 8 that `.add`
promised. A debug build does none of this, which is how a missing volatile
survives `cargo test` and every `oslings run`.

### C has all of this, invisibly { #deeper-c }

xv6, the C teaching kernel rv6 descends from, reaches its UART through three
macros:

```c
#define Reg(reg) ((volatile unsigned char *)(UART0 + (reg)))
#define ReadReg(reg) (*(Reg(reg)))
#define WriteReg(reg, v) (*(Reg(reg)) = (v))
```

Every line is as unsafe as the Rust version, and C has no way to say so: the
promise is everywhere and visible nowhere. Rust does not make a kernel safe. It
makes the unsafe parts searchable, so "where could this corrupt memory?" has a
finite answer. Safe Rust's promise always rests on that unsafe core being right.

### `asm!` versus `global_asm!`, and symbol names { #deeper-asm }

`global_asm!` emits whole functions. Its sibling `asm!` places an instruction or
two inside a Rust function and wires them to Rust values:
`asm!("csrr {}, sstatus", out(reg) x)` lets the compiler pick the register. Both
treat braces as operand placeholders, so a literal brace must be doubled.

Rust **mangles** names so two functions called `tick` in different modules can
coexist: `tick` in crate `mg` becomes something like
`_ZN2mg4tick17hc8025ea44c9d2c45E` (nightly, which rv6 uses, now emits the newer
form `_RNvCs…_2mg4tick`). A linker script that says `ENTRY(tick)`
needs the plain name, which `#[no_mangle]` keeps. `#[no_mangle]` fixes the name
and `extern "C"` the convention. Edition 2024 makes the promise visible: it
requires `#[unsafe(no_mangle)]` and `unsafe extern "C" { … }`.

### Reading `riscv64gc-unknown-none-elf` { #deeper-target }

```text
riscv64  gc   -unknown  -none  -elf
   |      |       |       |      +-- object format: plain ELF
   |      |       |       +--------- operating system: none; you are about to be it
   |      |       +----------------- vendor: unspecified
   |      +------------------------- extensions: G and C
   +-------------------------------- base ISA: 64-bit RISC-V
```

`G` bundles multiply, atomics, single and double float, CSR access (Zicsr) and
instruction fences (Zifencei); `C` adds 16-bit compressed encodings. Zicsr is
the quiet giant: without it there is no paging, no trap handling and no change
of privilege.

`rustc --print cfg --target riscv64gc-unknown-none-elf` answers
`target_os="none"` and prints no `target_family` line, and the target's metadata
records `"std": false`. That is also why
`qemu-riscv64` cannot run your kernel: it emulates one Linux process and
translates its system calls, and a `-none-` binary makes none.
`qemu-system-riscv64` emulates a whole machine.

### Getting `alloc` back { #deeper-alloc }

`#![no_std]` does not forbid a heap; it refuses to invent one. In week 10 rv6
builds a kernel heap on the page allocator from `32k`, registers it with
`#[global_allocator]`, and declares `extern crate alloc;`. Then `Box`, `Vec` and
`String` work in the kernel. `HashMap` still does not: its default hasher seeds
itself with randomness from the OS, so it lives only in `std`.

### Practice problems { #problems }

#### Problem 1: Sign extension by hand { #problem-1 }

Memory at `p` holds the bytes `41 E9 7F 80`, and `a0 = p`. Give each destination
register in hex:

```asm
    lb   t0, 1(a0)
    lbu  t1, 1(a0)
    lb   t2, 3(a0)
    lb   t3, 2(a0)
    add  t4, t0, t1
```

Then [`find_byte`](#20a-memory) runs on the bytes `41 E9 7F 00` with
`a1 = 0xE9`. What does it return, and what with `lb` for `lbu`?

<details markdown="1">
<summary>Click to reveal solution</summary>

| Register | Value | Why |
|---|---|---|
| `t0` | `0xFFFF_FFFF_FFFF_FFE9` | the top bit of `0xE9`, copied upward: −23 |
| `t1` | `0x0000_0000_0000_00E9` | `lbu` fills with zeros: 233 |
| `t2` | `0xFFFF_FFFF_FFFF_FF80` | −128 |
| `t3` | `0x0000_0000_0000_007F` | top bit clear, so both loads agree |
| `t4` | `0x0000_0000_0000_00D2` | −23 + 233 = 210; the add wraps past 2^64 |

With `lbu`, `find_byte` returns `p + 1`. With `lb`, `t0` holds
`0xFFFF_FFFF_FFFF_FFE9`, which never equals `a1 = 0xE9` (a Rust `u8` argument
arrives zero-extended). The loop walks on to the NUL and returns `p + 3`, "not
found".

</details>

#### Problem 2: Which lines need `unsafe`? { #problem-2 }

Say whether each numbered line compiles, and name any error.

```rust
static mut HITS: u64 = 0;

pub fn touch(words: &mut [u64; 4]) -> u64 {
    let start = words.as_mut_ptr();         // 1
    let p = start.add(2);                   // 2
    unsafe {
        *p = 7;                             // 3
        let a = &mut words[0];              // 4
        let b = &mut words[0];              // 5
        *a += 1; *b += 1;
        HITS += 1;                          // 6
        core::ptr::read_volatile(start)     // 7
    }
}
```

<details markdown="1">
<summary>Click to reveal solution</summary>

- **1 compiles.** Making a pointer is safe.
- **2 fails:** ``error[E0133]: call to unsafe function `…::add` is unsafe and
  requires unsafe function or block``. Nothing is dereferenced, but `.add` is an
  `unsafe fn`.
- **3 and 4 compile.**
- **5 fails:** ``error[E0499]: cannot borrow `words[_]` as mutable more than
  once at a time``, raised inside the block. No amount of `unsafe` fixes it.
- **6 compiles.** Writing a `static mut` is on the list.
- **7 compiles.** It calls an `unsafe fn` inside the block.

</details>

#### Problem 3: Offsets by hand { #problem-3 }

```rust
#[repr(C)]
pub struct Packet { pub kind: u8, pub len: u32, pub addr: u64, pub flags: u16 }
```

Give each field's offset, the size and alignment, and the instruction that loads
`addr` into `t0` when `a0` points at a `Packet`. Which field order makes the
struct smallest? What changes without `#[repr(C)]`?

<details markdown="1">
<summary>Click to reveal solution</summary>

```text
offset  0   kind    u8     1 byte, then 3 bytes of padding (u32 aligns to 4)
offset  4   len     u32    4 bytes
offset  8   addr    u64    8 bytes
offset 16   flags   u16    2 bytes, then 6 bytes of padding (size rounds to 8)
size = 24, align = 8
```

The load is `ld t0, 8(a0)`. Widest first, `addr, len, flags, kind`, gives
offsets 0, 8, 12 and 14 and a size of 16.

Without `#[repr(C)]` the layout is unspecified, and today's `rustc` picks exactly
that widest-first order. Now `ld t0, 8(a0)` loads `len`, `flags`, `kind` and a
padding byte, glued into one number.

</details>

#### Problem 4: Trace a resume { #problem-4 }

`checkpoint` is `resume`'s partner; `resume_with` also passes a value:

```asm
checkpoint:              # a0 = *mut Resume -> 0
    sd   sp, 0(a0)
    sd   ra, 8(a0)
    li   a0, 0
    ret
resume_with:             # a0 = *const Resume, a1 = value
    ld   sp, 0(a0)
    ld   ra, 8(a0)
    mv   a0, a1
    ret
```

`R` is at `0x8000_9000`. Function `f` calls `checkpoint(&R)` with
`sp = 0x8000_5600` and `ra = 0x8000_1044`, gets 0, and calls `g`. `g`'s prologue
saves `f`'s `s1` and drops `sp` to `0x8000_55E0`, then uses `s1` and calls
`resume_with(&R, 7)`, with `ra = 0x8000_2214`.

**Part 1.** Give `ra`, `sp` and `a0` after each instruction of `resume_with`.
Where does `ret` go, and what does `f` see?

**Part 2.** What does `f` find in `s1` afterwards, and what does that say about
a real switch?

<details markdown="1">
<summary>Click to reveal solution</summary>

**Part 1.**

| After | `ra` | `sp` | `a0` |
|---|---|---|---|
| `ld sp, 0(a0)` | `0x8000_2214` | `0x8000_5600` | `0x8000_9000` |
| `ld ra, 8(a0)` | `0x8000_1044` | `0x8000_5600` | `0x8000_9000` |
| `mv a0, a1` | `0x8000_1044` | `0x8000_5600` | `7` |

`ret` jumps to `0x8000_1044`, right after `f`'s call. `f` sees `checkpoint`
return a second time, now with 7, on its own stack.

**Part 2.** `f` finds `g`'s value. Only `g`'s epilogue would have restored
`f`'s `s1`, and it never ran. `s1` is callee-saved, so `f` was entitled to
trust it. That is why `setjmp` also records `s0`–`s11`, and why a real switch
saves every callee-saved register.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| ABI name | A register's conventional name, like `a0` for `x10` | `20a`, every trace |
| Caller-saved | The callee may destroy it: `t`, `a`, `ra` | `20a`, `35k` |
| Callee-saved | The callee must restore it: `s0`–`s11`, `sp` | `20a`, `35k` |
| Leaf function | Calls nothing, so `ra` survives; with only `a` and `t` registers, it needs no frame | `20a` |
| Local label | Reusable `1:`; `1b` looks back, `2f` ahead | `20a` |
| `#[repr(C)]` | Declaration-order fields at computable offsets | `20a`, `35k`, `48k` |
| `extern "C"` | The C calling convention; the signature is unchecked | `20a`, `30k` |
| MMIO | Device registers reached by loads and stores | `21r`, `31k`, `45k` |
| Raw pointer | An address and a type, no guarantees | `21r`, `32k`, `33k` |
| `unsafe` | Unlocks a few operations; disables no check | `21r` onward |
| Volatile | Performed as written, every time; for devices | `21r`, `31k`, `45k` |
| `core` / `alloc` / `std` | Needs nothing / a heap / an OS | `30k`, `38k` |

## Further reading { #reading }

- [Code and output](../inclass/week06-examples.html): thirteen bare-metal
  programs that run this page's examples under QEMU (`find_byte`, `span_end`,
  `resume`, `wait_until`, and a store the optimizer drops without `volatile`),
  each beside what it printed, and seven files that must not compile.
- [RISC-V guide](../guides/riscv.md#registers): registers,
  [the caller/callee split](../guides/riscv.md#the-callercallee-split), the
  [instruction quick reference](../guides/riscv.md#instruction-quick-reference)
  and [assembly inside Rust](../guides/riscv.md#assembly-inside-rust).
- [Unsafe Rust and no_std](../guides/rust-unsafe-nostd.md#raw-pointers): raw
  pointers, [what `unsafe` does not do](../guides/rust-unsafe-nostd.md#what-unsafe-does-not-do),
  [`static mut` and `addr_of!`](../guides/rust-unsafe-nostd.md#static-mut-and-addr_of)
  (Thursday's harness uses both) and
  [symptoms and their causes](../guides/rust-unsafe-nostd.md#symptoms-and-their-causes).
- [QEMU and GDB](../guides/qemu-gdb.md#first-how-to-get-out-of-qemu): getting out
  of QEMU, and the [diagnostic playbook](../guides/qemu-gdb.md#diagnostic-playbook).
- [Memory Map](../guides/memory-map.md#the-qemu-virt-physical-map): every device
  on the `virt` board.
- [Using OSlings](../guides/oslings-usage.md#the-three-test-modes) and
  [Dev Setup: `oslings doctor`](../guides/dev-setup.md#7-oslings-doctor).
- *RISC-V ELF psABI* (`riscv-non-isa/riscv-elf-psabi-doc` on GitHub): the
  document that makes `a0` the first argument.
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/), chapters 1–3, and
  [Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html).
- [The xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf),
  chapter 2: where the assembly lives in a real kernel.
