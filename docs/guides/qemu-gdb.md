# Debugging rv6 with QEMU and GDB

This is the page you open when your kernel prints nothing, hangs, faults, or
"worked until I turned the MMU on." From `31k_boot` onward, `oslings` runs your
kernel inside QEMU and shows you a serial log; when that log is empty, or ends
mid-sentence, the only way forward is to stop the machine and look at it. QEMU
has a GDB server built in, and attaching to it takes two commands. Everything
below is written for the exact QEMU command line this course uses, and every
transcript on this page was captured from the reference kernel. Pair it with
[Sv39 Paging](sv39-paging.md) for the bit layouts and [RISC-V](riscv.md) for
what each CSR means.

## First: how to get out of QEMU

Students lose more time to this than to any actual bug. `Ctrl-C` does **not**
quit QEMU — it is delivered to the guest, which does not have a signal
handler, so nothing happens.

| Keys | Effect |
|---|---|
| `Ctrl-A` then `x` | **Quit QEMU.** Release `Ctrl-A` before pressing `x` |
| `Ctrl-A` then `c` | Toggle between the guest console and the QEMU monitor |
| `Ctrl-A` then `h` | Print the list of `Ctrl-A` commands |
| `Ctrl-A` then `a` | Send a literal `Ctrl-A` to the guest |

This works because the course command line contains `-serial mon:stdio`. The
`mon:` prefix multiplexes the QEMU **mon**itor onto the same terminal as the
guest's serial port, and `Ctrl-A` is the multiplexer's escape prefix. Drop
`mon:` and there is no escape key: you must kill QEMU from another terminal.

One case where `Ctrl-A x` will not help: a QEMU you started with `-S` and never
resumed. It is frozen before it has read a single keystroke, and in practice it
does not always die from a plain `kill` either. From a second terminal:

```bash
pkill -9 -f qemu-system-riscv64
```

## Getting a RISC-V GDB

You need a GDB built for `riscv64`. Your system `gdb` (if any) is built for
your laptop's architecture and cannot disassemble RISC-V.

| Platform | Install | Binary name |
|---|---|---|
| macOS | `brew install riscv64-elf-gdb` | `riscv64-elf-gdb` |
| Debian / Ubuntu / WSL2 | `sudo apt install gdb-multiarch` | `gdb-multiarch` |

On macOS, `brew install riscv-gnu-toolchain` is worth having too — it provides
`riscv64-unknown-elf-objdump`, `-nm`, and `-readelf`, which are useful for
static questions ("what address did `kernelvec` land at?"). It does **not**
ship a debugger; the `riscv64-elf-gdb` formula is separate. If your machine has
`riscv64-unknown-elf-gdb` from some other toolchain, that works identically —
substitute the name everywhere below.

With `gdb-multiarch`, if it does not infer the architecture from the ELF, say
`set architecture riscv:rv64` after loading the file.

**Do not reach for `lldb`.** It will connect, and it even exposes the CSRs, but
on connecting it prints `This version of LLDB has no plugin for the language
"rust". Inspection of frame variables will be limited.` — which is exactly the
capability page-table debugging needs, since you spend the whole time printing
`(*p).pagetable` and dereferencing `*mut Pte`. Every command on this page is GDB syntax.

## The two-terminal loop

### Terminal 1 — QEMU, stopped and waiting

```bash
cd rv6
cargo build                  # or: cargo build --features harness
qemu-system-riscv64 -machine virt -bios none -m 128M -smp 1 \
  -nographic -serial mon:stdio \
  -kernel target/riscv64gc-unknown-none-elf/debug/rv6 \
  -s -S
```

That is the standard course command line (`runner.rs`) plus two flags:

| Flag | Long form | Meaning |
|---|---|---|
| `-s` | `-gdb tcp::1234` | Listen for a debugger on TCP port 1234 |
| `-S` | — | Do not start the CPU; freeze at the reset vector until told to run |

Use `-s` alone if you want the kernel to boot normally and plan to attach
later — that is the right choice for a hang, since you can attach *after* it
wedges and ask where it is. Use `-s -S` when the bug happens before the first
byte of output.

To run two kernels at once, or if port 1234 is taken, replace `-s` with
`-gdb tcp::4321`. If you forget, QEMU is blunt about it:

```text
qemu-system-riscv64: -s: Failed to find an available port: Address already in use
qemu-system-riscv64: -s: gdbstub: couldn't create chardev
```

`oslings` builds kernel exercises with `--features harness`, which makes the
kernel run its self-check and then power off (`main.rs`). A plain
`cargo build` gives you the interactive kernel instead. Debug whichever one is
failing — they take different paths through `kmain`.

