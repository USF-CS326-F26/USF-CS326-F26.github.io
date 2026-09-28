# Prep: An In-Memory Filesystem — 40k

**Session:** Thu Nov 5, 1h45 · **Exercises:** `40k_filesystem` · **Prep time:** ~20 min · **Lecture:** [Week 11 · Files, Boot Order, and Traps](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md)

## What you will build

The heart of a Unix filesystem, in RAM, behind one spinlock: a fixed table of inodes, each holding a kind, a size, and either file bytes or directory entries, never a name. You finish the two operations everything else rests on: asking a directory which inode a name points at, and putting bytes into a file. Creating an entry is given; read it, since it leans on your lookup to refuse duplicates. Every call returns a `Result` whose error variant says which fact went wrong.

## Concepts you need

- **A file is not its name: contents in the inode, names in directories** — [Week 11 · A file is not its name](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-inodes)
- **An inode number is an index; root is 1; the lowest free slot is reused** — [Week 11 · A file is not its name](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-inodes)
- **A directory is an inode with structure: a linear scan, kind check first** — [Week 11 · A file is not its name](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-inodes), [Path resolution by hand](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-paths)
- **Path resolution: one lookup per component; the failing step picks the error** — [Week 11 · Path resolution by hand](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-paths)
- **Errors as values: `Result`, `?`, matching one variant** — [Week 11 · Errors as values, behind one lock](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-errors) · [Rust for Systems: `Result`, `?`, error enums](../guides/rust-for-systems.md#7-result-error-enums)
- **One global lock around the filesystem** — [Week 11 · Errors as values, behind one lock](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-errors) · [rv6 Architecture: Locks, and the ordering rules](../guides/rv6-architecture.md#locks-and-the-ordering-rules)
- **What rv6 defers: persistence, bitmaps, buffer cache, log** — [Week 11 · What rv6's filesystem trades away](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#deeper-fs), in Going deeper (optional)

## Read before class

| What | Time |
|---|---|
| [Week 11 · This week](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#this-week), then [Thursday · `40k` Files and directories](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#thu-40k), all three sections | 6 min |
| [Week 11 · For the exam](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam): [Devices](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam-devices) and [Hard links and link counts](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam-links). Not needed today; on Midterm 2 | 2 min |
| [Rust for Systems: `Result`, `?`, error enums](../guides/rust-for-systems.md#7-result-error-enums), through "The `?` operator" (a refresher) | 4 min |
| [rv6 Architecture: Locks, and the ordering rules](../guides/rv6-architecture.md#locks-and-the-ordering-rules), the opening and the table | 1 min |

## Mental model

Two tables; every operation touches exactly one:

```text
directory inode 1 (root)       inode table
  slot 0  "notes" -> 2         2: File  size 5  "hello"
  slot 1  "todo"  -> 2         3: Dir   entries [ "x" -> 4 ]
  slot 2  "sub"   -> 3         4: File  size 0

lookup(1, "todo")   scan inode 1's slots -> Ok(2)          second name, same file
lookup(3, "todo")   scan inode 3's slots -> NotFound
lookup(2, "x")      inode 2 is a File    -> NotADirectory  before any scan
rename notes->log   rewrite slot 0
```

Inode 2 never changes when it gains or loses a name: names belong to the directory, not the file. That split is why `mv` costs the same at any size, why two look-alike failures are two variants, and why the kind check precedes the scan.

## Check yourself

1. Why does an inode have no name field, and what does that buy? <details><summary>Answer</summary>Names are directory entries; two entries may hold one inode number, so a file can have several names for free. Rename rewrites an entry; unlink removes a name, not the file.</details>
2. Root holds `sub` → 3 (a directory) and `log` → 4 (a file). Resolving `/sub/x` and `/log/x` both fail. Which variant does each produce? <details><summary>Answer</summary>`/sub/x` scans directory 3 and finds nothing: `NotFound`. `/log/x` asks inode 4, a file, for an entry: `NotADirectory`.</details>
3. A helper returns `Result<usize, FsError>`. What does `?` do, and when is `match` better? <details><summary>Answer</summary>`?` returns any `Err` from the enclosing function and unwraps `Ok`. `match` wins when one error is good news: in a create, `NotFound` means the name is free.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## Extra credit today

`41k_devices` (+0.5) turns the blind-write UART into a polled driver: read the NS16550A line-status register, spin on "room to transmit" before sending, and return `Option` when no byte is waiting. The test flips the chip's loopback bit, so what you send returns through your receive path. Read [Week 11 · For the exam: Devices](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#exam-devices) and [The UART up close](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#deeper-uart) first.

## If you finish early

Work [Week 11 · Problem 1: Resolve, create, rename](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#problem-1) on paper, then read chapter 8, "File system," of the xv6 book, or start [Friday's prep page](11-cs326-2026-11-06-prep-boot-to-life-traps-and-interrupts.md), where this kernel boots for real.
