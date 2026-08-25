# Cheatsheet

**This is the reference you are permitted to bring to the midterm and the
final.** Print it, write on it, bring it in. Every bit position, magic address
and constant rv6 is built from is on this one page, cited to the file and line
in `exercises/22_userland/solution/` so you can check it against the real
kernel. It is not a tutorial — it is what you look at when you cannot remember
whether `PTE_U` is bit 4 or bit 5. For the *why*, see
[Sv39 Paging](sv39-paging.md), [The Memory Map](memory-map.md), and
[rv6 Architecture](rv6-architecture.md).

> **Reading the bit tables.** Bit 0 is the least significant bit (value 1).
> `1 << n` puts a 1 in bit n. One hex digit is 4 bits. Rust's `_` in a number
> is a separator: `0x8000_0000` is `0x80000000`.

## Privilege levels

A trap moves *up* a level; a special return instruction moves *down*.

| Level | Runs there | May do |
|---|---|---|
| **M** machine | `start.rs`, `timervec` | everything; QEMU boots into M |
| **S** supervisor | the rv6 kernel | CSRs, page tables, take traps |
| **U** user | user programs | ordinary computation only |

- **M → S**: set `mstatus.MPP = 01`, `mepc = kmain`, then `mret` (`start.rs:25`).
- **S → U**: set `sstatus.SPP = 0`, `sepc = tf.epc`, then `sret` (`usermode.rs:440`).
- **U/S → up**: any `ecall`, interrupt, or fault enters the handler at `stvec`.

## Registers and the calling convention

| Reg | ABI | Role | Saved by |
|---|---|---|---|
| x0 | zero | always 0 | — |
| x1 | ra | return address | caller |
| x2 | sp | stack pointer | callee |
| x3 | gp | global pointer | — |
| x4 | tp | thread pointer | — |
| x5–x7 | t0–t2 | temporaries | caller |
| x8 | s0/fp | saved / frame pointer | callee |
| x9 | s1 | saved | callee |
| x10–x11 | a0–a1 | args, return values | caller |
| x12–x17 | a2–a7 | args | caller |
| x18–x27 | s2–s11 | saved | callee |
| x28–x31 | t3–t6 | temporaries | caller |

**Callee-saved** (`sp`, `s0`–`s11`) are exactly the 14 words `swtch` saves.
**Caller-saved** (`ra`, `t0`–`t6`, `a0`–`a7`) are the 16 registers `kernelvec`
parks before calling `kerneltrap` (`trap.rs:90`). Program entry after `exec`:
`a0 = argc`, `a1 = argv` (`exec.rs:705`).

## `Context` — what `swtch` saves (`swtch.rs:5`)

Field order *is* the byte offset order; `swtch` hardcodes these offsets.

```text
  0 ra    16 s0   32 s2   48 s4   64 s6   80 s8    96 s10
  8 sp    24 s1   40 s3   56 s5   72 s7   88 s9   104 s11
```

`swtch(old, new)` stores all 14 into `*old` (`a0`), loads all 14 from `*new`
(`a1`), and `ret`s — into the *new* context's `ra` (`swtch.rs:46`).
`init_context` sets `ra = entry`, `sp = stack_top`, so a fresh process "returns"
into its first function.

## `Trapframe` — what `uservec` saves (`usermode.rs:33`)

One page per process, mapped at `TRAPFRAME`; the offsets are hardcoded in the
trampoline assembly.

```text
  0 kernel_satp   40 ra    88 t2   136 a3   184 s3   232 s9    280 t6
  8 kernel_sp     48 sp    96 s0   144 a4   192 s4   240 s10
 16 kernel_trap   56 gp   104 s1   152 a5   200 s5   248 s11
 24 epc           64 tp   112 a0   160 a6   208 s6   256 t3
 32 kernel_hartid 72 t0   120 a1   168 a7   216 s7   264 t4
                  80 t1   128 a2   176 s2   224 s8   272 t5
```

The first five fields are notes the kernel leaves for the trampoline; the rest
are the 31 user registers. `a0` (offset 112) is saved last, because `uservec`
swaps it through `sscratch` first (`usermode.rs:94`).

## Sv39 virtual memory

39-bit addresses, three levels, 4096-byte pages, 512 entries per table.

