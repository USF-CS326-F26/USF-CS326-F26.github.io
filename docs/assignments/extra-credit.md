# Extra Credit

Up to **+4%** on the final grade. None of this is required, and none of it is
graded on a curve — if you do the work, you get the points.

Extra credit is worked in the same way as everything else: in class, or in
office hours with the TA. It is released alongside `ex22` in the final week.

| Exercise | Points | What you build |
|---|---|---|
| [`22_userland`](#ex22) | +2 | `exec` as a system call — the shell becomes an ordinary user program |
| [`25_ship_your_commands`](#ex25) | +0.5 | Run the commands you wrote in week 3 on your own kernel |
| [Pipes](#ex24) | +0.5 | A bounded ring buffer behind two file descriptors, so `a \| b` works — *design-only; see below* |
| [`23_elf_loader`](#ex23) | +0.5 | Teach the kernel to read a real ELF executable |
| `11_devices` | +0.5 | The polled UART driver, if you would rather write it than watch it |
| `c02_wc`, `c03_head` | +0.5 | The two optional command labs |

---

<a id="ex22"></a>

## `22_userland` — the shell in user mode

The finish line of the core course. `exec` becomes a real system call, and the
shell stops being kernel code with unlimited power and becomes an ordinary
unprivileged program that happens to start other programs.

Worth doing for one reason above all: after it, the sentence "the shell is
just a program" stops being something you were told and becomes something you
built.

It is extra credit rather than required only because it lands in the last week
and is eight markers deep. If you have time, do this one first.

---

<a id="ex25"></a>

## `25_ship_your_commands` — the payoff

**Do this one.** It is about twenty minutes once `ex22` passes, and it is the
best moment in the course.

In week 3 you wrote `echo`, `cat`, `wc`, `head`, and `grep` against the `ulib`
façade, and they ran on your laptop under `cargo test`. Those same source
files — unchanged, not ported, not rewritten — now compile for RISC-V and run
on the kernel you built.

```bash
oslings ship            # compile your commands for the kernel and embed them
cd rv6 && cargo run     # boot it
```

```text
rv6$ echo the cat sat > notes.txt
rv6$ run mygrep cat notes.txt
the cat sat
rv6$ run mywc notes.txt
       1       3      12 notes.txt
```

Every layer under those lines is yours: the shell, the syscall that returned
the bytes, the file descriptor that named the file, the page table that mapped
the program, the allocator that provided the page, and the boot code that
started the machine.

For reference, here is what your commands actually compile to. The image
budget is 64 KiB:

| Command | Image | % of budget |
|---|---|---|
| `echo` | 384 bytes | 0.6% |
| `cat` | 1,256 bytes | 1.9% |
| `wc` | 1,821 bytes | 2.8% |
| `head` | 2,713 bytes | 4.1% |
| `grep` | 2,854 bytes | 4.4% |

That a working `grep` fits in under 3 KB with no allocator, no standard
library, and no runtime is worth sitting with for a moment.

---

<a id="ex24"></a>

## Pipes — `a | b`

!!! note "Design-only for now"
    Unlike the other extra-credit exercises, this one has no `oslings` starter
    yet — the specification below is complete, but you build it against your
    own kernel rather than receiving a skeleton. Talk to the instructor if you
    want to take it on; it is the most substantial thing on this page.

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
  where `08_semaphores` pays off.
- End-of-file: `read` returns 0 when the buffer is empty **and** the last
  writer has closed. Getting this wrong is the classic pipe bug — either a
  reader that hangs forever or one that sees EOF too early.
- `SYS_PIPE` and `SYS_DUP`, using xv6's numbers so the syscall table stays
  honest.

---

<a id="ex23"></a>

## `23_elf_loader` — reading a real executable

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
kernel loads a real executable format rather than a blob.

> One detail that trips everyone: `include_bytes!` gives you a byte slice with
> alignment 1, so you cannot cast it to a header struct and read fields. Read
> each field with `u32::from_le_bytes` on a subslice. That is both correct and
> the better lesson — the on-disk format is a byte layout, not a Rust struct.

---

## Optional exercises

**`11_devices`** — the polled UART driver. It is demonstrated rather than
assigned because `15_console` replaces it with an interrupt-driven version a
week later, so writing it is genuinely optional. It is also a clean, satisfying
exercise if you want more practice with MMIO before the console.

**`c02_wc` and `c03_head`** — the two command labs the schedule marks optional.
Both are the same shape as `cat` and take a session slot the calendar does not
have. Doing them makes `25_ship_your_commands` more fun, because there is more
of your own software to run.
