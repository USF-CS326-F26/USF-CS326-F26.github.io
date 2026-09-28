# Prep: The Console and the Kernel Shell — 45k · 46k

**Session:** Thu Nov 12, 1h45 · **Exercises:** `45k_console`, `46k_shell` · **Prep time:** ~20 min · **Lecture:** [Week 12 · The Console, the Shell, and User Mode](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md)

## What you will build

A keypress makes the UART raise source 10 and the PLIC deliver a supervisor external interrupt; your handler asks the PLIC which source fired, drains the waiting bytes into the ring buffer, and tells the PLIC it is done. Then the evaluate step of a kernel-mode REPL: split a line into words and send the first to one of four given commands (`pwd`, `ls`, `cd`, `mkdir`), or report it as not found. The tests check that a simulated interrupt lands its byte in the buffer and that `mkdir docs` then `ls` lists `docs`; then `cargo run` boots to a `rv6$` prompt.

## Concepts you need

- **Claim, service, complete; two ways a console dies** — [Week 12 · Claim, service, complete](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#45k-claim) · [rv6 Architecture: Path 2, an S-mode device interrupt](../guides/rv6-architecture.md#path-2-an-s-mode-device-interrupt)
- **Top half, bottom half, the lock-free ring, `wfi`** — [Week 12 · A ring between two worlds](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#45k-ring)
- **A shell is a REPL, and here also the line discipline** — [Week 12 · A loop, and words](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#46k-repl)
- **Tokens are borrowed views; `split_whitespace` allocates nothing** — [Week 12 · A loop, and words](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#46k-repl)
- **Dispatch by `match`; output through the `Out` trait** — [Week 12 · One match, and `&mut dyn Out`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#46k-dispatch) · [rv6 Architecture: Two shells](../guides/rv6-architecture.md#two-shells)
- **Reading to extend, not to rebuild** — [Week 12 · Thursday · `46k` The kernel shell](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#thu-46k)

## Read before class

| What | Time |
|---|---|
| [Week 12 · This week](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#this-week), then [Thursday · `45k` The console](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#thu-45k) through [Claim, service, complete](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#45k-claim) | 4 min |
| [Week 12 · A ring between two worlds](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#45k-ring), with its four-slot trace | 3 min |
| [Week 12 · Thursday · `46k` The kernel shell](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#thu-46k), both sections and the [`47k` extra-credit box](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#ec-47k) | 3 min |
| [Week 12 · For the exam: The PLIC's four registers](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#exam-plic). Not needed today; on Midterm 2 | 1 min |
| [rv6 Architecture: Path 2, an S-mode device interrupt](../guides/rv6-architecture.md#path-2-an-s-mode-device-interrupt) and [Two shells](../guides/rv6-architecture.md#two-shells) | 4 min |

## Mental model

Type `ls` and Enter into a four-byte ring. The counters only grow; `% 4` picks the slot:

```text
                                BUF      HEAD  TAIL
'l', 's' -> two handler pushes  [ls..]    0     2    in the trap, SIE off
shell getc -> 'l', echo it      [ls..]    1     2    normal priority
shell getc -> 's', echo it      [ls..]    2     2    empty: HEAD == TAIL
shell getc -> wfi               [ls..]    2     2    halted, zero cycles
Enter -> handler push           [ls\r.]   2     3    wfi returns; "ls" is a line
```

The handler writes only `BUF` and `TAIL`, the reader only `HEAD`; a stale read errs safely, so one hart needs no lock, and a lock in the handler would deadlock with whatever it interrupted. The ring holds no echo, no erasing, no line: those are the shell's job, off the interrupt path.

## Check yourself

1. Your handler buffers the byte but never writes the source number back to the PLIC. What do you see? <details><summary>Answer</summary>The first keypress works; later ones vanish. The PLIC still considers source 10 claimed and never delivers it again; nothing panics.</details>
2. The opposite: it completes without reading the UART. Why is that different? <details><summary>Answer</summary>An interrupt storm: the byte still sits in the receive register, the level-triggered line stays high, and the PLIC re-raises it the moment the gateway re-arms; the kernel spins at 100% CPU.</details>
3. The tokenizer yields `&str` slices into the line buffer. What stops the REPL from clearing the line too early? <details><summary>Answer</summary>The tokens borrow the line, so the borrow checker refuses `line.clear()` until the evaluate step returns.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again. Midterm 2 is next Thursday, Nov 19, and covers processes through user mode.

## Extra credit today

`47k_file_commands` (+0.5): `touch`, `cat`, `echo TEXT > FILE`, `rm`, and `rmdir`. The redirect and `rmdir` are given as worked examples; the other three stitch together filesystem promises, and each decides which of the filesystem's facts count as errors. See [Week 12 · Extra credit · `47k`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#ec-47k) and [Why the call is `unlink`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#deeper-unlink).

## If you finish early

Work [Week 12 · Problem 1: The PLIC for a second hart](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#problem-1) and [Problem 2: Predict the screen and the line](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#problem-2) on paper; the PLIC's registers come back on Midterm 2. Then read chapter 5 of the xv6 book, "Interrupts and device drivers," or start Friday's prep page, [Prep: User Mode](12-cs326-2026-11-13-prep-user-mode.md).
