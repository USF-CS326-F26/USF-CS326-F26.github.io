# Booting the Reference Kernels

`oslings-boot` boots the reference solution of a kernel exercise in QEMU, so
you can watch a kernel that works next to yours. Use it to check what a passing
`39k_virtual_memory` prints before you go hunting through your own. From
`42k_boot_to_life` on, you can try the interactive rv6. You can also stop a
working kernel in gdb and compare its registers with what yours holds at the
same point. `oslings solution` prints a reference solution; this script boots
it.

It builds in a temporary copy of the crate, which it deletes afterward, so
your `rv6/src` is never touched. It boots only the solutions already in your
repo. A solution ships with the *next* exercise's release, after the deadline,
and `oslings update` fetches it (see
[Using OSlings](oslings-usage.md#the-ones-with-surprises-in-them)). Try the
exercise yourself first. The [Integrity Policy](integrity-policy.md) explains
why that order matters.

## Install it

The script is a single bash file. It runs as-is on macOS, Linux and WSL2:

```bash
curl -fsSL https://cs326-f26.cs.usfca.edu/assets/oslings-boot \
  -o ~/.cargo/bin/oslings-boot
chmod +x ~/.cargo/bin/oslings-boot
oslings-boot --help
```

`~/.cargo/bin` is where `oslings` lives, so it is already on your `PATH`. To
pick up a newer version later, run the same two commands again.

> On Windows, run everything inside WSL, in the same Ubuntu where your repo
> lives. Don't save the file from a browser on the Windows side: it arrives
> with Windows line endings, and bash refuses to run it.

| You need | For | You have it if |
|---|---|---|
| `qemu-system-riscv64` | booting | `oslings doctor` is green ([Dev Setup](dev-setup.md)) |
| A RISC-V gdb | debugging only | [QEMU and GDB](qemu-gdb.md#getting-a-risc-v-gdb): `brew install riscv64-elf-gdb` on macOS, `sudo apt install gdb-multiarch` on Ubuntu and WSL2 |

## Boot a reference kernel

Run it from inside your `oslings` repo. `--list` shows the kernel exercises
whose solutions you have, and any unique prefix picks one:

```bash
cd ~/oslings
oslings-boot --list
oslings-boot 39k
```

```text
== 39k_virtual_memory (reference solution): self-test, powers off when done
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.63s
     Running `qemu-system-riscv64 -machine virt -bios none -m 128M -smp 1 -nographic -serial 'mon:stdio' -kernel target/riscv64gc-unknown-none-elf/debug/rv6`

rv6 booting (exercise 39k: virtual memory)...
  [ok] kernel page table verified; MMU is now ON
OSLINGS:PASS
```

That is the same QEMU command line that `cargo run` uses in your own `rv6/`.
What a plain boot does depends on the exercise:

| Exercise | A plain boot |
|---|---|
| `30k_kernel_basics` | Compiles only. There is nothing to boot yet |
| `31k_boot` to `41k_devices` | Runs the exercise's self-test, prints `OSLINGS:PASS` and powers off |
| `42k_boot_to_life` on | Boots the interactive rv6. Quit with `Ctrl-A` then `x` |

From 42k on, `oslings-boot --harness 46k` (or `-H`) builds the graded
self-check instead, the run that prints `OSLINGS:PASS` and powers off. If QEMU
seems stuck, remember that `Ctrl-C` goes to the guest, not to QEMU; see
[how to get out of QEMU](qemu-gdb.md#first-how-to-get-out-of-qemu).

## Step through one in gdb

`--tree` writes the exercise out as a standalone rv6 crate, with scripts that
run the [two-terminal loop](qemu-gdb.md#the-two-terminal-loop) for you. Give it
a place outside your repo with `--into`:

```bash
oslings-boot --tree --into ~/rv6-41k 41k
```

```text
== wrote 41k_devices (reference solution) to /home/you/rv6-41k

   cd /home/you/rv6-41k
   cargo run                         # boot it (add --features harness for the self-check)
   ./qemu-gdb                        # terminal 1: build and boot halted, waiting for gdb
   ./gdb-attach                      # terminal 2: connect, stop at kmain, then 'c'
   ./gdb-attach --tui                #   ... or the same with source, asm, registers and CSRs
```

Without `--into`, the tree lands in the current directory as `rv6-41k_devices`.
Inside your repo, `oslings submit` would never commit it, but `git status`
would list it on every run. `--tree` never overwrites an existing tree,
because it may hold your edits.

Then use two terminals, both in the tree:

```bash
./qemu-gdb      # terminal 1: builds, then starts QEMU halted
./gdb-attach    # terminal 2: connects, runs gdbinit, stops at kmain
```

Terminal 1 says `qemu-gdb: halted, waiting for gdb on localhost:1234` and
then shows nothing more until the kernel prints. In terminal 2, gdb stops at
the first line of `kmain`. `c` continues, `Ctrl-C` in gdb stops the machine
again, and every command in [QEMU and GDB](qemu-gdb.md) works from there. To
finish, type `quit` in gdb, then `Ctrl-A` `x` in terminal 1.

| In the tree | What it is |
|---|---|
| `src/` | The reference sources. Edit them freely; `cargo run` boots your edits |
| `gdbinit` | gdb commands run on every attach: `break kmain`, plus your own |
| `qemu-gdb` | Builds, then runs QEMU with `-S` (start halted) and a gdb server. Extra arguments go to `cargo build`, so `./qemu-gdb --features harness` debugs the self-check |
| `gdb-attach` | Finds your RISC-V gdb (`riscv64-elf-gdb`, `riscv64-unknown-elf-gdb`, then `gdb-multiarch`) and connects |
| `gdb-tui.py` | The layouts behind `./gdb-attach --tui` |

`gdb-attach` starts gdb through `rust-gdb`, which `rustup` installed, so Rust
values print readably. Set `RISCV_GDB` to choose a different gdb binary. Set
`GDB_PORT` in *both* terminals to move off port 1234, for instance when two
trees are running at once.

### The TUI

`./gdb-attach --tui` opens a full-screen layout. Its two lower windows are
redrawn at every stop, and a value that changed since the previous stop is
shown in bold:

```text
┌ src ──────────────────────┬ asm ──────────────────────┐
│ the Rust line you are on  │ the instructions near pc  │
├ registers ────────────────┼ CSRs ─────────────────────┤
│ pc ra sp gp tp, a0-a7,    │ priv, satp, sstatus,      │
│ s0-s11, t0-t6             │ stvec, sepc, scause, ...  │
│ pc and ra as symbols      │ decoded beside each value │
├───────────────────────────┴───────────────────────────┤
│ (gdb)                                                 │
└───────────────────────────────────────────────────────┘
```

The CSR window decodes as it goes. On attach, for instance, it shows
`priv M`, `satp 0x0000000000000000 Bare (paging off)` and `scause` as a named
exception. `sepc`, `mepc` and the trap vectors print as symbols, not bare
addresses.

| Layout | Shows | Use it for |
|---|---|---|
| `layout rv6` | source and asm, registers and CSRs, command line | the default |
| `layout rv6-asm` | asm and CSRs, then registers | `_entry`, trap vectors, `swtch`, the trampoline: code with no Rust source |
| `layout rv6-small` | source and CSRs | a terminal that is not very big |

A few keys help. `focus csrs` (or `focus gregs`) lets the arrow keys scroll that
window; `focus cmd` gives them back to the command history. `Ctrl-X` `A` turns
the TUI off and on, and `winheight cmd 12` makes the command window taller.

## Which repo it reads

It looks in three places, in this order:

1. `$OSLINGS_ROOT`, if you set it.
2. The nearest directory at or above the current one that holds `info.toml`
   and `rv6/`, which is your repo whenever you are anywhere inside it.
3. `~/oslings`, the folder [Dev Setup](dev-setup.md) clones into.

A tree made by `--tree` doesn't need the repo again, so `./qemu-gdb` and
`./gdb-attach` work from anywhere.

## When it goes wrong

| You see | Do this |
|---|---|
| `oslings-boot: command not found` | Open a new terminal, or run `source ~/.cargo/env` |
| `no OSlings repo at …: run this inside your oslings repo, or set OSLINGS_ROOT` | `cd` into your repo first |
| `no released kernel solution matches '45k'` | That solution is not out yet. `oslings update` fetches new ones once they ship |
| `gdb-attach: no RISC-V gdb found` | Install one: see [Getting a RISC-V GDB](qemu-gdb.md#getting-a-risc-v-gdb) |
| `… already exists; remove it first to recreate it` | Pick another `--into`, or delete the old tree if you don't need your edits |
| `/usr/bin/env: 'bash\r': No such file or directory` | The file was saved on the Windows side. Rerun the `curl` line inside WSL |
| gdb waits, then says `Connection timed out` (Linux) or `Operation timed out` (macOS) | Start `./qemu-gdb` first, and use the same `GDB_PORT` in both terminals |
| `Failed to find an available port: Address already in use` | Another `./qemu-gdb` is still running. Quit it with `Ctrl-A` `x`, or set `GDB_PORT` |

## See also

- [QEMU and GDB](qemu-gdb.md): the commands to use once you are attached, and walking a page table by hand
- [Using OSlings](oslings-usage.md): `oslings solution`, `oslings update`, and how the harness runs QEMU
- [rv6 Architecture](rv6-architecture.md): where each part of the reference kernel lives
- [Dev Setup](dev-setup.md): installing QEMU and the toolchain