### Terminal 2 — GDB

```bash
cd rv6
riscv64-elf-gdb
(gdb) file target/riscv64gc-unknown-none-elf/debug/rv6
(gdb) target remote :1234
```

`file` loads symbols and DWARF from your kernel ELF — without it you get bare
addresses and no source lines. `target remote` connects to QEMU's stub. Order
matters: load symbols first, then connect.

`cargo build` in `rv6/` already produces a debug build with full line info
(`Cargo.toml` sets `panic = "abort"` but leaves `opt-level` at 0), so there is
nothing to configure. Note that the ELF is a *kernel*, not a program: GDB never
runs `run`, `start`, or `attach`. QEMU is already the process.

## What you see the instant you attach

```text
(gdb) target remote :1234
0x0000000000001000 in ?? ()
(gdb) x/6i $pc
=> 0x1000:	auipc	t0,0x0
   0x1004:	addi	a2,t0,40
   0x1008:	csrr	a0,mhartid
   0x100c:	ld	a1,32(t0)
   0x1010:	ld	t0,24(t0)
   0x1014:	jr	t0
```

`0x1000` surprises everyone. Even with `-bios none`, the `virt` machine has a
tiny hard-wired reset vector in ROM at `0x1000`; those six instructions load
the hart id into `a0`, the device tree address into `a1`, and jump to
`0x8000_0000`, which is where your `_entry` was linked (`kernel.ld`). `?? ()`
just means no symbol covers `0x1000` — correct, since that ROM is not part of
your ELF.

`p/x $satp` here reads `0x0`: paging is off, and stays off until `kvminithart`
writes it (`vm.rs`).

## Breakpoints in `no_std` code

There is no libc, no dynamic loader, and no `main`, but breakpoints work
normally because the DWARF is normal.

| Form | Example | When |
|---|---|---|
| Rust path | `b rv6::vm::walk` | Any Rust function. Crate name first |
| `#[no_mangle]` name | `b kmain` | Symbols exported for the linker: `kmain`, `start`, `_entry`, `usertrap` |
| File and line | `b vm.rs` | The usual workhorse. Bare filename is enough |
| Assembly label | `b uservec` | Labels inside `global_asm!` are real symbols |
| Raw address | `b *0x80000000` | No prologue skipping — the exact instruction |

Two things bite people:

**GDB skips prologues, including in assembly.** `b kernelvec` resolves to
`kernelvec+38`, past the register saves, which is wrong if the bug is in the
saves. Use `b *kernelvec` for the first instruction.

**Line numbers inside `asm!` all report the macro's opening line.** Every
instruction in `_entry`'s block shows as `entry.rs`, because that is where
the `asm!` starts (`entry.rs`). Do not conclude the kernel is stuck; switch
to instruction stepping.

A backtrace works all the way down to the reset:

```text
Breakpoint 1, rv6::vm::walk (table=0x87fff000, va=268435456, alloc=true) at src/vm.rs
53	    let mut level = 2;
(gdb) bt
#0  rv6::vm::walk (table=0x87fff000, va=268435456, alloc=true) at src/vm.rs
#1  0x000000008000d270 in rv6::vm::mappages (...) at src/vm.rs
#2  0x000000008000d006 in rv6::vm::kvmmake () at src/vm.rs
#3  0x000000008000dae2 in rv6::kinit () at src/main.rs
#4  0x000000008000db3c in rv6::kmain () at src/main.rs
#5  0x00000000800049aa in rv6::start::start () at src/start.rs
#6  0x0000000080000014 in rv6::entry::_entry () at src/entry.rs
Backtrace stopped: frame did not save the PC
```

That last line is not an error. `_entry` never saved a return address, because
there is nowhere to return to.

## Reading machine state

| Command | Shows |
|---|---|
| `x/16i $pc` | The next 16 instructions, disassembled |
| `info registers` | The 31 general registers plus `pc`. **No CSRs** |
| `info registers satp sepc scause stval` | Just those CSRs |
| `info registers csr` | Every CSR the stub exposes — long, but complete |
| `p/x $satp` | One CSR in hex. `p` defaults to signed decimal, which is useless here |
| `x/8gx addr` | Eight 8-byte ("giant") words in hex, starting at `addr` |
| `x/s addr` | A NUL-terminated string |
| `info files` | Section addresses and the entry point |

`x` format letters are worth memorizing: `i` instructions, `x` hex, `d`
decimal, `s` string, `c` char; sizes are `b` 1, `h` 2, `w` 4, `g` 8. `x/8gx` is
"eight giant words in hex" — the right shape for page tables, which are 512
eight-byte entries.

