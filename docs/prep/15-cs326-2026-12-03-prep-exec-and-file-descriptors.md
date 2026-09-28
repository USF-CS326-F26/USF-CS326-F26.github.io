# Prep: exec and File Descriptors — 49k · 50k

**Session:** Thu Dec 3, 1h45 · **Exercises:** `49k_exec` · `50k_file_descriptors` · **Prep time:** ~30 min · **Lecture:** [Week 15 · exec and File Descriptors](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md)

**Back from Thanksgiving.** This session's lecture was Tue Nov 24, before Thanksgiving: reread [Week 15 · Essentials](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#essentials) before class. The Tue Dec 1 lecture also walks this page.

## What you will build

Two focused pieces over given plumbing. For `exec`: a program named at the prompt starts in a fresh address space of its own, at instruction 0, with `a0 = argc` and `a1 = argv` pointing at its arguments on its stack. For descriptors: a per-process table of open files where the fd *is* the index, so `open` turns a name into a small integer, `read` moves bytes through that descriptor's cursor and advances it, and `close` frees the slot.

## Concepts you need

- **`exec` replaces the caller; a failed `exec` leaves it running** — [Week 15 · After 48k: the door, and the two calls](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-two-calls), [Starting it, and failing cleanly](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-start)
- **Programs by name: a flat binary, position-independent, run at address 0** — [Week 15 · Programs by name: flat binaries](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-flat) · [rv6 Architecture: The program table](../guides/rv6-architecture.md#the-program-table)
- **Image at 0, stack fixed above, `PTE_U` on user pages, zero before a partial copy** — [Week 15 · Loading more than a page, and where it lands](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-load) · [rv6 Architecture: Address spaces](../guides/rv6-architecture.md#address-spaces)
- **`argv`: strings first, NULL-terminated array of user addresses below, `sp` 16-byte aligned, written with `copyout`** — [Week 15 · argc and argv, on the new stack](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-argv)
- **An fd is an unforgeable capability: a kernel-owned table index, revalidated on every call** — [Week 15 · A descriptor is a small integer](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-fd), [The per-process file table](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-table) · [rv6 Architecture: The system call table](../guides/rv6-architecture.md#the-system-call-table)
- **The offset lives with the open file; `read` returns a count and advances it; 0 means end of file** — [Week 15 · The offset makes a descriptor stateful](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-offset)
- **`open` flags are bits in one integer; `O_RDONLY` is 0; a path ends at its NUL** — [Week 15 · `open` and its flags](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-open)
- **0, 1, 2 are a convention; lowest free slot is a guarantee; the kernel, not the caller, branches on console versus inode** — [Week 15 · A descriptor is a small integer](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-fd), [The per-process file table](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-table), [One read and write path](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-uniform)

## Read before class

| What | Time |
|---|---|
| [Week 15 · This week](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#this-week), then [Thursday · `49k` exec](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#thu-49k) through [Programs by name: flat binaries](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-flat) | 3 min |
| [Week 15 · Loading more than a page, and where it lands](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-load), [argc and argv, on the new stack](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-argv) and [Starting it, and failing cleanly](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#49k-start) | 6 min |
| [Week 15 · Thursday · `50k` File descriptors](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#thu-50k) through [The offset makes a descriptor stateful](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-offset) | 4 min |
| [Week 15 · `open` and its flags](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-open) and [One read and write path](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#50k-uniform) | 3 min |
| [Week 15 · For the exam](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#exam). Not needed today; on the Final | 2 min |
| [rv6 Architecture: Address spaces](../guides/rv6-architecture.md#address-spaces), the user address space and its constants | 3 min |
| [rv6 Architecture: The system call table](../guides/rv6-architecture.md#the-system-call-table) | 2 min |

## Mental model

A process with only 0, 1, 2 open reads a 12-byte file through an 8-byte buffer:

```text
open("notes.txt", O_RDONLY)  -> 3     lowest free slot; cursor = 0
read(3, buf, 8)  -> 8  "hello fi"     cursor 0 -> 8
read(3, buf, 8)  -> 4  "les\n"        cursor 8 -> 12
read(3, buf, 8)  -> 0                 cursor == size: end of file
close(3)                              slot 3 free again
open("notes.txt", O_RDONLY)  -> 3     new open, cursor back at 0
```

The cursor is the only state the kernel keeps between calls; the returned count says how far it moved. `cat` stops when `read` returns 0, which never comes if the cursor never advances. And `close(1)` then `open` hands out 1: that is redirection.

## Check yourself

1. `run wc -l notes.txt`. What are `a0` and `a1` at the first instruction, and what is at `argv[3]`? <details><summary>Answer</summary>`a0 = 3` (the name counts). `a1` equals `sp`: the 16-byte-aligned user address of the pointer array in the stack page. `argv[3]` is NULL, the sentinel C needs since it carries no lengths.</details>
2. A program never given fd 5 puts 5 in `a0` and calls `read`. What comes back, and why? <details><summary>Answer</summary>-1. Slot 5 is empty, so the lookup refuses it. The integer indexes a kernel-owned table; authority is granted by `open` or inherited, never computed.</details>
3. A 5,000-byte program loads onto two pages. Why zero the second page before copying the last 904 bytes? <details><summary>Answer</summary>The page holds whatever its previous owner left, possibly kernel data. Zeroing makes the tail predictable, as a real loader does for `.bss`, and keeps stale kernel bytes out of user mode.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 15 · Problem 1: Build the argv block](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#problem-1), [Problem 4: Two designs, one fork](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#problem-4) and [Problem 5: Try to forge authority](../lectures/15-cs326-2026-11-24-exec-and-file-descriptors.md#problem-5) on paper, then read xv6 book chapter 1 and chapter 3's "Code: exec" section. Then start Friday's prep page, [Prep: fork, Userland, and Ship](15-cs326-2026-12-04-prep-fork-userland-and-ship.md).
