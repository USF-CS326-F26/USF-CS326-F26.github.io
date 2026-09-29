# Prep: Setup and Hello, Rust — 00r

**Session:** Thu Aug 27, 1h45 · **Exercises:** `00r_hello_rust` · **Prep time:** ~30 min · **Lecture:** [Week 1 · Building an Operating System, and Your First Rust](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md)

**Most of Thursday is setup.** Work the [Setup page](../assignments/setup.md) step by step: accept both GitHub invitations, clone your repo, toolchain, `oslings doctor` green, first `oslings submit`. Budget 45 minutes.

## What you will build

Your first Rust, and the number formats the kernel is written in. You will name a couple of values a kernel keeps returning to — a page size, the address the kernel is linked at — the way kernel source writes them: hexadecimal, grouped with underscores, integer type spelled out. Then a function or two whose whole body is one expression. Nothing boots; the check is plain `cargo test` on your machine, green when the constants hold the exact values the lecture quotes and the functions return what the tests expect.

## Concepts you need

- **Bindings, `let mut`, and `const`** — [Week 1 · Bindings, `mut`, and `const`](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-bindings)
- **Integer widths: `u8`, `u64`, `usize` as an address** — [Week 1 · Integers name their width](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-widths)
- **Hex literals and the underscore** — [Week 1 · Hex, and the underscore](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-hex), [Hex by hand](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam-hex)
- **Tail expressions and the semicolon that bites** — [Week 1 · Functions, and the semicolon that bites](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-tail)
- **Reading a failed test: `left` and `right`** — [Week 1 · Red, then green](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#00r-tests) · [Using OSlings guide: The three test modes](../guides/oslings-usage.md#the-three-test-modes)
- **The three commands of every session** — [Week 1 · How the Course Runs](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#course-runs) · [Git and Submission guide: What `oslings submit` commits](../guides/git-and-submission.md#what-oslings-submit-commits)

## Read before class

| What | Time |
|---|---|
| [Setup](../assignments/setup.md) | 8 min |
| [Week 1 · This week](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#this-week), then [Thursday · `00r` Hello, Rust](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#thu-00r), all five sections | 8 min |
| [Week 1 · How the Course Runs](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#course-runs): the classroom network, the three commands, and what earns credit | 3 min |
| [Week 1 · For the exam](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam): [Octal, and four spellings of one number](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam-octal), [`as` truncates](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam-as) and [Hex by hand](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#exam-hex). Not needed today; on Midterm 1 | 2 min |
| [Dev Setup guide: Install rustup](../guides/dev-setup.md#1-install-rustup), [Accept your two invitations](../guides/dev-setup.md#3-accept-your-two-invitations) and [`oslings doctor`](../guides/dev-setup.md#7-oslings-doctor) | 5 min |
| [Using OSlings guide: The three test modes](../guides/oslings-usage.md#the-three-test-modes) | 2 min |

**Have done before Thursday:**

- `rustup` installed and `rustc --version` working ([Dev Setup guide: Install rustup](../guides/dev-setup.md#1-install-rustup)); large download.
- A GitHub account, and know which one you are signed in as. Your `oslings-<username>` repository is created *for* you — you do not make one. Accepting the two invitations is Setup step 3, and you can do it at home.
- A charged computer running macOS, Linux, or Windows with WSL2.

## Mental model

```rust
const UART0: usize = 0x1000_0000;   // an address: usize, hex, grouped in fours
const LSR_THRE: u8 = 1 << 5;        // bit 5 of one 8-bit device register

fn can_send(status: u8) -> bool {
    status & LSR_THRE != 0          // no semicolon: this is the value
}
// can_send(0b0010_0000) == true      can_send(0x00) == false
```

Every line is a decision the hardware already made. `0x1000_0000` is where QEMU puts the serial port; hex shows it is one bit twenty-eight places up. `u8` is the register's width, so a read is a one-byte bus transaction, not four. The body of `can_send` is one expression with no semicolon; put one there and the function returns `()`, and the compiler says "expected `bool`, found `()`". Today's exercise is this pattern with different numbers; in `31k_boot` such constants become the kernel's real memory map.

## Check yourself

1. What is `0x1000` in decimal, and how can you tell without dividing that `0x8000_0000` is a multiple of it? <details><summary>Answer</summary>4096; one hex digit is four bits, so `0x1000` is one bit at position 12. A hex numeral ending in three zeros has its low twelve bits clear, so it is a multiple of `0x1000`, as a decimal ending in `000` is a multiple of 1000.</details>
2. What does the compiler say about `fn twice(x: u64) -> u64 { x * 2; }`, and what is the fix? <details><summary>Answer</summary>`error[E0308]: mismatched types`, expected `u64`, found `()`. The semicolon discards the value; delete it, or write `return x * 2;`.</details>
3. Pick the type and binding form: a memory address, a UART register, a free-page count that goes down. <details><summary>Answer</summary>`usize`, `u8`, and `let mut` on a `usize`: bindings are immutable by default, so a value that changes must say so.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

Today "done" also means the [Setup deliverables](../assignments/setup.md#deliverables) are checked off and the commit is visible on github.com.

## If you finish early

- Work [Week 1 · Problem 1: What does the compiler say?](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-1) and [Problem 4: Hex by hand](../lectures/01-cs326-2026-08-25-building-an-os-and-first-rust.md#problem-4) on paper.
- Rustlings (https://github.com/rust-lang/rustlings): `00_intro`, `01_variables`, `02_functions`.
- 100 Exercises To Learn Rust (https://rust-exercises.com/100-exercises/): chapter 2, sections 2.1–2.4.
- Start reading Friday's prep page, [Prep: Control Flow](01-cs326-2026-08-28-prep-control-flow.md).