CSRs are the whole game in a kernel and `info registers` hides them, which
catches people out every year. After any fault, these four answer most of the
question:

```text
(gdb) info registers satp sepc scause stval
satp   0x8000000000087fff
sepc   0x12
scause 0xf
stval  0x10fc0
```

`scause 0xf` is 15, a store/AMO page fault. `sepc 0x12` is the user PC of the
faulting instruction. `stval 0x10fc0` is the address it tried to write —
inside the user stack page at `USER_STACK = 0x1_0000` (`memlayout.rs`). The
cause table lives in [RISC-V](riscv.md); the three you will see are 12
(instruction), 13 (load), and 15 (store) page faults.

## Single-stepping into assembly

| Command | Steps by |
|---|---|
| `si` (`stepi`) | One **instruction**, into calls |
| `ni` (`nexti`) | One instruction, over calls |
| `s` / `n` | One **source line** — nearly useless inside `asm!` |
| `finish` | Run to the end of the current frame, print the return value |
| `layout asm` / `layout split` | Curses view of disassembly, auto-updating |

Stepping through `_entry` (`entry.rs`) shows what the assembler actually
emitted, which is not what you typed:

```text
=> 0x80000000 <rv6::entry::_entry>:	auipc	sp,0x17
   0x80000004 <rv6::entry::_entry+4>:	addi	sp,sp,-496
   0x80000008 <rv6::entry::_entry+8>:	lui	t0,0x4
   0x8000000a <rv6::entry::_entry+10>:	add	sp,sp,t0
   0x8000000c <rv6::entry::_entry+12>:	auipc	ra,0x5
   0x80000010 <rv6::entry::_entry+16>:	jalr	-1734(ra)
```

`la sp, STACK0` became `auipc`/`addi`; `li t0, 16384` became `lui t0, 0x4`;
`call start` became `auipc`/`jalr`. Also note the addresses jump by 2 in
places: those are compressed (`c.*`) instructions from the `c` extension in
`riscv64gc`. Three `si`s from the top and `p/x $sp` reads `0x80016e10` — the *base* of
`STACK0`. The fourth instruction, `add sp, sp, t0`, adds `0x4000` to reach the
top, because the stack grows down (`entry.rs`). Establishing that one
register is the entire job of `_entry`.

`finish` is the fastest way to answer "what did that return?":

```text
(gdb) finish
Run till exit from #0  rv6::vm::walk (...) at src/vm.rs
Value returned is $4 = (*mut rv6::vm::Pte) 0x87ffd000
```

## Walking a page table by hand

**This is the highest-value technique on this page.** From `33k_paging` to the
end of the course, most kernel bugs are one wrong bit in one PTE, and the only
way to see it is to follow the pointers the hardware follows. Your kernel's own
`walk` (`vm.rs`) is often the thing under suspicion, so you cannot use it
to check itself. Do it with `x/gx`.

The layout is in [Sv39 Paging](sv39-paging.md); here is only what you type.

### Step 1 — find the root table

`satp` holds the mode in bits 63:60 and the root table's **physical page
number** in bits 43:0 (`SATP_SV39` in `vm.rs`). Shift the PPN back into an address:

```text
(gdb) p/x $satp
$1 = 0x8000000000087fff
(gdb) set $root = ($satp & 0xfffffffffff) << 12
(gdb) p/x $root
$2 = 0x87fff000
```

The leading `8` is `SATP_SV39`. A root table address always ends in `000`; if
yours does not, you shifted wrong.

Because the kernel's own table identity-maps all of RAM (`kvmmake()` in `vm.rs`) and
paging is off before `kvminithart`, physical addresses are directly readable
with `x` in both cases. That is a property of *this* kernel, not of RISC-V.

### Step 2 — index by VPN[2] and read the entry

```text
(gdb) set $va = 0x80000000
(gdb) p (($va >> 30) & 0x1ff)
$3 = 2
(gdb) x/gx $root + 2*8
0x87fff010:	0x0000000021ffe401
```

`+ 2*8` because entries are 8 bytes. `0x...401`: low ten bits are `0x001` — V
set, R/W/X clear, so this is a **branch**. The next table is
`(0x21ffe401 >> 10) << 12` = `0x87ff9000`.

### Step 3 — repeat, twice

VPN[1] is `($va >> 21) & 0x1ff`, VPN[0] is `($va >> 12) & 0x1ff`. Written out
with `printf` so you can read it:

```text
satp = 0x8000000000087fff
root = 0x87fff000
L2: index   2  pte=0x0000000021ffe401  flags=0x001 -> 0x87ff9000
L1: index   0  pte=0x0000000021ffe001  flags=0x001 -> 0x87ff8000
L0: index   0  pte=0x000000002000000f  flags=0x00f -> pa 0x80000000
```

