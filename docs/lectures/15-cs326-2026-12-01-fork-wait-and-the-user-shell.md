# Week 15 · fork, wait, and the User Shell

> **Thu Dec 3** `49k_exec`, `50k_file_descriptors` · **Fri Dec 4** `51k_fork_wait`, `52k_userland`, `53k_ship_your_commands` · extra credit `54k_elf_loader`
>
> Thursday's exercises were taught Tue Nov 24, in
> [Week 15 · exec and File Descriptors](15-cs326-2026-11-24-exec-and-file-descriptors.md).
> This page is for Friday.
> Read **Essentials** before Tuesday: it is what Friday assumes.
> **Going deeper** is optional and is not on the exam.

[Slides](15-cs326-2026-12-01-fork-wait-and-the-user-shell-slides.html){ .md-button }
[Thursday prep](../prep/15-cs326-2026-12-03-prep-exec-and-file-descriptors.md){ .md-button }
[Friday prep](../prep/15-cs326-2026-12-04-prep-fork-userland-and-ship.md){ .md-button }

## This week { #this-week }

The final, Tue Dec 8, always asks one long question: walk one command
through the whole system, from a keypress to the next prompt. This week
supplies the last layers of that walk.

Thursday rests on the Nov 24 lecture, where `exec` starts a program by name
and a file descriptor indexes a table of open files. Reread
[its Essentials](15-cs326-2026-11-24-exec-and-file-descriptors.md#essentials)
before Thursday.

On Friday, `fork` copies a running process, `exit` and `wait` hand its result
back, and the round robin from `36k` finally has two processes to choose
between. Then `exec` becomes a system call and the shell leaves the kernel. By
Friday night, `$ mycat notes.txt` runs the `cat` you wrote in September on your
own kernel.

---

## Essentials { #essentials }

### Friday · `51k` `fork`, `exit`, and `wait` { #fri-51k }

In `52k` your shell copies itself for every command, then waits for the copy.
`51k_fork_wait` builds the copy, the ending, and the wait.

#### One call, two returns { #51k-fork }

`fork` creates a **child**: a new process that is a copy of the calling
**parent**. Both then return from the same call, with the same memory. Only the
return value differs: the parent gets the child's pid, and the child gets 0.

Zero is safe because no process has pid 0. With no free slot or no memory,
`fork` makes nothing and returns -1. A program branches on all three answers:

```rust
let pid = fork();
match pid {
    0 => run_as_child(),            // only the copy sees 0
    p if p > 0 => wait_for(p),      // the parent holds the child's pid
    _ => complain("no free slot"),  // -1: nothing was copied
}
```

Read the `match` as one question answered twice: each process takes its own
arm, because the return value is all that differs.

#### What the child gets { #51k-child }

The program in the child must not be able to tell it is a copy, except by one
value. So the kernel copies everything the program can see, and makes new what
it keeps about the process itself:

| The child's… | Is | Because |
|---|---|---|
| user pages | copied, at the same virtual addresses | writes stay private |
| open files | copied | fd 1 still means what it meant |
| saved user registers | copied, except one | it resumes where the parent will |
| pid | new | a pid names one run, forever |
| kernel stack and trapframe page | new | each process traps on its own |
| parent | the caller | its exit status needs an addressee |

The memory copy walks the parent's page table, giving the child a fresh page
for every user page, same address, same permissions. Only the trampoline is
shared. Open files are copied by value, offset included; a Unix child instead
[shares each open file and its offset](15-cs326-2026-11-24-exec-and-file-descriptors.md#exam-shared-offset)
with its parent, a difference the final asks about.

The copied program counter puts the child just past the `ecall`, like the
parent. The one register that must differ is the child's saved `a0`: the kernel
plants 0 there. The parent's `a0` gets the pid the ordinary way: the trap
handler stores every system call's return value in the caller's saved `a0`.

#### `exit`, the zombie, and `wait` { #51k-zombie }

`exit(status)` ends a process, but the kernel cannot free its slot yet. The
status is addressed to the parent, who may not be listening. So the process
becomes a **zombie**: it never runs again, and its slot keeps the pid and the
status. [Week 9](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-states)
drew that state.

`wait` **reaps** a zombie: it copies the status out and frees the slot. It has
three outcomes:

| The caller has… | `wait` |
|---|---|
| a zombie child | reaps it and returns its pid |
| children, none finished | yields, then looks again |
| no children at all | returns -1 at once |

The middle row is how rv6 blocks: the parent, `Running` while it scans, marks
itself `Runnable` (never `Sleeping`), yields, and rescans the table whenever it
is picked.

#### The scheduler finally has work { #51k-scheduler }

After a `fork` the running parent has a `Runnable` child, and your `36k` round
robin finally has a choice. The loop asks your policy for a slot, switches in
with your `35k` switch, and gets the CPU back only when that process lets go of
it.

It gives it up only by yielding inside `wait` or by exiting. rv6 is
**cooperative**: the `44k` timer still ticks, but nothing takes the CPU away. A
process that has never run starts at `forkret`, which takes the trap-return
path into user mode.

In `forktest` the parent forks, writes `parent`, and waits; the child writes
`child` and exits 7. The parent, in slot 0, then exits with that status plus
10. States are as each turn ends; during its own turn a process is `Running`:

```text
turn     what happens                             slot 0    slot 1    prints
parent   forks, writes, wait finds no zombie      Runnable  Runnable  parent
child    fork returned 0; writes; exit(7)         Runnable  Zombie    child
parent   wait reaps slot 1, status 7; exit(17)    Zombie    Unused
```

`parent` prints first: nothing preempts the parent until it waits.

> **The one thing to get right:** `[fail] only the parent ran`, and the output
> shows `parent` twice. The child's registers were an exact copy, so its saved
> `a0` still held the parent's value from before the call, and it took the
> parent's branch. A copy that differs in nothing is not yet a child.

### Friday · `52k` `exec` as a system call { #fri-52k }

In `53k` your September commands run as programs your shell starts.
`52k_userland` makes `exec` a system call and moves the shell out of the
kernel.

#### Replace the program, keep the process { #52k-exec }

After `fork`, the child is running the shell's code, and `mycat` is nowhere in
it. **`exec`** brings it in: it replaces the caller's program and keeps the
process. `49k` loaded a program into a fresh process; `52k` loads one into a
process already running.

| Survives `exec` | Replaced by `exec` |
|---|---|
| pid, parent, process slot | the page table, and every user page with it |
| open files | code, data, stack, and argv |
| kernel stack, trapframe page | the [four starting registers](15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-start) from `49k` |

The surviving open files are how a shell hands a program its input and output
([For the exam](#exam-two-calls)). Nothing the CPU is using lives in the old
pages: from the trap until the trampoline's return path, `satp` holds the
kernel's table ([why no fence is needed](#exam-sfence)), so the kernel may give
them back mid-call.

#### `exec` does not return on success { #52k-no-return }

Only a failed `exec` comes back, with -1, to a caller that is still itself. A
successful one resumes somewhere else entirely:

```text
exec("mycat", argv) succeeds   next instruction: mycat's first, at address 0
exec("mycta", argv) fails      next instruction: the one after the ecall, a0 = -1
```

Read every line after an `exec` as its failure path, where a shell's child
prints `exec: not found`.

#### The shell leaves the kernel { #52k-shell }

Since `46k` the shell has lived in the kernel. `sh` is a user program instead,
started by the kernel shell's `run sh`, with the prompt `$ `. It loops forever:

```text
write "$ ", then read a line from fd 0 one byte per call, echoing each to fd 1
split the line into words: argv
if argv[0] is "exit": exit(0)
fork; the child calls exec(argv[0], argv), printing "exec: not found" if it returns
the parent waits, then loops
```

Read every line but the split as system calls: `sh` has no other way to touch
anything. `exit` is a **builtin**, a command the shell runs itself, because its
effect is on the shell.

> **The one thing to get right:** `[fail] execfail did not finish cleanly`.
> The program execs a name that does not exist and should go on to `exit(7)`.
> The failed `exec` had already given back the old program's pages, so its -1
> returned into memory that was gone. Let go of nothing old until everything
> new exists.

### Friday · `53k` Ship your commands { #fri-53k }

`53k_ship_your_commands` runs the `echo`, `cat`, `wc` and `grep` you wrote in
September on your own kernel, without editing a line.

#### One source, two backends { #53k-backends }

In `10c`–`13c` you called `ulib`, never `std`. It has two private
**backends**, and the compile target picks one: `std` on your laptop, system
calls into rv6 on `riscv64gc-unknown-none-elf`. Apart from one `cfg_attr` line
that turns on `no_std` for the kernel target, your command contains no `cfg`.
The switch is a fact about the target, and `rustc` prints it (one line of many,
on a Mac):

```text
$ rustc --print cfg --target riscv64gc-unknown-none-elf
target_os="none"
$ rustc --print cfg
target_os="macos"
```

Read `target_os = "none"` as "no operating system underneath"; it follows from
the target, so it cannot disagree with the build. On rv6 each `ulib`
system-call wrapper is one `ecall`, in `48k`'s convention:

```rust
fn getpid() -> isize {
    let pid: isize;
    unsafe { core::arch::asm!("ecall", in("a7") 11usize, lateout("a0") pid) };
    pid
}
```

Read `in("a7") 11usize` as "the call number goes in `a7`", and
`lateout("a0") pid` as "afterward, `a0` holds the answer".

#### What `oslings ship` does { #53k-ship }

rv6 cannot read ELF, so `oslings ship` makes each command something it can
load:

```text
your September cat.rs           unchanged
  built for riscv64gc-unknown-none-elf, in release mode
an ELF file                      linked at address 0
  loadable segments laid out by address; gaps become zeros
a flat image                     copied to address 0, run from its first byte
  embedded in the kernel with include_bytes!
mycat                            a name exec can find
```

Inside the kernel they are `myecho`, `mycat`, `mywc` and `mygrep`, since rv6's
own `echo` and `cat` demos would otherwise run instead. Each image is a few
kilobytes at most, far inside the loader's 64 KiB: no allocator, no formatting
machinery, no runtime came along.

> **The one thing to get right:** a command that passed `cargo test` in
> September stops `oslings ship` with ``cannot find macro `format` in this
> scope``. On your laptop the `std` prelude supplied it; on the kernel target
> the crate is `no_std`, with no allocator, so `format!`, `println!`, `Vec` and
> `String` do not exist.

#### The long question, one layer per line { #53k-layers }

The final's long question, for `$ mycat notes.txt`, from Enter to the next
prompt:

```text
UART, PLIC   Enter: IRQ 10 while sh waits in read; trap to stvec, scause 0x80…09
console      the handler claims 10, moves the byte into the ring, completes
sh           read(0) returns 1; sh echoes it on fd 1, sees Enter, splits words
fork         ecall, a7 = 1: a copy of sh, saved a0 = 0; sh's wait yields
scheduler    round robin picks the child: forkret, then sret into its copy of sh
exec         ecall, a7 = 7: finds mycat's shipped image, builds a new page table
user mode    sepc = 0, satp = the new table, SPP = 0; sret, a0 = 2, a1 = argv
files        open returns 3; read(3), write(1) trap with scause 8, a7 = 5 and 16
UART         the console fd hands each byte of write(1) to the UART driver
exit, wait   exit(0) leaves a zombie; sh reaps it, writes "$ ", reads again
```

The past form, `rv6$ ls`, is shorter: the kernel shell runs `ls` itself, so its
walk has no `fork`, `exec` or user mode.

> **Extra credit · `54k_elf_loader`** `oslings ship` does rv6's loading ahead
> of time, and the flat image it leaves behind forgets what the ELF file knew.
> `54k` moves that job into the kernel, reading the file's own headers at
> `exec` time. Done outside class; not on the exam.

### For the exam { #exam }

*Not needed on Friday. On the final.*

**The process tree and `init`** · *Final.* Processes form a **process tree**
rooted at `init`, pid 1, which starts the shell. An exiting process's children
become **orphans**, reparented to `init`, whose `wait` loop reaps them. rv6 has
no `init`; the kernel frees leftovers when your `run` ends.
{ #exam-init }

**The stale parent pointer** · *Final.* rv6's parent record names a slot, and
slots recycle: reap a parent before its child, and the slot's next occupant
inherits a child it never forked ([Problem 2](#problem-2)). Record the pid, or
reparent at exit.
{ #exam-stale-parent }

**Why `fork` and `exec` are two calls** · *Final.* Between them, the child runs
the shell's code on its own file table. On Unix, `2>&1` is `close(2)`, then
`dup(1)`, which takes the lowest free descriptor, 2; `exec` keeps the table.
The child can also close descriptors or change its directory or limits. One
`spawn` needs each as a parameter, as `posix_spawn` does.
Copy-on-write keeps it cheap.
{ #exam-two-calls }

**The shell is unprivileged** · *Final.* `sh` is an ordinary user program; its
only door is `ecall`, where the kernel checks every request. So `cd` must be a
builtin: a child that changes directory changes only itself.
{ #exam-shell }

**Why `exec` needs no `sfence.vma`** · *Final.* `exec` changes only which table
the process will use; `satp` changes in the trampoline, between two
`sfence.vma`s.
{ #exam-sfence }

**Cumulative retrieval** · *Final.* Practice Set 3 Problem 12 needs
[`scause`](11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#44k-scause),
[the Sv39 split](07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#33k-address)
and [the trampoline's one address](12-cs326-2026-11-10-console-shell-and-user-mode.md#exam-top-pages).
{ #exam-retrieval }

**The long question** · *Final.* Tell [every layer](#53k-layers) aloud: the
component, the CSR or table, and what the alternative would cost (polling for
the key; an `exec` that destroys first).
{ #exam-long }

---

## Going deeper { #deeper }

*Optional. Nothing here is needed on Thursday or Friday, and nothing here is on
the exam.*

### Copied or shared: rv6 and Unix { #deeper-copied-shared }

rv6 copies memory eagerly: `copy_level()` (`vm.rs`) duplicates every user page
before the child runs. Unix copies it logically: both processes map the same
frames read-only, and a page is copied only when one of them writes it and
faults. That is **copy-on-write**, and it makes `fork` then `exec` copy almost
nothing.

Open files go the other way on Unix ([What the child gets](#51k-child)):
memory is copied because processes must stay isolated, and offsets are shared
because a redirected stream must stay coherent.

### The cost of a copy { #deeper-cost }

Before copy-on-write, BSD tried `vfork` (1979), which copies nothing: the
child borrows the parent's memory, parent suspended, until it calls `exec` or
exits, so a child that writes a variable writes the parent's.

Threads make `fork` worse. The child gets only the calling thread, but every
lock in whatever state it was in, so a lock another thread held stays locked
forever. POSIX therefore allows only async-signal-safe calls between `fork` and
`exec` in a threaded program.

### The status word { #deeper-status }

rv6 keeps an `isize` of exit status and copies four bytes of it to the parent.
Unix, Linux included, packs several answers into one `int`: bits 15–8 hold the
low 8 bits of the exit status, and the low 7 bits hold the signal that killed
the process, or 0; `WEXITSTATUS` and `WTERMSIG` unpack them. So on Linux
`exit(256)` reaches the parent as 0 and `exit(-1)` as 255, which is why shell
exit codes stay small.

### Waiting without polling { #deeper-sleep }

rv6's `wait` polls: a parent with a running child yields, rejoins the rotation,
and rescans all 64 slots whenever it is picked. That is correct on one
cooperative CPU, but a parent can spend many turns finding nothing. xv6 sleeps
instead: `wait` parks the parent on a channel, its own address, and `exit` calls
`wakeup` on its parent. Linux puts the parent on a wait queue and sends it
`SIGCHLD`. Either way, looking again becomes being told, and the unused
[`Sleeping` state](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-states)
is where such a parent would wait.

### Orphans on purpose { #deeper-orphans }

A **daemon**, a service with no terminal, wants no parent waiting on it, and
its classic launch orphans it deliberately. The launcher forks; the child forks
again and exits at once; the launcher reaps that child. The grandchild is now an
orphan, adopted by `init`, and nobody else's concern.

### One call instead of two { #deeper-spawn }

Fold `fork` and `exec` into one `spawn`, and every adjustment made in the
window becomes a parameter: descriptors, the working directory, credentials,
signal settings, the process group, resource limits, and on Linux namespaces
and cgroups. The window needs none, because it is not an interface but a place
to run code, so an adjustment invented later needs no new call.

`posix_spawn` (POSIX 2001) shows the cost. Beside the path and argv it takes a
list of file actions (`addopen`, `adddup2`, `addclose`) and an attributes
object: a small language for what the window would have done. The strongest
modern case against `fork` is Baumann and colleagues' "A `fork()` in the road"
(HotOS 2019).

### What a flat image costs { #deeper-flat }

Two of `oslings ship`'s refusals exist only because its output is flat. The
image must start at 0 and its entry must be 0, since a flat image has nowhere
to record either; `ulib`'s entry macro and the user linker script arrange both.
The loader maps every image page alike, `R X U`, so the only page a shipped
command can store to is its stack page ([Problem 4](#problem-4)). `54k` lifts
both limits by reading the ELF file instead.

### What rv6 still lacks { #deeper-missing }

`ls` at `rv6$` is still a kernel-shell command, and it cannot become a user
program yet: rv6 offers no system call to read, make, or change into a
directory. That is the price of a userland: every power the kernel keeps must
be handed out again, one system call at a time. Also missing are `dup`,
signals, copy-on-write, preemption, and a second hart.

### Practice problems { #problems }

#### Problem 1: Predict the output { #problem-1 }

This program runs alone on rv6's cooperative scheduler. Each `write` puts one
letter on fd 1:

```text
write "a"
p = fork()
if p == 0 { write "b"; q = fork(); if q == 0 { write "c"; exit(1) }; write "d"; exit(2) }
write "e"
wait(&s)
write "f"
exit(s)
```

(a) What prints, and with what status does the first process exit? (b) Which
process is never reaped by its own parent, and who frees it? (c) On Linux, with
preemption, which letters race, and can any letter follow `f`?

<details markdown="1">
<summary>Click to reveal solution</summary>

(a) **`aebdcf`**, status 2. Call the processes P, A (P's child) and B (A's
child), in slots 0, 1 and 2:

```text
turn   prints   what happens
P      a, e     forks A; wait finds no zombie, yields
A      b, d     forks B; exit(2): Zombie
B      c        exit(1): Zombie, its parent A already a zombie
P      f        wait reaps A (status 2); exit(2): the run is over
```

Round robin goes from slot 0 to 1 to 2 and back to 0, and nothing runs until
the one before it yields or exits.

(b) B: its parent A exited without waiting. rv6 frees it with every other
leftover when the first process finishes; on Unix, `init` would adopt and reap
it.

(c) `e` races with `b`, `c` and `d`, since the child may run first; `c` races
with `d`. And `c` can print after `f`, even after P exits: nothing waits for
B.

</details>

#### Problem 2: A child it never forked { #problem-2 }

Program P starts alone, as pid 1 in slot 0 of an empty table. A claim takes the
lowest `Unused` slot:

```text
P: a = fork()
   if a == 0 { if fork() == 0 { exit(3) }; exit(5) }        // A, and its child G
   s1 = wait(&x);  s2 = wait(&y)
   c = fork()
   if c == 0 { if wait(&z) < 0 { exit(0) }; exit(z + 10) }  // C
   wait(&w);  exit(w)
```

Give each process's slot and pid, what every `wait` returns, and P's exit
status on rv6. Then say what Unix does differently.

<details markdown="1">
<summary>Click to reveal solution</summary>

```text
process   slot   pid   parent pointer names
A         1      2     slot 0 (P)
G         2      3     slot 1 (A)
C         1      4     slot 0 (P)      C reuses A's slot
```

P forks A and yields in its first `wait`. A forks G and exits 5; G exits 3. P's
first `wait` reaps A: `s1 = 2`, `x = 5`, and slot 1 is `Unused`. G's parent
pointer still names slot 1, not P, and P has no other child, so `s2 = -1`.

P forks C into slot 1. C's `wait` finds G, a zombie whose parent pointer names
slot 1, which is now C's: it reaps G, `z = 3`, and C exits 13. P reaps C and
exits **13**.

On Unix, pid 1 is `init` itself, so let P be an ordinary process there. A's
exit hands G to `init`, which reaps it. `s1` and `s2` come out the same, but C
has no children, so its `wait` returns -1, C exits 0, and P exits **0**.

</details>

#### Problem 3: Redirect in the window { #problem-3 }

`notes.txt` holds `the cat sat\n`. Your shell learns `<`: for
`mycat < notes.txt`, its child points fd 0 at the file
[in the window](#exam-two-calls). (a) `mycat` is never told about the
redirect. Why does it still read the file? (b) A classmate moves the redirect
before the `fork`. `mycat` still prints the file. What goes wrong afterward, on
rv6 and on Unix?

<details markdown="1">
<summary>Click to reveal solution</summary>

(a) Open files survive `exec`, so `mycat` starts with fd 0 already naming
`notes.txt`. With no file argument it reads fd 0, whatever that is, and never
learns anything changed. The shell's fd 0, in its own table, is still the
console.

(b) Moved before the `fork`, the redirect changes the shell itself. Its fd 0 is
now `notes.txt`, so its next command line comes from the file, and the keyboard
is gone. On rv6 the shell's copy of the offset is still 0, so it reads
`the cat sat` as a command and tries to run `the`. Then every read returns 0,
which rv6's `sh` takes for a blank line, so it prints `$ ` forever. On Unix
`mycat` moved the shared offset to the end, so the shell reads end of file and
exits, as if you had pressed Ctrl-D. The window exists so that only the child changes.

</details>

#### Problem 4: Size a shipped command { #problem-4 }

`oslings ship` produces a 9,500-byte image for a command you ship as
`mytally`. (a) How many pages hold the image, and how many zero bytes end the
last one? (b) List every page the running process maps, with its permissions.
(c) You add `static mut HITS: u32 = 0;`, increment it on every match, and print
it at the end. The command now dies at its first match. Why, and what happens to
the `$ ` shell that ran it?

<details markdown="1">
<summary>Click to reveal solution</summary>

(a) Three pages, since 8,192 < 9,500 ≤ 12,288. The last holds
9,500 − 8,192 = 1,308 image bytes and 4,096 − 1,308 = 2,788 zeros, because
each page is zeroed before the copy. The image uses 14.5% of the 64 KiB budget.

(b)

| Virtual address | Contents | Flags |
|---|---|---|
| `0x0000`, `0x1000`, `0x2000` | the image | `R X U` |
| `0x1_0000` | the stack page; argv at its top, below `0x1_1000` | `R W U` |
| `0x3F_FFFF_E000` | the trapframe | `R W` |
| `0x3F_FFFF_F000` | the trampoline | `R X` |

Pages 3 through 15 stay unmapped, so running off the image faults instead of
reaching the stack.

(c) `HITS` starts at zero, so it lives in `.bss`, which `oslings ship` folded
into the image as zeros. Image pages have no `W`, so the first increment is a
store page fault, `scause` 15. A fault ends the whole run in rv6: the scheduler
frees every process but the root, the kernel shell then frees `sh`, and `rv6$`
prints `run: the program faulted`.

</details>

---

## Key terms { #terms }

| Term | Meaning | Where you use it |
|---|---|---|
| `fork` | Copy the caller; the parent gets the child's pid, the child 0 | `51k`, `52k` |
| Parent, child | The process that called `fork`, and its copy | `51k` |
| Zombie | An exited process holding its pid and status until reaped | `51k` |
| Reap | Collect a zombie's status and free its slot | `51k` |
| Cooperative scheduling | A process leaves the CPU only by yielding or exiting | `51k` |
| `exec` | Replace the caller's program and keep the process | `52k` |
| User shell | `sh`: a user program looping read, fork, exec, wait | `52k` |
| Builtin | A command the shell runs itself, because it changes the shell | `52k`, Final |
| Backend | One of `ulib`'s two implementations, chosen by the target | `53k` |
| Flat image | Bytes copied to address 0 and run from byte 0 | `53k`, `54k` |
| Orphan | A live process whose parent has exited | Final |
| `init` | Pid 1, root of the process tree: starts the shell, adopts and reaps orphans | Final |

## Further reading { #reading }

- [rv6 Architecture: Two shells](../guides/rv6-architecture.md#two-shells) and
  [the program table](../guides/rv6-architecture.md#the-program-table).
- [ulib and the Command Set: the rv6 backend](../guides/ulib-and-commands.md#the-rv6-backend-one-ecall-per-call),
  [`oslings ship`](../guides/ulib-and-commands.md#oslings-ship), and
  [the budget](../guides/ulib-and-commands.md#the-budget-and-what-a-command-actually-costs).
- [Key Concepts: the Unix process API](../guides/key-concepts.md#the-unix-process-api),
  from `fork` to `init`.
- [Cheatsheet: system calls](../guides/cheatsheet.md#system-calls) and
  [processes](../guides/cheatsheet.md#processes).
- [Exam Prep: how to prepare](../guides/exam-prep.md#how-to-prepare).
- Week 9: [process states](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#34k-states),
  [round robin](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#36k-round-robin),
  and [why `Zombie` exists](09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#deeper-zombie).
- [The xv6 book](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf),
  chapter 1, "Operating system interfaces", and the `sleep` and `wakeup`
  section of chapter 7.
- Arpaci-Dusseau and Arpaci-Dusseau,
  [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/),
  chapter 5, "Process API".
- A. Baumann, J. Appavoo, O. Krieger, T. Roscoe,
  [*A fork() in the road*](https://www.microsoft.com/en-us/research/publication/a-fork-in-the-road/),
  HotOS 2019.
- The Linux [`elf(5)`](https://man7.org/linux/man-pages/man5/elf.5.html) manual
  page, for `54k`.
