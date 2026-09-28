# Week 15 · exec and File Descriptors

> **Thu Dec 3** `49k_exec`, `50k_file_descriptors`
>
> Presented Tue Nov 24 for Thursday Dec 3; Thanksgiving falls between.
> Read **Essentials** before Nov 24 and again before Dec 3.
> **Going deeper** is optional and is not on the exam.

[Slides](15-cs326-2026-11-24-exec-and-file-descriptors-slides.html){ .md-button }
[Thursday Dec 3 prep](../prep/15-cs326-2026-12-03-prep-exec-and-file-descriptors.md){ .md-button }

## This week { #this-week }

In `53k` the `cat` and `wc` you wrote in Module 1 run on rv6 as ordinary user
programs. Your kernel must start each one by name, pass it the rest of the
command line, and let it open files. This week builds both halves.

Thanksgiving sits between this lecture and its session, so reread Essentials
before Dec 3; the Dec 1 lecture walks the prep page. The Final, Tue Dec 8,
covers all of Essentials; the [two-table design](#exam) is needed only there.

On Thursday Dec 3 you finish `exec`, which builds a fresh address space for a
named program and hands it its arguments, then give user programs file
descriptors. By Thursday night, `run cat notes.txt` at the `rv6$` prompt prints
a file that an unprivileged program opened and read for itself.

---

## Essentials { #essentials }

### Thursday · `49k` exec { #thu-49k }

In `52k` the shell becomes a user program that asks the kernel to start each
command by name. `49k_exec` builds that start, called for now from the kernel
shell's `run`.

#### After 48k: the door, and the two calls { #49k-two-calls }

`48k` ran only the program it was built around, with no arguments or files. It
also left a door: a call number in `a7`, arguments in `a0`–`a2`, then `ecall`.
The trampoline parks all 31 user registers in the process's **trapframe**; the
kernel answers in `a0` and reaches user memory only through `copyin` and
`copyout`.

Unix starts a program with two calls. `fork` copies the running process, and
`exec` keeps the process but replaces its program: new memory, new code, same
pid. `fork` arrives on Dec 4.

#### Programs by name: flat binaries { #49k-flat }

rv6 has no disk of executables. Instead the kernel carries a **program
table**: each entry is a name and one program's bytes. Each is a **flat
binary**: its byte 0 is its first instruction. Real systems load **ELF** files,
which begin with a header for the loader.

Those bytes are read at one address in the kernel and run at another, user
address 0, so they must be **position-independent**: every address is computed
from the `pc`. In the given programs, `la a1, msg` becomes:

```asm
1:  auipc a1, %pcrel_hi(msg)       # a1 = this pc + the distance's upper bits
    addi  a1, a1, %pcrel_lo(1b)    # a1 += the low 12 bits: a1 = &msg
```

Read `auipc` as "add an upper immediate to the pc". The distance to `msg` is
fixed at assembly time, and copying the image moves both ends.

#### Loading more than a page, and where it lands { #49k-load }

Any image loads like `48k`'s single page, once per page: allocate, zero, copy
the next 4,096 bytes or what is left, and map it R X U at the next virtual
address. A 10,000-byte image:

```text
image bytes   0..4095         4096..8191       8192..9999
physical      page A, full    page B, full     page C: 1,808 bytes, then 2,288 zeros
virtual       0x0000          0x1000           0x2000          (all R X U)
```

Zeroing matters because the allocator returns pages as their last owner left
them ([week 7](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#32k-building)).
The loader is given. Around the image, the address space is fixed:

| Virtual address | What lives there | Flags |
|---|---|---|
| `0x3F_FFFF_F000` | the trampoline | R X, no U |
| `0x3F_FFFF_E000` | this process's trapframe | R W, no U |
| `0x0001_0000` | one stack page, filled down from `0x1_1000` | R W U |
| below `0x1_0000` | unmapped, down to the image's last page | none |
| `0x0000_0000` | the image, 1 to 16 pages | R X U |

The stack sits where a 17th image page would go, so unmapped pages separate any
smaller image from its stack, and an access past the image's end faults. The
image has no W: a store into it faults, and writable data lives on the stack.

#### argc and argv, on the new stack { #49k-argv }

C's `main(int argc, char **argv)` is the model: a new program gets the count,
**argc**, in `a0`, and in `a1` **argv**, the address of an array of string
pointers. The name counts, so `run echo pie is good` has argc 4.

Both go on the new stack, written through `copyout`. Each string and its
**NUL**, the zero byte that ends it, goes below the last, rounded down to a
multiple of 8. Below them goes the array, argc + 1 eight-byte entries ending in
NULL, rounded down to 16. `sp` ends on the array:

```text
0x1_1000   top of the stack page
0x1_0FF8   "echo\0"     (3 bytes above it unused)
0x1_0FF0   "pie\0"
0x1_0FE8   "is\0"
0x1_0FE0   "good\0"
0x1_0FD8   (8 bytes unused: the 16-byte rounding)
0x1_0FD0   argv[4] = 0          the NULL that ends the list
0x1_0FC8   argv[3] = 0x1_0FE0
0x1_0FC0   argv[2] = 0x1_0FE8
0x1_0FB8   argv[1] = 0x1_0FF0
0x1_0FB0   argv[0] = 0x1_0FF8   <- sp = a1 = 0x1_0FB0, and a0 = 4
```

The strings go first because the array holds their user virtual addresses. C
arrays carry no length, hence the NULL, and 16 is the
calling convention's rule for `sp`
([week 6](06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#20a-registers)).

#### Starting it, and failing cleanly { #49k-start }

A process that never ran has nothing to resume, so the kernel writes four
values into its trapframe. The saved program counter is `0`, the image's first
instruction; `sp` is the array's address; `a0` is argc; and `a1` is argv, equal
to `sp`.

The kernel never jumps into user code. It runs `48k`'s return path, like
[week 9's forged context](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#35k-fresh)
one level up: the trampoline loads all 31 registers, and `sret` drops to user mode at the saved program counter.

Building can fail: no such program, no free page, more than 16 words counting
the name, or a word over 63 characters. A failed launch leaves no trace, so in
`49k` given code releases whatever the build had claimed. On Dec 4 `exec`
replaces a running program, and a failed `exec` returns -1 to it. The
principle becomes an order: build the new world before destroying the old.

> **The one thing to get right:** `[fail] argc came through as 0, expected 3`,
> though the program ran and exited. Its code and stack were mapped; it lacked a
> register. A program's first registers come from its trapframe, which starts as
> zeros, so a value nobody stored arrives as 0.

### Thursday · `50k` File descriptors { #thu-50k }

In `53k` your Module 1 `cat` opens a file by name and reads it to the end.
`50k_file_descriptors` adds the four calls it makes: `open`, `read`, `write`
and `close`.

#### A descriptor is a small integer { #50k-fd }

A user program cannot reach an inode or the kernel's open-file entries, which
live in kernel memory. `open` hands back a **file descriptor** (fd), a small
integer, and every later call names the file by it. The number means something
only through this process's table: the same 3 in two processes can name two
different files.

That makes a descriptor a **capability**: holding it is the right to use it.
Guessing forges nothing, because the kernel rechecks every use: the number in
range, the slot open, the mode allowing the call, and the buffer in user memory
([week 7](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#exam-walkaddr)).

rv6 opens 0, 1 and 2 on the console in every new process: standard input,
output and error. The numbering is a Unix agreement; the kernel treats none of
them specially.

#### The per-process file table { #50k-table }

Each PCB gains a table of 16 open-file entries, and fd *n* is entry *n*. An
entry records what is open, which inode, the offset, and whether reads and
writes are allowed. After a file is opened read-only and read 40 bytes:

```text
fd   what      inode   offset   read   write
0    console   -       -        yes    yes
1    console   -       -        yes    yes
2    console   -       -        yes    yes
3    file      5       40       yes    no
4-15 free
```

A new descriptor takes the lowest free slot, and that is a promise: close 0,
then open a file, and the file is your standard input.

#### The offset makes a descriptor stateful { #50k-offset }

An open-file entry's **offset** counts the bytes read or written through it. A
call that moves n bytes starts there and adds n; `read` returns n, so at the
end it returns 0. One 30-byte file, opened twice, as `a` and `b`:

```text
call               returns   a's offset   b's offset
read(a, buf, 20)   20        20           0
read(b, buf, 8)    8         20           8
read(a, buf, 20)   10        30           8     a short read: 10 left
read(a, buf, 20)   0         30           8     a is at the end; b is not
```

`cat` loops until `read` returns 0; a short read is not the end. Each `open`
made its own entry, so `b` has 22 bytes to go. A Rust iterator is the same
kind of stateful handle:

```rust
let mut letters = "pie".chars();
letters.next();   // Some('p')
letters.next();   // Some('i')
letters.next();   // Some('e')
letters.next();   // None: used up
```

Read `letters` as a place in the string, not the string: each call answers
from where the last one stopped, and `None` plays the part of `read`'s 0.

#### `open` and its flags { #50k-open }

`open(path, flags)` is the one file call that takes a name. It finds or
creates the file, fills an entry with offset 0, and returns the descriptor. The
**flags** are yes-or-no bits in one integer, combined with `|` and tested with
`&` as in
[week 7](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#33k-bits):

| Flag | Value | Means |
|---|---|---|
| `O_RDONLY` | `0x000` | read only |
| `O_WRONLY` | `0x001` | write only |
| `O_RDWR` | `0x002` | read and write |
| `O_CREATE` | `0x200` | create it if missing |
| `O_TRUNC` | `0x400` | empty the file first |

So `O_CREATE | O_RDWR` is `0x202`. `O_RDONLY` is the odd one: it is 0, a bit
you cannot test, so a file opened with neither write bit set is read-only.

A path crosses the wall with no length attached: `"notes"` is six bytes in user
memory, the last a NUL, and the kernel finds the end only by reaching it, one
byte at a time.

#### One read and write path { #50k-uniform }

The user-mode `cat` makes the same two calls for every chunk: `read` on fd 3
and `write` on fd 1. One lands in the filesystem at the offset, the other on
the serial port, and `cat` cannot tell which. The kernel settles it inside
each call, from the entry. That is Unix's **everything is a file**: one
interface over very different things, like `07r`'s `Out` trait.

> **The one thing to get right:** `[fail] cat never finished`: a timeout, not
> wrong bytes. `cat` stops when `read` returns 0 at the end, or -1 on an error.
> If the offset stays at 0, every call starts again at byte 0: the file is
> never used up, so `read` returns neither.

### For the exam { #exam }

*Not needed on Thursday. On the Final.*

**Two tables, not one** · *Final.* Unix splits what rv6 keeps in one entry.
Each process has a **descriptor table** of pointers into one system-wide
**open-file table**, whose entries hold the offset, the access mode and a
reference count, and point at the inode. rv6 stores the whole entry by value in
the per-process table, so it has no middle table. After an `open`, a `fork`,
and a `dup(3)` in the child:
{ #exam-two-tables }

```text
parent  fd 3 --+
child   fd 3 --+--> open file: offset 120, write-only, count 3 --> inode 7
child   fd 4 --+
```

**One offset, shared** · *Final.* `dup(fd)` copies a pointer, and `fork` copies
the whole descriptor table, pointer by pointer. Either way, two descriptors
share one offset. That is why a shell's children can write one output file in
turn: `(echo a; echo b) > f` leaves two lines. Two separate `open` calls make
two entries, and two offsets, on any system. rv6's `fork` copies each entry,
offset included, so a child's write starts at its own offset and can overwrite
the parent's bytes.
{ #exam-shared-offset }

**Reference counts** · *Final.* An entry's count says how many descriptors, in
any process, point at it. `open` sets it to 1; `dup` adds one, and `fork` adds
one for each open descriptor; `close` subtracts one. The entry is freed, with
its offset, only when the count reaches 0, so one process's `close` never cuts
off another. rv6 shares nothing and needs no count: its `close` just empties the
slot.
{ #exam-refcount }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday, and nothing here is on the
exam.*

### What a real `exec` puts on the stack { #deeper-real-stack }

rv6 stops at argv. On Linux the kernel builds more, and it puts argc itself on
the stack rather than in a register. Above argc come the argv pointers and a
NULL, then **envp**, pointers to the environment strings, and another NULL.
Then comes the **auxiliary vector**, key and value pairs for the C library's
start-up code: the program headers, the entry point, the vDSO (kernel-supplied
code for calls such as `clock_gettime`), and `AT_RANDOM`, sixteen random bytes
that seed stack canaries. The strings sit highest, as in rv6.

`argv[0]` is a convention the kernel never checks. BusyBox is one binary that
reads `argv[0]` to decide which of its tools to be. `login` starts your shell
with an `argv[0]` that begins with `-`, which tells it to act as a login shell.

### ELF and `fence.i` { #deeper-elf }

An ELF file opens with a header, then a table of **program headers**, one for
each region the program wants in memory. xv6's `exec` walks that table; the
xv6 book's chapter 3, "Code: exec", goes through it. On Linux,
`readelf -l /bin/ls` prints the table for a real program. The extra-credit
`54k_elf_loader`, released Dec 4, teaches rv6 to read ELF.

The given loader, `load_segment()` (`vm.rs`), ends with `fence.i`. It has just
written instructions with ordinary stores, and RISC-V does not promise that
instruction fetch sees them until that hart runs a `fence.i`. x86 keeps
instruction fetch coherent with stores in hardware, so an x86 loader has no
such line.

### Linux's point of no return { #deeper-no-return }

A real `exec` replaces a running program, so a failure has two cases. Before
the old memory is released, `exec` can still return an error to its caller.
After, there is no caller left. Linux names that line: `begin_new_exec()` in
`fs/exec.c` (called `flush_old_exec()` before Linux 5.8) sets a "point of no
return" flag, and a failure after it kills the process with `SIGSEGV`. So
everything that can fail, from opening the file to reading its headers and
copying the arguments, happens first.

### Capabilities and ambient authority { #deeper-capability }

A descriptor is authority you hold. A path is authority the kernel works out
again each time, from your identity and the file's permissions. Unix has both,
and the difference shows. A program that checks a path and then opens it can be
fooled when the name changes in between: a **time-of-check-to-time-of-use**
(TOCTOU) race. A descriptor keeps naming the file it was opened on.

Newer interfaces lean on descriptors. `openat` resolves a path relative to a
directory descriptor. FreeBSD's Capsicum lets a process give up path lookups
entirely and keep only its descriptors. Linux's `pidfd` names a process by
descriptor instead of by a pid that can be reused. A descriptor can even move
between processes: a Unix-domain socket carries one with `SCM_RIGHTS`, and the
kernel installs a new descriptor on the far side.

### `O_TRUNC` and `O_APPEND` { #deeper-flags }

A shell runs `cmd > out` by opening `out` with `O_TRUNC` before the command
starts. That order explains an old trap: `sort notes > notes` empties `notes`
before `sort` reads a byte of it.

`>>` opens with `O_APPEND` instead, and user code cannot fake that flag. Asking
for the file's size and then writing there takes two steps, so two processes
appending to one log can both see size 100 and both write at 100. With
`O_APPEND` the kernel moves the offset to the end and writes in one step. rv6
has neither `O_APPEND` nor a way to move an offset. A file opened without
`O_TRUNC` is written from byte 0, over what is there, and keeps its old size if
you write less.

### A name removed while a file is open { #deeper-unlink }

On Linux, `rm` removes a name, not a file. If a process still has the file
open, its data lives on without a name until the last descriptor closes. That is
why deleting a huge log a running server holds open frees no disk space, and
`lsof +L1` lists such files.

rv6's entry holds a bare inode number, and `unlink()` (`fs.rs`) frees the inode
at once for the next file to reuse. If a descriptor could outlive its name, a
later read would quietly return some other file's bytes. rv6 escapes by
accident: only the kernel shell's `rm` and `rmdir` unlink, and neither can run
while a user program is running. A kernel with an `unlink` system call needs a count of open
references on each inode.

### Practice problems { #problems }

#### Problem 1: Build the argv block { #problem-1 }

A user types `run args hello-there 7`. Use [the layout rules](#49k-argv): each
string, NUL included, goes below the last with its address rounded down to a
multiple of 8. The pointer array, argc + 1 entries, goes below the strings,
rounded down to 16. The stack page's top is `0x1_1000`.

1. What is argc, and what exit status does `run` report for `args`?
2. At what address does each string start?
3. What are `a1` and `sp` at the first instruction, and what does `argv[1]` hold?
4. How many bytes of the page does the rounding leave unused?
5. What happens with one 64-character argument? With 16 arguments after `args`?

<details markdown="1">
<summary>Click to reveal solution</summary>

1. argc = 3: `args`, `hello-there` and `7`. `args` exits with its argc, so
   `run` reports status 3.
2. Each string, from the top down:

    ```text
    "args\0"          5 bytes   0x1_1000 - 5  = 0x1_0FFB  -> 0x1_0FF8
    "hello-there\0"  12 bytes   0x1_0FF8 - 12 = 0x1_0FEC  -> 0x1_0FE8
    "7\0"             2 bytes   0x1_0FE8 - 2  = 0x1_0FE6  -> 0x1_0FE0
    ```

3. The array holds 4 pointers, 32 bytes: `0x1_0FE0 - 0x20 = 0x1_0FC0`, already a
   multiple of 16. So `a1 = sp = 0x1_0FC0`, and `argv[1]`, at `0x1_0FC8`,
   holds `0x1_0FE8`.
4. 13 bytes: 3 above `"args"` (`0x1_0FFD`–`0x1_0FFF`), 4 above `"hello-there"`
   (`0x1_0FF4`–`0x1_0FF7`), 6 above `"7"` (`0x1_0FE2`–`0x1_0FE7`), and none for
   the array.
5. A 64-character word needs 65 bytes with its NUL, over the limit of 64. Sixteen
   arguments make argc 17, over the limit of 16. Either way the launch fails
   before the program runs, and `run` prints `run: could not start the
   program`.

</details>

#### Problem 2: Where does it fault? { #problem-2 }

Suppose the program table held a 12,500-byte program. For each access it makes,
say whether it succeeds. If it faults, give the exception code in `scause` and
the reason.

1. It loads a byte from `0x30D0`.
2. It loads a byte from `0x3100`.
3. It loads a byte from `0x4000`.
4. It stores a byte to `0x0100`.
5. It jumps to `0x1_0000`.
6. It loads 8 bytes from `0x3F_FFFF_E000`.

<details markdown="1">
<summary>Click to reveal solution</summary>

`12,500 = 3 × 4,096 + 212`, so the image fills four pages, `0x0000`–`0x3FFF`.
The last page holds 212 image bytes, then zeros.

1. **Succeeds.** `0x30D0 - 0x3000 = 0xD0 = 208`, below 212: an image byte.
2. **Succeeds, and reads 0.** `0x100 = 256` lands in the zeroed tail of a mapped
   page.
3. **Load page fault, 13.** `0x4000` is in the unmapped gap, pages 4 through 15.
4. **Store page fault, 15.** The image is R X U, with no W.
5. **Instruction page fault, 12.** The stack page is R W U, with no X.
6. **Load page fault, 13.** The trapframe is mapped, but without U, and user
   mode may touch only U pages.

In each fault the kernel ends the run, and `run` prints `run: the program
faulted`.

</details>

#### Problem 3: Decode the flags, then predict { #problem-3 }

`notes` holds 50 bytes. A process with only fds 0–2 open runs these calls in
order. Give each return value, and the file's size at the end.

```text
a = open("notes", 0x402)
read(a, buf, 10)
write(a, "hello", 5)
read(a, buf, 10)
b = open("notes", 0x000)
read(b, buf, 10)
write(b, "x", 1)
```

<details markdown="1">
<summary>Click to reveal solution</summary>

`0x402 = O_TRUNC | O_RDWR`: read and write, and empty the file first.

| Call | Returns | Why |
|---|---|---|
| `open(..., 0x402)` | 3 | the lowest free slot; `notes` is now 0 bytes |
| `read(a, ...)` | 0 | the offset, 0, is already at the end |
| `write(a, ...)` | 5 | `notes` is now `hello`; `a`'s offset is 5 |
| `read(a, ...)` | 0 | the write moved the same offset to the end |
| `open(..., 0x000)` | 4 | a separate entry, with its own offset 0 |
| `read(b, ...)` | 5 | `hello`: 10 asked, 5 left |
| `write(b, ...)` | -1 | `b` is read-only |

The file ends at 5 bytes. rv6 has no call to move an offset back, so `a` can
never read what it wrote; a second descriptor can.

</details>

#### Problem 4: Two designs, one fork { #problem-4 }

On the finished rv6, with `fork` from `51k`, a process creates `log` and opens
it as fd 3 for writing. It writes 10 bytes and forks. The child writes 6 bytes
to fd 3 and exits. The parent waits for it, then writes 4 bytes to fd 3.

1. On rv6, which bytes does each write cover, and how long is `log`?
2. With Unix's [shared open-file table](#exam-two-tables)?
3. Under Unix, what is the entry's reference count after the open, after the
   fork, after the child exits, and after the parent closes fd 3?

<details markdown="1">
<summary>Click to reveal solution</summary>

1. rv6's `fork` copies each entry, offset included. The parent writes bytes
   0–9, leaving its offset at 10. The child's copy also starts at 10, so it
   writes 10–15, and `log` grows to 16 bytes. The parent's offset is still 10:
   its 4 bytes land on 10–13, over the child's first four. `log` stays 16 bytes,
   and 4 of the child's 6 are gone.
2. One shared offset: the parent writes 0–9, the child 10–15, then the parent
   16–19. `log` is 20 bytes, and nothing is lost.
3. 1, then 2: the child's fd 3 points at the same entry. The child's exit
   closes its descriptors, leaving 1, and the parent's close makes it 0, which
   frees the entry.

</details>

#### Problem 5: Try to forge authority { #problem-5 }

A process has fds 0–2 on the console and fd 3 open read-only on a 50-byte file.
Give each call's result, and the check that decides it.

1. `read(16, buf, 8)`
2. `read(9, buf, 8)`
3. `write(0, "hi", 2)`
4. `write(1, 0x8000_0000, 16)`
5. `read(3, 0x3F_FFFF_E000, 16)`
6. `close(3)`, then `close(3)` again

<details markdown="1">
<summary>Click to reveal solution</summary>

1. **-1.** The table's slots are 0–15, so the range check refuses 16 before any
   lookup.
2. **-1.** Slot 9 is in range, but free: nothing was ever opened there.
3. **2, and `hi` prints.** fd 0 is the console, opened readable and writable. The
   convention says 0 is for input; the kernel enforces only the entry's mode.
4. **-1.** The descriptor is fine; the buffer is not. `0x8000_0000` is kernel RAM
   and is not mapped in the user's page table, so `copyin` refuses it.
5. **-1.** The trapframe is mapped, but without U. `copyout` will not touch a
   page that the user could not touch itself.
6. **0, then -1.** The first `close` frees slot 3; the second finds it free.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| `exec` | Replace a process's program: new memory and code, same process | `49k`, `52k` |
| Flat binary | A program whose byte 0 is its first instruction: no header, one fixed load address | `49k` |
| Position-independent code | Code that names addresses only as distances from the `pc` | `49k`–`51k` |
| argc, argv | The argument count in `a0`; in `a1`, a NULL-ended array of string pointers | `49k`, `53k` |
| Trapframe | The saved user registers; writing it is how a program starts | `48k`, `49k`, `51k` |
| File descriptor | A small integer naming an open file inside one process | `50k` onward |
| Standard streams | fds 0, 1 and 2, open on the console when every process starts | `50k`, `52k` |
| Per-process file table | 16 entries per process; fd *n* is entry *n* | `50k`, `51k` |
| Offset | The count of bytes read or written through an entry; the next call starts there | `50k` |
| Open flags | A bitmask: the access mode, plus `O_CREATE` and `O_TRUNC` | `50k`, `53k` |
| Everything is a file | One read and write interface over the console, files, and more | `50k`, `53k` |
| Open-file table | Unix's shared middle table: offset, mode, reference count | Final |

## Further reading { #reading }

- [rv6 Architecture: address spaces](../guides/rv6-architecture.md#address-spaces):
  the user address space and its constants, and
  [the program table](../guides/rv6-architecture.md#the-program-table).
- [rv6 Architecture: the system call table](../guides/rv6-architecture.md#the-system-call-table)
  and [the user syscall round trip](../guides/rv6-architecture.md#path-3-the-user-syscall-round-trip).
- [Key Concepts: file descriptor](../guides/key-concepts.md#file-descriptor)
  and [`exec`](../guides/key-concepts.md#exec).
- [Sv39 Paging: the page-table entry](../guides/sv39-paging.md#the-page-table-entry):
  the U bit every user pointer must carry.
- [The xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf):
  chapter 1, "Operating system interfaces"; chapter 3's "Code: exec"; and
  chapter 8's "File descriptor layer", the reference-counted table rv6 leaves
  out.
- Arpaci-Dusseau and Arpaci-Dusseau,
  [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/),
  chapter 5, "Process API", and chapter 39, "Files and Directories".
- Ritchie and Thompson, "The UNIX Time-Sharing System", *Communications of the
  ACM*, 1974: descriptors, `fork` and `exec` in their original words.