Flags `0xf` = V+R+W+X: the kernel's identity mapping of RAM, exactly what
`kvmmake` asked for (`vm.rs`). Virtual `0x8000_0000` is physical
`0x8000_0000` — boring, and that is the point: when it is *not* boring you have
found your bug.

### The script

Paste this into `walk.gdb` and run `source walk.gdb` after setting `$root` and
`$va`. `set language c` is required: in Rust mode GDB rejects the C cast with
`No symbol 'unsigned' in current context`.

```text
set language c
set $i2 = ($va >> 30) & 0x1ff
set $p2 = *(unsigned long *)($root + $i2*8)
printf "L2: idx %3d pte=0x%016lx flags=0x%03lx -> 0x%lx\n", $i2, $p2, $p2 & 0x3ff, ($p2>>10)<<12
set $t1 = ($p2 >> 10) << 12
set $i1 = ($va >> 21) & 0x1ff
set $p1 = *(unsigned long *)($t1 + $i1*8)
printf "L1: idx %3d pte=0x%016lx flags=0x%03lx -> 0x%lx\n", $i1, $p1, $p1 & 0x3ff, ($p1>>10)<<12
set $t0 = ($p1 >> 10) << 12
set $i0 = ($va >> 12) & 0x1ff
set $p0 = *(unsigned long *)($t0 + $i0*8)
printf "L0: idx %3d pte=0x%016lx flags=0x%03lx -> pa 0x%lx\n", $i0, $p0, $p0 & 0x3ff, ($p0>>10)<<12
```

### Reading the flags you land on

| Low bits | Meaning | Where it is right |
|---|---|---|
| `0x001` | V only — a branch | Interior nodes at L2 and L1 |
| `0x00f` | V+R+W+X | Kernel identity map of RAM |
| `0x007` | V+R+W | MMIO: UART, PLIC, test finisher (`vm.rs`) |
| `0x00b` | V+R+X, no U | The trampoline page |
| `0x01b` | V+R+X+U | A user code page |
| `0x017` | V+R+W+U | A user stack page |
| `0x000` | not present | The walk stops here; hardware faults |

R/W/X all zero on a **leaf** level means you are not at a leaf at all. R/W/X
set on an **interior** entry means you accidentally made a superpage and the
walk stopped early — two levels early at L2, one at L1.

### Walking a user address space

A process's root is in its `Proc`, so let GDB read it for you rather than
copying hex:

```text
Breakpoint 1, rv6::usermode::usertrapret (p=0x80017da0 <rv6::proc::PROCS>) at src/usermode.rs
(gdb) set $root = (*p).pagetable
(gdb) p/x $root
$1 = 0x87fb2000
(gdb) p/x (*(*p).trapframe).epc
$2 = 0x0
(gdb) p/x (*(*p).trapframe).sp
$3 = 0x10fe0
```

`epc = 0` is `USER_CODE`, `sp = 0x10fe0` is just below `USER_STACK_TOP`
(`memlayout.rs,75`). Then walk `$va = 0x10000` and confirm the level-0 entry
reads `0x17`. If it reads `0x13` — V+R+U, no W — the program will die on its
first push with `scause 15`, which is exactly the fault shown earlier.

Your physical addresses will not match these; they depend on how many pages
`kalloc` has handed out. The *shape* is what you compare against
[Sv39 Paging](sv39-paging.md).

## The shortcut, and why to distrust it

QEMU's monitor is reachable from GDB with `monitor`, and `monitor info mem`
dumps every mapping the current `satp` produces:

```text
(gdb) monitor info mem
vaddr            paddr            size             attr
---------------- ---------------- ---------------- -------
0000000000100000 0000000000100000 0000000000001000 rw-----
000000000c000000 000000000c000000 0000000000200000 rw-----
000000000c200000 000000000c200000 0000000000200000 rw-----
0000000010000000 0000000010000000 0000000000001000 rw-----
0000000080000000 0000000080000000 000000000000c000 rwx----
...
0000003ffffff000 0000000087fb8000 0000000000001000 r-x----
```

Line 1 is the test finisher, lines 2-3 the PLIC's 4 MiB, line 4 the UART, then
RAM in chunks, and the last line is the trampoline at `TRAMPOLINE`
(`memlayout.rs`). It is excellent for "is it mapped at all?" and for
spotting a missing region in one glance.

Two caveats. It shows the table the hardware is using *now*, so it tells you
nothing about a user page table you have built but not installed. And it will
not teach you the walk, which is an exam topic and a debugging skill you need
when the table is malformed rather than merely wrong. Use it to confirm, not to
discover.

