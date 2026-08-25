# Prep: An In-Memory Filesystem — 40k

**Session:** Thu Nov 5, 1h45 · **Exercises:** `40k_filesystem` · **Prep time:** ~40 min · **Lecture:** [Filesystems, Devices, and the Boot Sequence](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md)

## What you will build

The heart of a Unix filesystem, in RAM, behind one spinlock: a fixed table of inodes, each holding a kind, a size, and either file bytes or directory entries, never a name. You finish the two operations everything else rests on: asking a directory which inode a name points at, and putting bytes into a file. Creating an entry is given; read it, since it leans on your lookup to refuse duplicates. Every call returns a `Result` whose error variant says which fact went wrong.

## Concepts you need

- **A file is not its name: contents in the inode, names in directories** — [Filesystems and Devices §1](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#1-the-file-and-its-name)
- **An inode number is an index; root is 1; the lowest free slot is reused** — [Filesystems and Devices § Key Concepts](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#key-concepts)
- **A directory is an inode with structure: a linear scan, kind check first** — [Filesystems and Devices §2](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#2-directories-are-files-with-structure)
- **Path resolution: one lookup per component; the failing step picks the error** — [§ Problem 3](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#problem-3-resolve-four-paths-by-hand)
- **Errors as values: `Result`, `?`, matching one variant** — [Traits, Generics, and the ulib Facade §6.1](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#61-option-for-absence-result-for-failure), [§6.3](../lectures/03-cs326-2026-09-10-traits-generics-and-the-ulib-facade.md#63-and-the-desugaring-you-should-know)
- **One global lock around the filesystem** — [rv6 Architecture § Locks, and the ordering rules](../guides/rv6-architecture.md#locks-and-the-ordering-rules)
- **What rv6 defers: persistence, bitmaps, buffer cache, log** — [Filesystems and Devices §4](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#4-what-rv6s-filesystem-trades-away)

## Read before class

| What | Time |
|---|---|
| Filesystems and Devices §1–§4 | 25 min |
| Traits, Generics, and the ulib Facade §6.1–§6.3 (`Result` and `?` refresher) | 5 min |
| rv6 Architecture: Locks, and the ordering rules | 3 min |
| Filesystems and Devices Practice Problem 3, on paper | 7 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Thursday 11:59 pm** and submit again.

## Extra credit today

`41k_devices` (+0.5) turns the blind-write UART into a polled driver: read the NS16550A line-status register, spin on "room to transmit" before sending, and return `Option` when no byte is waiting. The test flips the chip's loopback bit, so what you send returns through your receive path. Read [Filesystems and Devices §5–§6](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#5-devices-the-register-file-is-the-interface) first.

## If you finish early

Work the lecture's [Practice Problems 1 and 2](../lectures/10-cs326-2026-10-29-filesystems-devices-and-boot-to-life.md#practice-problems) on paper, then read chapter 8, "File system," of the xv6 book, or start [Friday's prep page](11-cs326-2026-11-06-prep-boot-to-life-traps-and-interrupts.md), where this kernel boots for real.
