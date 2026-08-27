# Prep: wc and grep — 12c · 13c

**Session:** Fri Sep 25, 1h30 · **Exercises:** `12c_wc` · `13c_grep` · **Prep time:** ~30 min · **Lecture:** [Buffers, Bytes, and Line-Oriented I/O](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md)

## What you will build

Two filters, each last session's copy loop plus one idea. `wc` streams input through a fixed buffer and prints lines, words, and bytes per file, with a `total` row for several; all it remembers between bytes is whether it is inside a word. `grep` reads lines through `ulib::Lines`, prints those in which a fixed byte pattern occurs, prefixes hits with `name:` only for two or more files, and reports through its exit status: 0 matched, 1 nothing matched, 2 something went wrong.

## Concepts you need

- **Streaming with O(1) state** — count a word at the whitespace-to-word transition; one `bool` and three counters suffice at any file size. [Buffers & Bytes §7](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#7-five-commands-one-idea)
- **Bytes, not characters** — a line is a `\n` byte, a word is a run of non-whitespace bytes, `é` counts as 2; arguments and file content are `&[u8]`. [Buffers & Bytes §5](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#5-bytes-char-and-utf-8)
- **A line iterator that never allocates** — `Lines::new(fd, &mut buf)` borrows your buffer; `next_line()` returns each line without its `\n`. [Buffers & Bytes §6](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#6-lines-without-an-allocator) · [ulib and Commands §API surface](../guides/ulib-and-commands.md#the-complete-api-surface)
- **Three substring-search edge cases** — the empty pattern occurs everywhere; a longer one cannot, and subtracting `usize` lengths first panics; the last legal start is haystack length minus pattern length, so the range is inclusive. [Buffers & Bytes §7](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#7-five-commands-one-idea)
- **Exit status is output** — "nothing matched" is a successful no, which makes `grep -q x f && …` work; the `i32` your program returns is that status. [Buffers & Bytes §7](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#7-five-commands-one-idea)

## Read before class

| What | Time |
|---|---|
| Buffers & Bytes §5–§7 | 15 min |
| [Practice Problem 3](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#problem-3-the-word-counter-across-a-chunk-boundary) and [Problem 4](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#practice-problems), answers closed | 10 min |
| ulib and Commands: API surface · Portability rules | 5 min |

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

1. `printf 'a  b' | wc` prints what, and why not 1 line? <details><summary>Answer</summary>`0 2 4`. A line is a newline byte and there is none; two spaces are one separator; `b` was counted when it began.</details>
2. `grep` prints nothing and every file opened. Exit status, and why not 0? <details><summary>Answer</summary>1, a successful run answering no. Returning 0 either way would break `&&` chains; 2 means something went wrong.</details>
3. Searching for `x` in `abcx`, which start positions must you try? Now search for `abcdefgh` in `abc`. <details><summary>Answer</summary>0 through 3, and 3 is 4 − 1, so the range is `0..=n`. Then 3 − 8 on `usize` panics: rule out a longer pattern before subtracting, and the empty pattern before that.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## Extra credit today

`14c_head` (+0.5): parse `-n COUNT` by hand with `checked_mul`, print lines through `Lines`, and **stop reading** once you have enough; `next_line` reads lazily, so the stopping belongs in the loop bound. [Buffers & Bytes §7](../lectures/04-cs326-2026-09-15-buffers-bytes-and-line-oriented-io.md#7-five-commands-one-idea)

## If you finish early

Rustlings [`iterators`, `lifetimes`, `strings`](https://github.com/rust-lang/rustlings) and 100 Exercises [chapter 6, Ticket Management](https://rust-exercises.com/100-exercises/) cover the borrow behind `next_line`. Next Thursday needs QEMU installed; check the [setup page](../assignments/setup.md) now.
