# OSlings Debugging

This is the page you open when a Module 1 exercise is red and `oslings` has
told you only that a test failed. Those exercises — `00r`–`08r` and `21r` —
live in the `warmup` crate, which `oslings` grades with `cargo test` and never
runs for you. So you cannot see what your function actually returned, you
cannot try it on an input of your own, and a `println!` you add appears to do
nothing. This
page fixes all three: a scratch `main.rs` you can run, how printing really
behaves under the test harness, and a real debugger. For the kernel from
`31k_boot` on, go to [QEMU and GDB](qemu-gdb.md) instead; for what the harness
runs, see [Using OSlings](oslings-usage.md).

## Why your `println!` disappeared

The harness runs `cargo test`, and cargo **captures** everything a test prints —
stdout and stderr both. A test that passes has its output thrown away; only a
test that *fails* gets its output replayed, in a block headed
`---- tests::name stdout ----`. That is the whole mystery: printing works, but
it is invisible exactly when things go green, and half-visible when they do
not.

```text
running 2 tests
test tests::fails ... FAILED
test tests::passes ... ok

failures:

---- tests::fails stdout ----
f(2)
```

Note what is *not* there: the passing test called `f(1)`, and that line is gone.

To see every print, pass `--nocapture` yourself. `oslings` does not, so run it
by hand from the `warmup` directory:

```bash
cd warmup
cargo test -- --nocapture
```

Output then appears live, interleaved with the test names, whether the test
passes or fails. Add `--test-threads=1` if the interleaving is confusing —
that is what the harness does, and it makes the ordering stable
(`run_host_test()` in `runner.rs`). To run one test on its own, name it:
`cargo test page_list -- --nocapture`.

## A scratch `main.rs`

`warmup` is a library crate, and every item you implement in
`warmup/src/lib.rs` is `pub`. That means a binary in the same crate can call
your work directly. Create **`warmup/src/main.rs`**:

```rust
// Scratch binary — not part of any exercise. Delete before you submit.
use warmup::*;

fn main() {
    let r = MemRegion::of_pages(0x8000_0000, 3);
    println!("start={:#x}  end={:#x}  size={}", r.start, r.end, r.size());
    println!("pages: {:#x?}", r.page_list());
}
```

Cargo discovers `src/main.rs` on its own and builds it as a binary named
`warmup`. Nothing else is needed.

> **Do not add a `[[bin]]` section to `warmup/Cargo.toml`.** You do not need
> one, and that manifest is a file the course owns: change it and your next
> `oslings update` stops and asks you to `git checkout` it before it will do
> anything. Creating `warmup/src/main.rs` touches nothing the course owns —
> the `src` trees are yours.

Run it:

| From | Command |
|---|---|
| `warmup/` | `cargo run` |
| the repo root | `cargo run --manifest-path warmup/Cargo.toml` |

`cargo run -p warmup` from the repo root does **not** work. There is no cargo
workspace in this repo — every crate stands alone — so cargo replies
`error: could not find Cargo.toml in ... or any parent directory`.

This is an ordinary host build on stable Rust. No `--target`, no nightly, no
QEMU, nothing installed beyond `rustup`, which is why it works in week 1 while
your bare-metal setup is still being sorted out. Only `rv6`, `asmlab`, and
`commands` carry a `.cargo/config.toml`; `warmup` deliberately has none.

Run it against an exercise you have not started and you get the most useful
first output there is — what the skeleton returns before you touch it:

```text
start=0x0  end=0x0  size=0
pages: []
```

