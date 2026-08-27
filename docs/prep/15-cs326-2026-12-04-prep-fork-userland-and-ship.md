# Prep: fork, the User Shell, and Your Commands — 51k · 52k · 53k

**Session:** Fri Dec 4, 1h30 · **Exercises:** `51k_fork_wait` · `52k_userland` · `53k_ship_your_commands` · **Prep time:** ~45 min · **Lecture:** [exec as a System Call, and Userland](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md) (and [exec, File Descriptors, and fork](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md) §4–§5)

## What you will build

The finish line. First the kernel runs a *tree* of processes: `fork` copies the caller, `exit` parks the child as a zombie holding its status, and `wait` reaps it. Then `exec` becomes a system call and the shell leaves the kernel: `run sh` at the `rv6$` prompt drops you into `$ `, an unprivileged program that reaches the kernel only through `ecall`. Finally `oslings ship` compiles the five commands you wrote in September for RISC-V, flattens each ELF, and embeds them as `myecho`, `mycat`, and so on.

Reference images (64 KiB budget):

| Command | Flat image |
|---|---|
| `echo` | 384 B |
| `cat` | 1,256 B |
| `wc` | 1,821 B |
| `head` | 2,713 B |
| `grep` | 2,854 B |

## Concepts you need

- **Zombies and reaping** — [exec as a System Call §1](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#1-ending-a-process-exit-and-why-a-corpse-has-a-job), [§2](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#2-wait-reaping-blocking-and-the-two-ways-to-fail)
- **`fork` returns twice** — [exec, File Descriptors, and fork §4](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#4-fork-the-call-that-returns-twice)
- **The process tree, and rv6's stand-in for `init`** — [exec as a System Call §3](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#3-the-process-tree-init-and-reparenting)
- **Why fork/exec and not `spawn`** — [exec as a System Call §5](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#5-why-fork-exec-and-not-spawn)
- **`exec` swaps the address space; the shell is just a program** — [exec as a System Call §6](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#6-exec-swapping-an-address-space-under-a-running-program), [§7](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#7-the-shell-is-just-a-program) · [rv6 Architecture § Two shells](../guides/rv6-architecture.md#two-shells)
- **One seam, two backends: an unedited command becomes `ecall`s** — [ulib and Commands § The rv6 backend](../guides/ulib-and-commands.md#the-rv6-backend-one-ecall-per-call) · [§ oslings ship](../guides/ulib-and-commands.md#oslings-ship)

## Read before class

| What | Time |
|---|---|
| exec as a System Call §1–§2 (zombies, reaping) | 8 min |
| exec, File Descriptors, and fork §4–§5 | 8 min |
| exec as a System Call §4–§7 (scheduler; the swap; the window; the shell as a program) | 20 min |
| ulib and Commands: The rv6 backend, oslings ship, The budget | 7 min |
| rv6 Architecture: Two shells | 2 min |

## Mental model

Redirection, `ls > out.txt`, is not a feature of `exec`; it is four ordinary calls in the window between `fork` and `exec`:

```text
pid = fork()             slot 1: sh, Running   slot 2: copy of sh, a0 = 0
child:  close(1)         fd 1 free in slot 2 only
        open("out.txt", O_CREATE|O_WRONLY)   lowest free fd -> 1
        exec("ls", argv) same pid and fds; new page table, epc, sp
        ...ls writes fd 1, never knowing; exit(0) -> Zombie
parent: wait(&status)    yields until slot 2 is a Zombie, then reaps it
```

`fork` copies the descriptor table and `exec` never touches it; that is the case against a single `spawn`.

## Check yourself

1. Two processes return from the same `fork` with identical memory. How does each know which it is? <details><summary>Answer</summary>Only the return register differs: the child's saved `a0` is 0, the parent's is the child's pid, and zero is never a valid pid.</details>
2. Your `echo` source has no `#[cfg]`, yet it runs on your laptop and on rv6. Where is the switch, and why is `println!` still forbidden? <details><summary>Answer</summary>Inside `ulib`: the backend is chosen by `target_os`, so on the kernel every call is one `ecall` with the number in `a7`. `println!` drags in `core::fmt`, roughly quintupling the largest image.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## Extra credit today

`54k_elf_loader` (+1.0). Every program so far is a flat image: byte 0 is the entry point, every page read-execute, no `.bss`. This exercise teaches the kernel to read the ELF the compiler already emits, taking entry point, segment permissions, and a zeroed `.bss` from its `PT_LOAD` headers.

## If you finish early

Work the lecture's [Practice Problems](../lectures/15-cs326-2026-12-03-exec-as-a-syscall-and-userland.md#practice-problems), then read xv6 book chapter 1 and the `sleep`/`wakeup` section of chapter 7, which rv6's polling `wait` omits. Tuesday Dec 8 is the payoff lecture and final review; the final is Dec 11–17.