`monitor` reaches the rest of the monitor too: `monitor info registers` prints
QEMU's own view of every CSR, and `monitor quit` kills the VM from GDB.

## A `.gdbinit` worth keeping

Put this in `rv6/.gdbinit` so `riscv64-elf-gdb` with no arguments lands you
connected:

```text
set confirm off
set pagination off
file target/riscv64gc-unknown-none-elf/debug/rv6
target remote :1234
break kmain
```

If GDB refuses it with a warning about `auto-load safe-path`, add this line to
`~/.gdbinit` (with your real path):

```text
add-auto-load-safe-path /Users/you/oslings/rv6
```

## Diagnostic playbook

| Symptom | Most likely cause | First move in GDB |
|---|---|---|
| **Total silence** — no banner, no output at all | Faulted before `uart::init`, or `_entry` never got a stack | Attach with `-s` (no `-S`), then `info registers pc sp`. `pc` in ROM at `0x1000`-ish means you never reached `0x8000_0000`; `sp = 0` means `_entry` did not run |
| **Reset loop** — the banner prints over and over | Something returns to `_entry`, or the machine re-enters at `0x8000_0000` | `b *0x80000000`, then `continue` twice and `bt` on the second hit. Also check `p/x $mepc` and `p/x $mcause` |
| **Store page fault** (`scause` 15) | A user page mapped without `PTE_W`, or a store through a stale/unmapped VA | `info registers sepc scause stval`, then walk `stval` and read the leaf flags. `0x13` instead of `0x17` on the stack page is the classic |
| **"It worked until I turned the MMU on"** | The kernel's own text is not mapped in the table you installed, so the instruction *after* `csrw satp` cannot be fetched | Attach and read `pc`, `scause`, `satp`. The real transcript: `pc = 0x0`, `satp = 0x8000000000087fff`, `scause = 0xc` (instruction page fault). `pc = 0` means it trapped and `stvec` was still 0. Check `kvmmake` maps `KERNBASE..PHYSTOP` and that `trap::init` runs |
| **QEMU exits immediately**, status 0 | Your kernel wrote `0x5555` to the test finisher at `0x10_0000` — `exit_success` (`testdev.rs`), usually via the harness self-check or a panic path | `b rv6::testdev::exit_success` and `b rv6::testdev::exit_failure`, then `bt` to see who called it. `OSLINGS:FAIL (panic)` in the log means the panic handler (`main.rs`) |
| **QEMU hangs** — no output, no exit; `oslings` reports a timeout after 10s (`runner.rs`) | An infinite loop, a spin on a device bit that never sets, or a fault loop with `stvec` pointing somewhere harmless | Attach with `-s`, press `Ctrl-C` in GDB, then `bt` and `x/8i $pc`. A `pc` that never leaves three instructions is a spin; a `pc` that keeps returning to your trap vector is a fault loop |
| GDB connects but registers and disassembly are nonsense, or it complains about the remote `g` packet | Wrong GDB architecture | `set architecture riscv:rv64`, or use a `riscv64-*` GDB |
| Breakpoints never hit, symbols look wrong | Stale ELF — you rebuilt after starting QEMU | Kill both, `cargo build`, restart. QEMU loaded the ELF at launch |
| Source lines say `asm!(` forever | You are inside an `asm!` block | `si` and `x/8i $pc` instead of `s` |
| After a fault loop, `sepc`/`stval` look meaningless | Each new fault overwrites them; you are reading the *last* fault, not the first | Set `b *kernelvec` (or `b *uservec`) early so you stop on fault number one |

Hardware watchpoints (`watch *(unsigned long *) 0x8002b3e0`, after
`set language c`) are accepted by QEMU's stub and report as `hw watchpoint`,
but in this setup they are unreliable enough that you should verify one fires
before you plan around it. A breakpoint on whatever writes the location is
usually faster and always trustworthy.

## See also

- [Sv39 Paging](sv39-paging.md) — PTE bits, `satp`, and five worked translations to check your walks against
- [RISC-V](riscv.md) — every CSR, the `scause` decode table, and the assembly you will be stepping through
- [Memory Map](memory-map.md) — what is at `0x1000`, `0x10_0000`, `0x0c00_0000`, and `0x8000_0000`
- [rv6 Architecture](rv6-architecture.md) — a symptom-to-source table for logic bugs, once you know *where* it broke
- [Dev Setup](dev-setup.md) — installing QEMU and the toolchain
- [Using OSlings](oslings-usage.md) — what the harness runs, and how to reproduce it by hand
