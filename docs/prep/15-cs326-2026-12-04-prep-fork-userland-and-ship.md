# Prep: fork, the User Shell, and Your Commands — 51k · 52k · 53k

**Session:** Fri Dec 4, 1h30 · **Exercises:** `51k_fork_wait` · `52k_userland` · `53k_ship_your_commands` · **Prep time:** ~35 min · **Lecture:** [Week 15 · fork, wait, and the User Shell](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md)

## What you will build

The finish line. First the kernel runs a *tree* of processes: `fork` copies the caller, `exit` parks the child as a zombie holding its status, and `wait` reaps it. Then `exec` becomes a system call and the shell leaves the kernel: `run sh` at the `rv6$` prompt drops you into `$ `, an unprivileged program that reaches the kernel only through `ecall`. Finally `oslings ship` compiles the commands you wrote in September for RISC-V, flattens each ELF, and embeds them as `myecho`, `mycat`, and so on.

Reference images (64 KiB budget):

| Command | Flat image |
|---|---|
| `echo` | 384 B |
| `cat` | 1,256 B |
| `wc` | 1,821 B |
| `head` | 2,713 B |
| `grep` | 2,854 B |

## Concepts you need

- **`fork` returns twice; what the child gets** — [Week 15 · One call, two returns](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-fork), [What the child gets](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-child)
- **Zombies and reaping** — [Week 15 · `exit`, the zombie, and `wait`](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-zombie)
- **The scheduler finally has two processes** — [Week 15 · The scheduler finally has work](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-scheduler)
- **`exec` swaps the address space; only a failure returns** — [Week 15 · Replace the program, keep the process](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#52k-exec), [`exec` does not return on success](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#52k-no-return)
- **The shell is just a program** — [Week 15 · The shell leaves the kernel](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#52k-shell) · [rv6 Architecture: Two shells](../guides/rv6-architecture.md#two-shells)
- **One seam, two backends: an unedited command becomes `ecall`s** — [Week 15 · One source, two backends](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#53k-backends), [What `oslings ship` does](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#53k-ship) · [ulib and Commands: The rv6 backend](../guides/ulib-and-commands.md#the-rv6-backend-one-ecall-per-call), [`oslings ship`](../guides/ulib-and-commands.md#oslings-ship)
- **The final's long question, one layer per line** — [Week 15 · The long question, one layer per line](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#53k-layers)
- **The process tree, and rv6's stand-in for `init`** — [Week 15 · For the exam: The process tree and `init`](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#exam-init)
- **Why fork/exec and not `spawn`** — [Week 15 · For the exam: Why `fork` and `exec` are two calls](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#exam-two-calls)

## Read before class

| What | Time |
|---|---|
| [Week 15 · This week](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#this-week), then [Friday · `51k` `fork`, `exit`, and `wait`](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#fri-51k) through [What the child gets](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-child) | 5 min |
| [Week 15 · `exit`, the zombie, and `wait`](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-zombie) and [The scheduler finally has work](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#51k-scheduler) | 3 min |
| [Week 15 · Friday · `52k` `exec` as a system call](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#fri-52k), all three sections | 4 min |
| [Week 15 · Friday · `53k` Ship your commands](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#fri-53k) through [What `oslings ship` does](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#53k-ship) | 3 min |
| [Week 15 · The long question, one layer per line](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#53k-layers), with the `54k` extra-credit box | 3 min |
| [Week 15 · For the exam](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#exam). Not needed today; on the Final | 3 min |
| [ulib and Commands: The rv6 backend](../guides/ulib-and-commands.md#the-rv6-backend-one-ecall-per-call), [`oslings ship`](../guides/ulib-and-commands.md#oslings-ship) and [The budget](../guides/ulib-and-commands.md#the-budget-and-what-a-command-actually-costs) | 7 min |
| [rv6 Architecture: Two shells](../guides/rv6-architecture.md#two-shells) | 1 min |

## Mental model

Redirection, `ls > out.txt`, is not a feature of `exec`; it is two ordinary calls in the window between `fork` and `exec`:

```text
pid = fork()             slot 1: sh, Running   slot 2: copy of sh, a0 = 0
child:  close(1)         fd 1 free in slot 2 only
        open("out.txt", O_CREATE|O_WRONLY|O_TRUNC)   lowest free fd -> 1
        exec("ls", argv) same pid and fds; new page table, epc, sp
        ...ls writes fd 1, never knowing; exit(0) -> Zombie
parent: wait(&status)    yields until slot 2 is a Zombie, then reaps it
```

`fork` copies the descriptor table and `exec` never touches it; that is the case against a single `spawn`.

## Check yourself

1. Two processes return from the same `fork` with identical memory. How does each know which it is? <details><summary>Answer</summary>Only the return register differs: the child's saved `a0` is 0, the parent's is the child's pid, and zero is never a valid pid.</details>
2. Your `echo` source has no `#[cfg]`, yet it runs on your laptop and on rv6. Where is the switch, and why is `println!` still forbidden? <details><summary>Answer</summary>Inside `ulib`: the backend is chosen by `target_os`, so on the kernel every call is one `ecall` with the number in `a7`. `println!` comes from `std`, so it does not exist on the `no_std` kernel target; even a `core::fmt` stand-in would roughly quintuple the largest image.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## Extra credit today

`54k_elf_loader` (+1.0). Every program so far is a flat image: byte 0 is the entry point, every page read-execute, no `.bss`. This exercise teaches the kernel to read the ELF the compiler already emits, taking entry point, segment permissions, and a zeroed `.bss` from its `PT_LOAD` headers.

## If you finish early

Work [Week 15 · Practice problems](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#problems) on paper, starting with [Problem 1: Predict the output](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#problem-1) and [Problem 4: Size a shipped command](../lectures/15-cs326-2026-12-01-fork-wait-and-the-user-shell.md#problem-4), then read xv6 book chapter 1 and the `sleep`/`wakeup` section of chapter 7, which rv6's polling `wait` omits. Tuesday Dec 8 is the **final exam**, in class, the last day of the term — there is no exam during finals week. Practice Set 3 goes out today and its solutions go up Monday Dec 7, so attempt it on paper first.
