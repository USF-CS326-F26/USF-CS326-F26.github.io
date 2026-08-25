# Extra Credit

Up to **+3%** on the final grade. None of this is required, and none of it is
graded on a curve — if you do the work, you get the points. The work usually
outweighs the points; do it because you want the thing to exist.

Extra credit is released on ordinary exercise days, alongside the core
exercise, and is worked the same way as everything else: in class once the
day's core exercise passes, or in office hours with the TA or instructor. It
is never scheduled for a session of its own, and nothing later in the course
depends on it — skipping every item here costs nothing but the points. Submit
it with `oslings submit` like anything else; it is graded from your repo at
the end of the semester.

| Exercise | Released | Points | What you build |
|---|---|---|---|
| [`14c_head`](#14c) | Fri Sep 25, with `12c`/`13c` | +0.5 | `head -n`: stop early on a line-oriented stream |
| [`41k_devices`](#41k) | Thu Nov 5, with `40k` | +0.5 | The polled NS16550A UART driver |
| [`47k_file_commands`](#47k) | Thu Nov 12, with `45k`/`46k` | +0.5 | `touch`, `cat`, `echo >`, `rm`, `rmdir` over your filesystem |
| [`54k_elf_loader`](#54k) | Fri Dec 4, with `51k`–`53k` | +1.0 | Teach the kernel to read a real ELF executable |
| [`55k_pipes`](#55k) | design-only, no starter | +1.0 | A bounded ring buffer behind two file descriptors, so `a \| b` works |

3.5 points are available; the total is capped at 3.

---

<a id="14c"></a>

## `14c_head` — stop early

`head` prints the first *n* lines of its input and then stops reading — and
the stopping is the exercise. `cat` and `wc` drain a stream to the end;
`grep` matches against every line; `head` is the one command whose correctness
depends on *not* consuming input it does not need. You parse a `-n` flag with
`ulib::parse_usize`, iterate with `ulib::Lines` over a fixed buffer, and
return the moment the count is reached.

It is the same shape as `13c_grep` and about the same length. It is extra
credit rather than core because the calendar has one Friday for `wc` and
`grep` together and no room for a third. Doing it makes
`53k_ship_your_commands` more fun in December, because there is more of your
own software to run.

---

<a id="41k"></a>

## `41k_devices` — the polled UART driver

The NS16550A is the template for every driver you will write: a handful of
memory-mapped registers, a status byte with flag masks, and a poll-then-transfer
loop. You write `uart::getc` and `uart::putc` against `LSR.DR` and `LSR.THRE`
with `read_volatile`/`write_volatile`, and the kernel reads its first keystroke.

It is demonstrated in L17 rather than assigned because `45k_console` replaces
it with an interrupt-driven version a week later, and `42k_boot_to_life`
already carries the finished driver. It is a clean, satisfying exercise if you
want more practice with MMIO before the console.

---

<a id="47k"></a>

## `47k_file_commands` — the four verbs

Exercise `46k_shell` gives rv6 a shell that moves around a namespace: `pwd`,
`ls`, `cd`, `mkdir`. This exercise teaches it to work on the things inside it —
`touch`, `cat`, `echo >`, `rm`, `rmdir` — each three or four lines over the
filesystem API you wrote in `40k_filesystem`. The thinness is the lesson: a
good API makes its clients boring. The lecture behind it is
[L21](../lectures/14-cs326-2026-11-24-file-commands-over-a-filesystem-api.md),
on November 24; the exercise is released with `45k`/`46k` on November 12, so
you may do it before or after the lecture. `48k_user_mode` carries the finished
commands, so nothing depends on your having written them.

---

<a id="54k"></a>

## `54k_elf_loader` — reading a real executable

Right now `exec` loads a **flat image**: the kernel copies bytes to virtual
address 0 and jumps to the first one. That works, but it is a lie of
convenience, and it is the last piece of hand-waving left in the kernel.

A flat image has no entry point, no per-segment permissions, and no `.bss`.
The consequences are real: your program's `_start` must be physically first in
the file, so adding a function above it silently breaks the program; every
page is mapped read-write-execute because there is nothing to say otherwise;
and you cannot have a mutable global, because there is nowhere to put one.

An ELF file answers all three. You implement `elf::load`:

- Parse the ELF64 header — check the magic, the class, and that `e_machine`
  really is RISC-V.
- Walk the program headers and map each `PT_LOAD` segment at its own
  `p_vaddr`, with the permissions its `p_flags` asks for.
- Zero the tail where `p_memsz > p_filesz` — that is `.bss`, and the C and
  Rust runtimes both assume it arrives zeroed.
- Return `e_entry` so `exec` can start the program wherever the linker put it.

About eighty lines. It is exactly what xv6's `exec` does, and after it, the
kernel loads a real executable format rather than a blob. It is released on
Friday, December 4 with `51k`–`53k` and builds on `53k`'s finished kernel, so
start it only once the core exercises for the day pass.

> One detail that trips everyone: `include_bytes!` gives you a byte slice with
> alignment 1, so you cannot cast it to a header struct and read fields. Read
> each field with `u32::from_le_bytes` on a subslice. That is both correct and
> the better lesson — the on-disk format is a byte layout, not a Rust struct.

---

<a id="55k"></a>

## `55k_pipes` — `a | b`

!!! note "Design-only"
    Unlike the other extra-credit exercises, this one has no OSlings starter —
    the specification below is complete, but you build it against your own
    kernel, in office hours, rather than receiving a skeleton. Talk to the
    instructor if you want to take it on; it is the most substantial thing on
    this page. The final exam covers pipes at the design level only, and no
    question depends on having built one.

A pipe is a bounded ring buffer with a reader end and a writer end, each
holding a file descriptor. Once it exists, the shell's `|` operator falls out
of machinery you already have: `fork` twice, `dup` the ends onto stdin and
stdout, `exec` both children.

You implement:

- `struct Pipe` — a fixed `[u8; 512]` buffer with read and write cursors, and
  a flag for each end being open. No allocation; it lives in a fixed table
  behind a `SpinLock`, in the same style as the process table.
- Blocking semantics: a reader on an empty pipe yields until a writer writes
  or closes; a writer on a full pipe yields until a reader drains it. This is
  where `38k_semaphores` pays off.
- End-of-file: `read` returns 0 when the buffer is empty **and** the last
  writer has closed. Getting this wrong is the classic pipe bug — either a
  reader that hangs forever or one that sees EOF too early.
- `SYS_PIPE` and `SYS_DUP`, using xv6's numbers so the syscall table stays
  honest.

---

## The payoff

Not extra credit — core, and the best moment in the course. On Friday,
December 4, `53k_ship_your_commands` compiles the `echo`, `cat`, `wc`, and
`grep` you wrote in September (and `head`, if you did it) for RISC-V and runs
them, unchanged, on the kernel you built. For reference, here is what those
commands compile to against a 64 KiB image budget:

| Command | Image | % of budget |
|---|---|---|
| `echo` | 384 bytes | 0.6% |
| `cat` | 1,256 bytes | 1.9% |
| `wc` | 1,821 bytes | 2.8% |
| `head` | 2,713 bytes | 4.1% |
| `grep` | 2,854 bytes | 4.4% |

That a working `grep` fits in under 3 KB with no allocator, no standard
library, and no runtime is worth sitting with for a moment.