```text
 38      30 29      21 20      12 11         0
+----------+----------+----------+-----------+
| VPN[2]   | VPN[1]   | VPN[0]   |  offset   |
| 9 bits   | 9 bits   | 9 bits   |  12 bits  |
+----------+----------+----------+-----------+
   L2 index   L1 index   L0 index   byte in page
```

`px(level, va) = (va >> (12 + level*9)) & 0x1ff` (`vm.rs:44`). `walk` uses
VPN[2] on the root table, VPN[1] next, VPN[0] on the leaf (`vm.rs:52`).

### Page table entry (64 bits)

```text
 63    54 53                10 9   8 7 6 5 4 3 2 1 0
+--------+--------------------+-----+-+-+-+-+-+-+-+-+
| unused |   PPN (44 bits)    | RSW |D|A|G|U|X|W|R|V|
+--------+--------------------+-----+-+-+-+-+-+-+-+-+
```

| Bit | Const | Value | Meaning |
|---|---|---|---|
| 0 | `PTE_V` | `1 << 0` | Valid — the entry is in use |
| 1 | `PTE_R` | `1 << 1` | Read allowed |
| 2 | `PTE_W` | `1 << 2` | Write allowed |
| 3 | `PTE_X` | `1 << 3` | eXecute allowed |
| 4 | `PTE_U` | `1 << 4` | User mode may access — the wall |
| 5 | G | `1 << 5` | Global mapping (rv6 never sets it) |
| 6 | A | `1 << 6` | Accessed (hardware sets) |
| 7 | D | `1 << 7` | Dirty (hardware sets) |
| 8–9 | RSW | | reserved for software |
| 10–53 | PPN | | physical page number |

Constants at `vm.rs:17`; helper arithmetic at `vm.rs:29`:
`Pte::new(pa, flags)` = `((pa >> 12) << 10) | flags`, `Pte::pa()` =
`(pte >> 10) << 12`, `Pte::flags()` = `pte & 0x3ff`.

**Leaf vs. interior:** R, W, X all zero and V set means an interior node pointing
at the next table. Any of R/W/X set makes it a leaf (`vm.rs:358`).

**Permissions actually used:** kernel RAM `R|W|X` (`vm.rs:141`); MMIO pages
`R|W` (`vm.rs:132`); trampoline `R|X` and trapframe `R|W`, both without `U`
(`proc.rs:164`); user code `R|X|U` (`vm.rs:228`); user stack `R|W|U`
(`vm.rs:245`).

### `satp` — turning paging on

```text
 63    60 59        44 43              0
+--------+------------+----------------+
| MODE=8 |    ASID    |   root PPN     |
+--------+------------+----------------+
```

`SATP_SV39 = 8 << 60`; `make_satp(root) = SATP_SV39 | (root >> 12)`
(`vm.rs:104`). Install with `csrw satp, x` then `sfence.vma zero, zero`
(`vm.rs:177`). MODE 0 = paging off.

## Constants you must not misremember

| Constant | Value | File |
|---|---|---|
| `PGSIZE` | `4096` = `0x1000` | `memlayout.rs:7` |
| `KERNBASE` | `0x8000_0000` | `memlayout.rs:10` |
| `PHYSTOP` | `0x8800_0000` (KERNBASE + 128 MiB) | `memlayout.rs:13` |
| `PLIC_SIZE` | `0x40_0000` (4 MiB) | `memlayout.rs:27` |
| `MAXVA` | `1 << 38` = `0x40_0000_0000` | `memlayout.rs:49` |
| `TRAMPOLINE` | `MAXVA - PGSIZE` = `0x3F_FFFF_F000` | `memlayout.rs:53` |
| `TRAPFRAME` | `TRAMPOLINE - PGSIZE` = `0x3F_FFFF_E000` | `memlayout.rs:57` |
| `USER_CODE` | `0x0` | `memlayout.rs:61` |
| `MAX_PROG_PAGES` | `16` (64 KiB) | `memlayout.rs:65` |
| `USER_STACK` | `0x1_0000` | `memlayout.rs:72` |
| `USER_STACK_TOP` | `0x1_1000` | `memlayout.rs:75` |
| `NPROC` | `64` | `param.rs:7` |
| `NOFILE` | `16` | `file.rs:19` |
| boot `STACK_SIZE` | `4096 * 4` | `entry.rs:11` |