The example above is written against `04r_structs_impl`. Part 0 is not
cumulative, so the next exercise replaces `lib.rs` with a different set of
functions and this `main` will stop compiling. That is not a bug, but it does
have consequences — see [the last section](#delete-mainrs-before-you-submit).

## Printing from inside your functions

Three tools:

| | Goes to | Use it for |
|---|---|---|
| `println!("{x}")` | stdout | tracing a value at a point you choose |
| `eprintln!("{x}")` | stderr | the same, but out of the way of a shell redirect when you run the binary |
| `dbg!(expr)` | stderr | prints the source location, the expression *as written*, and its value — then **returns the value** |

The test harness captures stdout and stderr alike, so `eprintln!` is no escape
from the previous section — under `cargo test` all three vanish from a passing
test and all three reappear in a failing one.

`dbg!` earns its place by giving the value back, so it wraps a subexpression
with no restructuring: `let n = count * 4;` becomes `let n = dbg!(count) * 4;`
and the code still means what it meant. It labels its output with the source
location and the expression, so you never have to guess which print you are
looking at — `[file:line:col] count = 2`.

This course is written in addresses and bit masks, so the format specifier
matters as much as the value:

| Spec | `4096` prints as |
|---|---|
| `{}` | `4096` |
| `{:x}` / `{:#x}` | `1000` / `0x1000` |
| `{:b}` / `{:#b}` | `1000000000000` / `0b1000000000000` |
| `{:#066b}` | all 64 bits, zero-padded — the way to read a page table entry |
| `{:08x}` / `{:>10}` | zero-padded / right-aligned to a fixed width |
| `{:?}` / `{:#?}` | the derived `Debug` form, compact / pretty-printed over several lines |

`{:#x?}` combines them: `Debug`, with the numbers inside in hex. That is what
makes `println!("{:#x?}", region.page_list())` readable.

### You cannot print inside a `const fn`

Several warmup items are `const fn`, and a `println!` in one does not compile:

```text
error[E0015]: cannot call non-const formatting macro in constant functions
```

The macro reaches `std::io`, which cannot run at compile time. Deleting the
`const` is not the way out either — the tests that ship with the exercise
evaluate these functions in `const` bindings, so dropping it breaks the build a
different way. Print from `main.rs` *around* the call instead:

```rust
let out = page_align_up(0x8000_0001);
println!("page_align_up(0x8000_0001) = {out:#x}");
```

## Stepping through it in a debugger

You already have a debugger. `rustup` installed `rust-lldb` and `rust-gdb` into
`~/.cargo/bin` alongside `cargo`. They are wrappers that start your system
debugger with Rust's pretty-printers loaded, so a `Vec` shows its elements
rather than three raw pointers.

| Platform | Use | Also needs |
|---|---|---|
| macOS | `rust-lldb` | the Xcode command line tools from [Dev Setup](dev-setup.md) |
| Linux, WSL2 | `rust-gdb` | `gdb` from your package manager |

`cargo build` produces the dev profile — unoptimized, with debug info — so
the binary is ready to step through as it stands:

```bash
cd warmup
cargo build
rust-lldb target/debug/warmup      # rust-gdb target/debug/warmup on Linux
```

Then set a breakpoint on your own function and run. Both debuggers accept the
fully qualified Rust path:

| Goal | lldb | gdb |
|---|---|---|
| Break on a function | `b warmup::page_align_up` | `b warmup::page_align_up` |
| Start the program | `run` | `run` |
| Show all locals | `frame variable` | `info locals` |
| Print one value | `p addr` | `p addr` |
| Print it in hex | `p/x addr` | `p/x addr` |
| Next line, stepping over calls | `n` | `n` |
| Step into a call | `s` | `s` |
| Run to the end of this function | `finish` | `finish` |
| Where am I | `bt` | `bt` |
| Keep going | `c` | `c` |
| Leave | `quit` | `quit` |

A session on the exercise above, trimmed:

```text
(lldb) b warmup::page_align_up
Breakpoint 1: where = warmup`warmup::page_align_up + 8 at lib.rs
(lldb) run
* thread #1, stop reason = breakpoint 1.1
    frame #0: warmup`warmup::page_align_up(addr=2147483649) at lib.rs
(lldb) p/x addr
(unsigned long) 0x0000000080000001
(lldb) finish
Return value: (unsigned long) $0 = 0
```

That last line is the one to notice. `finish` prints what your function
returned, which is the question the failing assertion was asking.

Two things that will otherwise confuse you:

- A `const fn` **called from a `const` binding** is evaluated by the compiler,
  so at run time there is no call to stop at and your breakpoint never fires.
  The same function called normally from `main` breaks fine. If a breakpoint
  seems to be ignored, check which of the two you wrote.
- To debug a *test* rather than `main`, build it without running it.
  `cargo test --no-run` prints the path of the binary it produced — something
  like `target/debug/deps/warmup-7aedab94d729abcc`, hash and all. Open that
  path in the debugger and start it with the test's name:
  `run addresses_round_up_to_page_boundaries --test-threads=1`.

This is a different activity from [QEMU and GDB](qemu-gdb.md). There, a RISC-V
cross-`gdb` attaches over a socket to a machine QEMU is emulating. Here you are
running a native binary under your own system debugger. The two share the word
"breakpoint" and very little else.

## Delete `main.rs` before you submit

Part 0 is not cumulative: each exercise replaces `warmup/src/lib.rs` wholesale,
and nothing ever removes a file you added. Meanwhile `oslings` grades `warmup`
with a plain `cargo test` over the whole package, and that compiles **every**
target in it — your scratch binary included.

Put those two facts together and a leftover `main.rs` fails the *next* exercise,
against a `lib.rs` that is completely correct:

```text
  ✗ not yet  04r_structs_impl
    tests failed to compile

error[E0425]: cannot find function `pgroundup` in this scope
 --> src/main.rs:2:31
```

Nothing there mentions `main.rs` until the fourth line, and the exercise it
names is not the one the stale code came from.

> **Delete it before you submit.** `oslings submit` commits everything under
> `warmup/src`, your scratch binary included, and the grader recompiles it when
> it re-runs your past exercises. One stale `main.rs` can fail an exercise you
> passed weeks ago. Deleting it loses nothing: `oslings` archives it to
> `my-work/<exercise>/main.rs` before every overwrite, exactly as it does your
> `lib.rs`.
>
> ```bash
> rm warmup/src/main.rs
> ```

Two smaller things worth knowing:

- Saving `main.rs` re-runs the current exercise. `oslings watch` and the app
  watch `warmup/src` recursively (`watch()` in `watch.rs`), and they do not
  filter by filename. Expected, not a fault.
- `main.rs` counts as work you own, not course material, so `oslings goto` and
  `oslings reset` will not delete it for you. That is deliberate — losing a
  scratch file you wrote is the bug the archive exists to prevent — but it
  does mean the cleanup is yours to do.

### When it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `tests failed to compile`, and the errors name functions you do not recognize | a `main.rs` left over from an earlier exercise | rewrite it for this exercise, or `rm warmup/src/main.rs` |
| `error[E0425]: cannot find function ... in this scope`, pointing at `src/main.rs` | the same | the same |
| An exercise that passed weeks ago fails when it is re-graded | a stale `main.rs` was committed by `oslings submit` | delete it and submit again |
| `oslings update` refuses: `warmup/Cargo.toml` has uncommitted changes | you added a `[[bin]]` section | `git checkout -- warmup/Cargo.toml`; cargo needs no section to find `src/main.rs` |
| `error: no bin target named warmup` | the file is not at `warmup/src/main.rs` | move it there — the path is what cargo looks for |
| `error: could not find Cargo.toml` | you ran `cargo run -p warmup` from the repo root | `cd warmup && cargo run`, or use `--manifest-path` |
| `error[E0015]: cannot call non-const formatting macro in constant functions` | a `println!` or `dbg!` inside a `const fn` | print from `main.rs` around the call instead |
| A breakpoint on a `const fn` never fires | the compiler evaluated the call | call the function from `main` rather than in a `const` binding |

The Part 1 command exercises (`10c`–`14c`) need none of this. Each is already
a binary you can run directly with `cargo run --bin echo` from the `commands`
directory, and the harness grades each one on its own, so a broken scratch file
there cannot take another exercise down with it.

## See also

- [Using OSlings](oslings-usage.md) — what the harness runs, the three test modes, and where your code is staged
- [Rust for Systems](rust-for-systems.md) — the language behind these exercises, and what the common compiler errors mean
- [Dev Setup](dev-setup.md) — installing the toolchain, and what `oslings doctor` checks
- [QEMU and GDB](qemu-gdb.md) — the other debugging page, for the kernel from `31k_boot` on
