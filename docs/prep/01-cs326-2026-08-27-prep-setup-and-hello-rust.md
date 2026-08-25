# Prep: Setup and Hello, Rust — 00r

**Session:** Thu Aug 27, 1h45 · **Exercises:** `00r_hello_rust` · **Prep time:** ~30 min · **Lecture:** [Rust I: Values, Types, and Control Flow](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md)

**Most of Thursday is setup.** Work the [Setup page](../assignments/setup.md) step by step: private repository, toolchain, `oslings doctor` green, first `oslings submit`. Budget 45 minutes.

## What you will build

Your first Rust, and the number formats the kernel is written in. You will name a couple of values a kernel keeps returning to — a page size, the address the kernel is linked at — the way kernel source writes them: hexadecimal, grouped with underscores, integer type spelled out. Then a function or two whose whole body is one expression. Nothing boots; the check is plain `cargo test` on your machine, green when the constants hold the exact values the lecture quotes and the functions return what the tests expect.

## Concepts you need

- **Bindings, `let mut`, and `const`** — [Rust I §1](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#1-bindings-and-immutability-as-a-decision) · [`const` versus `let`](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#const-versus-let)
- **Integer widths: `u8`, `u64`, `usize` as an address** — [Rust I §2](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#2-scalar-types-and-why-width-is-hardware)
- **Hex literals and the underscore** — [Rust I §3](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#3-hex-binary-and-the-underscore) · [the underscore is nothing](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#the-underscore-is-nothing)
- **Tail expressions and the semicolon that bites** — [Rust I §4](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#4-expressions-statements-and-the-semicolon-that-bites) · [Rust I §5](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#5-functions)
- **The three commands of every session** — [Building an Operating System §6](../lectures/01-cs326-2026-08-25-course-intro-and-what-an-os-is.md#6-how-the-course-runs) · [Git and Submission, `oslings submit`](../guides/git-and-submission.md#what-oslings-submit-commits)

## Read before class

| What | Time |
|---|---|
| [Setup](../assignments/setup.md) | 8 min |
| [Rust I §§1–5](../lectures/01-cs326-2026-08-27-rust-values-types-and-control-flow.md#1-bindings-and-immutability-as-a-decision) | 15 min |
| [Dev Setup §1](../guides/dev-setup.md#1-install-rustup), [§3](../guides/dev-setup.md#3-create-your-own-private-repository), [§7](../guides/dev-setup.md#7-oslings-doctor) | 5 min |
| [Using OSlings: test modes](../guides/oslings-usage.md#the-three-test-modes) | 2 min |

**Have done before Thursday:**

- `rustup` installed and `rustc --version` working ([Dev Setup §1](../guides/dev-setup.md#1-install-rustup)); large download.
- A GitHub account. The `oslings-<username>` repository is Setup step 3; if made at home, follow the rules: private, empty, instructor and TA added.
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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Thursday 11:59 pm** and submit again.

Today "done" also means the [Setup deliverables](../assignments/setup.md#deliverables) are checked off and the commit is visible on github.com.

## If you finish early

- Rustlings (https://github.com/rust-lang/rustlings): `00_intro`, `01_variables`, `02_functions`.
- 100 Exercises To Learn Rust (https://rust-exercises.com/100-exercises/): chapter 2, sections 2.1–2.4.
- Start reading Friday's prep page, [Prep: Control Flow](01-cs326-2026-08-28-prep-control-flow.md).
