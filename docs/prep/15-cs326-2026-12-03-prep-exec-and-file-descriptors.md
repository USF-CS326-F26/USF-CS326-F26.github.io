# Prep: exec and File Descriptors — 49k · 50k

**Session:** Thu Dec 3, 1h45 · **Exercises:** `49k_exec` · `50k_file_descriptors` · **Prep time:** ~45 min · **Lecture:** [`exec`, File Descriptors, and `fork`](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md)

## What you will build

Two focused pieces over given plumbing. For `exec`: find a program by name, build it a fresh address space, copy its image in page by page, give it a stack, lay `argv` out with the given helper, and set the four trapframe fields so it starts at instruction 0 with `a0 = argc` and `a1 = argv`. For descriptors: a per-process table of open files where the fd *is* the index, so `open` turns a name into a small integer, `read` moves bytes through that descriptor's cursor and advances it, and `close` frees the slot.

## Concepts you need

- **`exec` replaces the caller; a failed `exec` leaves it running** — [L15 §2](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#why-replace-instead-of-create) · [L15 § Failure atomicity](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#failure-atomicity-build-first-destroy-second)
- **`exec`'s four products; image at 0, stack fixed above, `PTE_U` on user pages, zero before a partial copy, `fence.i` after writing code** — [L15 § The world it builds](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#the-world-it-builds) · [rv6 Architecture § Address spaces](../guides/rv6-architecture.md#address-spaces)
- **`argv`: strings first, NULL-terminated array of user addresses below, `sp` 16-byte aligned, written with `copyout`** — [L15 § argv on the stack](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#argv-on-the-stack)
- **An fd is an unforgeable capability: a kernel-owned table index, revalidated on every call** — [L15 §3](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#the-fd-as-an-unforgeable-capability) · [rv6 Architecture § The system call table](../guides/rv6-architecture.md#the-system-call-table)
- **The offset lives with the open file; `read` returns a count and advances it; 0 means end of file** — [L15 § Two tables](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#two-tables-and-where-the-offset-lives) · [L14 § cat](../lectures/14-cs326-2026-11-24-file-commands-over-a-filesystem-api.md#cat-is-lookup-read-decode-print)
- **0, 1, 2 are a convention; lowest free slot is a guarantee; the kernel, not the caller, branches on console versus inode** — [L15 § 0, 1, 2](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#0-1-2-a-convention-not-a-rule) · [L15 § Everything is a file](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#what-everything-is-a-file-buys)

## Read before class

| What | Time |
|---|---|
| L15 §2 `exec`: Building a World | 15 min |
| L15 §3 File Descriptors | 15 min |
| L14 §4, the `cat` subsection | 5 min |
| rv6 Architecture: Address spaces; The system call table | 10 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Thursday 11:59 pm** and submit again.

## If you finish early

Work [Practice Problems](../lectures/15-cs326-2026-12-01-exec-file-descriptors-and-fork.md#practice-problems) 1, 2, and 6, then read xv6 book chapter 1 and chapter 3's "Code: exec" section. Then start Friday's prep page, [Prep: fork, Userland, and Ship](15-cs326-2026-12-04-prep-fork-userland-and-ship.md).