`MAXVA` is `1 << 38`, one bit short of Sv39's 39, so no rv6 address ever needs
sign extension — a deliberate simplification, not a hardware limit.

## Physical memory map (QEMU `virt`)

| Address | What |
|---|---|
| `0x0000_1000` | boot ROM; QEMU's reset vector jumps to `0x8000_0000` |
| `0x0010_0000` | `TEST_FINISHER` — SiFive test finisher (power off) |
| `0x0200_0000` | CLINT (timer) |
| `0x0c00_0000` | `PLIC`, 4 MiB of registers |
| `0x1000_0000` | `UART0` — NS16550A serial port |
| `0x8000_0000` | `KERNBASE` — RAM starts; the kernel is loaded here |
| `0x8800_0000` | `PHYSTOP` — one past the end of 128 MiB of RAM |

`kalloc`'s free memory runs from `end` (the linker symbol after `.bss`), rounded
up to a page, through `PHYSTOP` (`kalloc.rs:21`). Test finisher: write `0x5555`
to pass, `0x3333 | (code << 16)` to fail (`testdev.rs:13`).

## User address space

| Virtual address | Contents | Perms |
|---|---|---|
| `0x3F_FFFF_F000` `TRAMPOLINE` | `uservec` / `userret` | R X |
| `0x3F_FFFF_E000` `TRAPFRAME` | saved user registers | R W |
| … | unmapped | |
| `0x1_1000` `USER_STACK_TOP` | initial `sp` | |
| `0x1_0000` `USER_STACK` | the one stack page | R W U |
| … | unmapped guard gap | |
| `0x0` `USER_CODE` … | program image, 1–16 pages | R X U |

**argv layout** (`push_argv`, `exec.rs:781`), top down: the argument strings,
8-byte aligned; then `argc + 1` user pointers to them, NULL-terminated and
16-byte aligned. `sp` and `a1` both point at that array; `a0 = argc`.
`MAXARG = 8`, `MAXARGLEN = 32` (`exec.rs:612`).

## `scause` — why a trap happened

Top bit: 1 = interrupt, 0 = exception; low bits say which. rv6 reads
`scause >> 63` and `scause & 0xff` (`trap.rs:55`).

**Interrupts** (`scause >> 63 == 1`):

| Code | Meaning | rv6 |
|---|---|---|
| 1 | supervisor software | the forwarded timer tick (ex14) |
| 5 | supervisor timer | unused; we forward via software instead |
| 7 | machine timer | handled in M-mode by `timervec` |
| 9 | supervisor external | a device via the PLIC (ex15) |

**Exceptions** (`scause >> 63 == 0`):

| Code | Meaning | rv6 |
|---|---|---|
| 1 | instruction access fault | a faulting user program |
| 2 | illegal instruction | a faulting user program |
| 3 | **breakpoint** (`ebreak`) | the ex13 trap test |
| 5, 7 | load / store access fault | fault |
| 8 | **ecall from U-mode** | every system call |
| 9, 11 | ecall from S-mode, M-mode | unused |
| 12, 13, 15 | instruction / load / store page fault | bad memory access |

On any `ecall`, `sepc` points **at** the `ecall`, so the handler must add 4 or
it re-executes forever: `(*tf).epc += 4` (`usermode.rs:401`); same for `ebreak`
(`trap.rs:77`).

## Supervisor CSRs

**`sstatus`:**

| Bit | Name | Meaning |
|---|---|---|
| 1 | SIE | S-mode interrupts enabled now |
| 5 | SPIE | interrupts were enabled before the trap |
| 8 | SPP | previous privilege: 0 = user, 1 = supervisor |

`sret` returns to the SPP level and restores SIE from SPIE. `usertrapret` clears
bit 8 and sets bit 5 before `sret` (`usermode.rs:455`).

**`sie` / `sip`** (enable / pending — same bit layout):

| Bit | Name | Source |
|---|---|---|
| 1 | SSIE / SSIP | software (our forwarded timer tick) |
| 5 | STIE / STIP | timer |
| 9 | SEIE / SEIP | external (PLIC devices) |

