# Prep: wc and grep — 12c · 13c

**Session:** Fri Sep 25, 1h30 · **Exercises:** `12c_wc`, `13c_grep` · **Prep time:** ~30 min · **Lecture:** [Week 5 · Streams of Bytes](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md)

## What you will build

Two filters, each last session's copy loop plus one idea. `wc` streams input through a fixed buffer and prints lines, words, and bytes per file, with a `total` row for several; all it remembers between bytes is whether it is inside a word. `grep` reads lines through `ulib::Lines`, prints those in which a fixed byte pattern occurs, prefixes hits with `name:` only for two or more files, and reports through its exit status: 0 matched, 1 nothing matched, 2 something went wrong.

## Concepts you need

- **Streaming with O(1) state; a word is a change, not a byte** — [Week 5 · Streaming with O(1) state](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#12c-state), [State across a chunk boundary](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#exam-chunks)
- **Bytes, not characters; what counts as a line and a word** — [Week 5 · Bytes, `char`, and UTF-8](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#12c-bytes)
- **A line iterator that never allocates; `while let`** — [Week 5 · Lines without an allocator](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#13c-lines), [`while let`](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#13c-while-let) · [ulib guide: The complete API surface](../guides/ulib-and-commands.md#the-complete-api-surface)
- **Substring search: an empty needle, a needle with more bytes than the line, the last start** — [Week 5 · Where a search breaks](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#13c-search)
- **Exit status is output** — [Week 5 · An answer scripts can test](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#13c-status)

## Read before class

| What | Time |
|---|---|
| [Week 5 · Friday · `12c` wc](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#fri-12c), both sections | 5 min |
| [Week 5 · Friday · `13c` grep](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#fri-13c), all four sections | 7 min |
| [Week 5 · For the exam: State across a chunk boundary](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#exam-chunks). Not needed today; on Midterm 1 | 1 min |
| [Week 5 · Problem 2: Carry it across](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#problem-2) and [Problem 4: Unsigned arithmetic and ranges](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#problem-4), answers closed | 10 min |
| [ulib guide: The complete API surface](../guides/ulib-and-commands.md#the-complete-api-surface), the `Lines` paragraph | 2 min |

## Mental model

Count the runs of digits in a byte stream, remembering one bit:

```rust
// "a1b22c333" -> 3 runs
let mut runs = 0;
let mut in_run = false;      // the one bit carried across bytes and reads
for &b in chunk {
    match (b.is_ascii_digit(), in_run) {
        (true, false) => { runs += 1; in_run = true; }  // a run begins: count it
        (true, true) => {}                              // inside a counted run
        (false, _) => in_run = false,                   // run over
    }
}
```

Split the input into `a1b2` and `2c333`: still 3, because `in_run` summarizes every byte already seen, so chunk boundaries are invisible, and end of input needs no special case since a run is counted when it starts. The UART driver and shell tokenizer you write later are this machine with a different predicate.

## Check yourself

1. <code style="white-space: pre">printf 'a  b' | wc</code> prints what, and why not 1 line? <details><summary>Answer</summary>`0 2 4`. A line is a newline byte and there is none; two spaces are one separator; `b` was counted when it began.</details>
2. `grep` prints nothing and every file opened. Exit status, and why not 0? <details><summary>Answer</summary>1, a successful run answering no. Returning 0 either way would break `&&` chains; 2 means something went wrong.</details>
3. Searching for `x` in `abcx`, which start positions must you try? Now search for `abcdefgh` in `abc`. <details><summary>Answer</summary>0 through 3, and 3 is 4 − 1, so the range is `0..=n`. Then 3 − 8 on `usize` panics: rule out a longer pattern before subtracting, and the empty pattern before that.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## Extra credit today

`14c_head` (+0.5) prints the first lines of its input, 10 unless `-n COUNT` asks for another number, and is judged by how little of the input it reads. See [Week 5 · Extra credit · `14c`](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#ec-14c) and the [extra-credit page](../assignments/extra-credit.md#14c).

## If you finish early

Work [Week 5 · Problem 3: Does it need a flush?](../lectures/05-cs326-2026-09-22-cat-wc-and-grep.md#problem-3) on paper (Midterm 1 material). Rustlings [`iterators`, `lifetimes`, `strings`](https://github.com/rust-lang/rustlings) and 100 Exercises [chapter 6, Ticket Management](https://rust-exercises.com/100-exercises/) cover the borrow behind `next_line`. Next Thursday needs QEMU installed; check the [setup page](../assignments/setup.md) now, then start the next prep page, [Prep: The Assembly Bridge](06-cs326-2026-10-01-prep-asm-bridge.md).
