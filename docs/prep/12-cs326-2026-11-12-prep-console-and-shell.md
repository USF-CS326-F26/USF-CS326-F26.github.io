# Prep: The Console and the Kernel Shell — 45k · 46k

**Session:** Thu Nov 12, 1h45 · **Exercises:** `45k_console`, `46k_shell` · **Prep time:** ~55 min · **Lecture:** [Device Interrupts, the PLIC, and the Console](../lectures/11-cs326-2026-11-05-device-interrupts-the-plic-and-the-console.md) · [Shells, and the Reference Kernel](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md)

## What you will build

A keypress makes the UART raise source 10 and the PLIC deliver a supervisor external interrupt; your handler asks the PLIC which source fired, drains the waiting bytes into the ring buffer, and tells the PLIC it is done. Then the evaluate step of a kernel-mode REPL: split a line into words and send the first to one of four given commands (`pwd`, `ls`, `cd`, `mkdir`), or report it as not found. The tests check that a simulated interrupt lands its byte in the buffer and that `mkdir docs` then `ls` lists `docs`; then `cargo run` boots to a `rv6$` prompt.

## Concepts you need

- **Claim, service, complete; two ways a console dies** — [Device Interrupts §2.3](../lectures/11-cs326-2026-11-05-device-interrupts-the-plic-and-the-console.md#23-claim-service-complete) · [rv6 Architecture § Path 2](../guides/rv6-architecture.md#path-2-an-s-mode-device-interrupt)
- **Top half, bottom half, the lock-free ring, `wfi`** — [Device Interrupts §4.1](../lectures/11-cs326-2026-11-05-device-interrupts-the-plic-and-the-console.md#41-top-half-bottom-half), [§4.2](../lectures/11-cs326-2026-11-05-device-interrupts-the-plic-and-the-console.md#42-the-ring-buffer), [§4.3](../lectures/11-cs326-2026-11-05-device-interrupts-the-plic-and-the-console.md#43-blocking-and-why-wfi-is-not-a-busy-wait)
- **A shell is a REPL, and here also the line discipline** — [Shells §2.1](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#21-four-steps-and-nothing-else), [§2.3](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#23-line-discipline-who-owns-the-backspace) · [Device Interrupts §5.2](../lectures/11-cs326-2026-11-05-device-interrupts-the-plic-and-the-console.md#52-the-four-jobs)
- **Tokens are borrowed views; `split_whitespace` allocates nothing** — [Shells §3.1](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#31-words-not-characters)
- **Dispatch by `match`; output through the `Out` trait** — [Shells §4.1](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#41-why-a-table-not-a-chain-of-ifs), [§4.3](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#43-the-out-trait-where-the-output-goes) · [rv6 Architecture § Two shells](../guides/rv6-architecture.md#two-shells)
- **Reading to extend, not to rebuild** — [Shells §1.3](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#13-from-building-to-extending), [§6.1](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#61-name-it-precisely)

## Read before class

| What | Time |
|---|---|
| Device Interrupts §2.3, §3, §4, §6 (claim, service, complete; the ring; the whole path) | 25 min |
| Shells §2–§4 (REPL, tokens, dispatch, `Out`) | 20 min |
| Shells §1.3, §6.1 · rv6 Architecture: Path 2, Two shells | 10 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again. Midterm 2 is next Thursday, Nov 19, and covers processes through user mode.

## Extra credit today

`47k_file_commands` (+0.5): `touch`, `cat`, `echo TEXT > FILE`, `rm`, and `rmdir`. The redirect and `rmdir` are given as worked examples; the other three stitch together filesystem promises: name to inode number, bytes into a fixed buffer, `core::str::from_utf8`, unlink. See [Shells §1.3](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#13-from-building-to-extending) and [§3.4](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#34-why-echo-has-to-cheat).

## If you finish early

Work [Shells Practice Problem 5](../lectures/12-cs326-2026-11-12-shells-and-the-reference-kernel.md#practice-problems), the deadlock in the kernel shell; it comes back on Midterm 2. Then read chapter 5 of the xv6 book, "Interrupts and device drivers," or start Friday's prep page, [Prep: User Mode](12-cs326-2026-11-13-prep-user-mode.md).