`intr_on()` = `csrs sie, 1<<1` plus `csrs sstatus, 1<<1` (`trap.rs:39`); the
console adds `csrs sie, 1<<9` (`console.rs:63`). Clear a pending software
interrupt with `sip &= !2` (`trap.rs:63`) or the tick re-fires forever. Other
S-CSRs: `stvec` (trap vector), `sepc` (trap PC), `scause`, `sscratch` (where
`uservec` parks the trapframe pointer), `satp`.

## Machine CSRs (`start.rs`)

| CSR | Value | Why |
|---|---|---|
| `mstatus.MPP` | `0b01 << 11` | `mret` lands in Supervisor |
| `mepc` | `kmain` | where `mret` jumps |
| `medeleg`, `mideleg` | `0xffff` | delegate all traps to S |
| `pmpaddr0` | `0x3fffffffffffff` | cover all physical memory |
| `pmpcfg0` | `0xf` | R+W+X, A=1 (TOR): S-mode gets it all |
| `mcounteren` | `0xffffffff` | let S-mode read `time` |
| `mtvec` | `timervec` | machine timer vector |
| `mie` | bit 7 (MTIE) | enable the machine timer |

`mstatus.MPP` (bits 12:11): `00` U, `01` S, `11` M. `pmpcfg0` byte: bit 0 R,
bit 1 W, bit 2 X, bits 3–4 A (0 off, 1 TOR, 2 NA4, 3 NAPOT), bit 7 lock.

## CLINT — the timer

Base `0x0200_0000` (`start.rs:17`).

| Register | Address | Meaning |
|---|---|---|
| `mtime` | `0x0200_bff8` | free-running current time |
| `mtimecmp0` | `0x0200_4000` | hart 0's alarm: interrupt when `mtime >= this` |

`INTERVAL = 1_000_000` ticks; the `time` CSR runs at 10 MHz on QEMU `virt`, so
about 0.1 s. `timervec` (M-mode, `start.rs:80`) adds `INTERVAL` to `mtimecmp`,
writes `2` to `sip` to raise SSIP, and `mret`s.

## UART — NS16550A (`uart.rs`)

Base `0x1000_0000`. Every register is one byte at these offsets:

| Off | Read | Write | Name |
|---|---|---|---|
| 0 | RBR | THR | Receive Buffer / Transmit Holding |
| 1 | IER | IER | Interrupt Enable |
| 2 | — | FCR | FIFO Control |
| 3 | LCR | LCR | Line Control |
| 4 | MCR | MCR | Modem Control |
| 5 | LSR | — | Line Status |

**LSR** — poll before touching data: bit 0 `DR` (a byte waits in RBR), bit 5
`THRE` (safe to write THR). `getc` waits for `LSR & 1`; `putc` spins until
`LSR & 0x20`.

| Write | Value | Effect |
|---|---|---|
| `IER` | `0x00` | polling: interrupts off (`uart.rs:28`) |
| `IER` | `0x01` | interrupt when a byte arrives (`uart.rs:37`) |
| `LCR` | `0x03` | 8 data bits, no parity, 1 stop bit |
| `FCR` | `0x07` | enable FIFO + clear Rx FIFO + clear Tx FIFO |
| `MCR` | `1 << 4` | loopback: Tx wired to Rx, for deterministic tests |

The console fills a 256-byte ring buffer from the interrupt handler
(`console.rs:8`).

## PLIC — device interrupt routing

Base `0x0c00_0000`. `UART0_IRQ = 10` (`plic.rs:14`).

| Register | Address | Purpose |
|---|---|---|
| priority | `PLIC + irq*4` | source priority; 0 means disabled |
| S-enable | `PLIC + 0x2080` | bitmask of sources enabled for hart 0 S-mode |
| S-threshold | `PLIC + 0x20_1000` | ignore priorities ≤ this |
| S-claim/complete | `PLIC + 0x20_1004` | read = claim, write = complete |

`init` writes priority 1 to `PLIC + 40`, `1 << 10` to S-enable, 0 to the
threshold (`plic.rs:22`). On an interrupt: `claim()` gives the IRQ (0 = none),
handle it, then `complete(irq)` — skip that and it re-fires forever.

## System calls

`ecall` in U-mode → `scause == 8` → `usertrap` → `syscall::dispatch`.

| Register | Role |
|---|---|
| a7 | which call |
| a0, a1, a2 | arguments |
| a0 (on return) | return value; `-1` = error |

Numbers match xv6 (`syscall.rs:21`):

| # | Call | Signature |
|---|---|---|
| 1 | `fork` | `() -> child pid (parent) / 0 (child)` |
| 2 | `exit` | `(status) -> !` |
| 3 | `wait` | `(&status) -> pid` |
| 5 | `read` | `(fd, buf, len) -> bytes read` |
| 7 | `exec` | `(path, argv)`: no return on success, `-1` on failure |
| 11 | `getpid` | `() -> pid` |
| 15 | `open` | `(path, flags) -> fd` |
| 16 | `write` | `(fd, buf, len) -> bytes written` |
| 21 | `close` | `(fd) -> 0` |

The gaps (4, 6, 8–10, 12–14, 17–20) are xv6 calls rv6 does not implement;
`dispatch` returns `-1` for any unknown number. A successful `exec` never
returns — the caller's code was just freed; the process resumes as the new
program with `a0 = argc`. Open fds survive `exec`, which is how a redirected
stdout persists.

**User pointers.** A `buf` or `path` argument is a *user* virtual address, and a
syscall runs on the *kernel* page table — never dereference it directly. Use
`copyin`, `copyout`, or `copyinstr` (NUL-terminated), all at `vm.rs:268`.

## File descriptors and open flags

An fd indexes `Proc::ofile`, size `NOFILE = 16`; fds 0 (stdin), 1 (stdout) and
2 (stderr) start open on the console (`proc.rs:128`). A `File` (`file.rs:40`) is
`{ kind, inum, off, readable, writable }`; `kind` is `None` / `Console` /
`Inode`, and `off` is the read/write cursor that makes an fd remember its
place.

| Flag | Value | Meaning |
|---|---|---|
| `O_RDONLY` | `0x000` | read only (the default) |
| `O_WRONLY` | `0x001` | write only |
| `O_RDWR` | `0x002` | read and write |
| `O_CREATE` | `0x200` | create the file if missing |
| `O_TRUNC` | `0x400` | truncate to zero length on open |

Access mode: `writable = flags & O_WRONLY != 0 || flags & O_RDWR != 0`;
`readable = flags & O_WRONLY == 0`.

## Filesystem constants (`fs.rs:5`)

| Constant | Value | Meaning |
|---|---|---|
| `ROOT` | `1` | inode number of `/` |
| `NINODE` | `64` | inodes |
| `NDIRENT` | `16` | entries per directory |
| `NAMELEN` | `14` | filename bytes |
| `FILESIZE` | `128` | bytes per file |

## Processes

`ProcState` (`proc.rs:19`): `Unused` → `Runnable` → `Running` → `Sleeping` /
`Zombie`. A **Zombie** has exited but not been reaped; it holds `xstate` until a
parent's `wait` frees the slot.

`Proc` (`proc.rs:27`): `state`, `pid`, `pagetable`, `context`, `trapframe`,
`kstack`, `ofile[NOFILE]`, `parent`, `xstate`, `name[16]`. The kernel stack is
one page, so `sp` starts at `kstack + PGSIZE`.

The scheduler (`usermode.rs:278`) reads every slot's state, calls `pick_next`
(`RoundRobin`), marks the winner `Running`, and `swtch`es in; it regains control
when that process yields (`proc_yield`) or exits (`exit_current`). rv6's
scheduler is **cooperative** — nothing preempts a running process.

## The QEMU command line

```bash
qemu-system-riscv64 -machine virt -bios none -m 128M -smp 1 \
  -nographic -serial mon:stdio -kernel <elf>
```

Target `riscv64gc-unknown-none-elf`, one hart, no firmware — `-bios none` is why
QEMU jumps straight to your `_entry` at `0x8000_0000`. The course uses
`qemu-system-riscv64` only, never `qemu-riscv64` (Linux user-mode emulation,
which does not exist on macOS). See [QEMU and GDB](qemu-gdb.md) for debugging
and [Exam Prep](exam-prep.md) for what to study.
