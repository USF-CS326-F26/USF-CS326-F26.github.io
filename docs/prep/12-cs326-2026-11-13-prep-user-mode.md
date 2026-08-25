# Prep: User Mode — 48k

**Session:** Fri Nov 13, 1h30 · **Exercises:** `48k_user_mode` · **Prep time:** ~50 min · **Lecture:** [User Mode I: The Wall, the Trampoline, and the Trapframe](../lectures/12-cs326-2026-11-10-user-mode-i-the-wall-trampoline-and-trapframe.md)

## What you will build

rv6 runs its first user program: a dozen lines of assembly in a private address space with a code page and a stack page it may touch, plus the trampoline and trapframe it cannot. The kernel clears `sstatus.SPP` and executes its first `sret`; the program prints through a system call, asks for its pid, and exits with that pid plus 41. You finish the crossing in both directions. The self-check expects `hello from user mode` on the console and exit status 42 from pid 1.

## Concepts you need

- **U-mode, and the two doors back: `ecall` or a fault** — [User Mode I §2](../lectures/12-cs326-2026-11-10-user-mode-i-the-wall-trampoline-and-trapframe.md#2-the-third-privilege-level) · [User Mode II §1](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#1-two-kinds-of-trap)
- **`PTE_U` is the wall, in both directions** — [User Mode I §3](../lectures/12-cs326-2026-11-10-user-mode-i-the-wall-trampoline-and-trapframe.md#3-the-private-address-space) · [Sv39 Paging § The page-table entry](../guides/sv39-paging.md#the-page-table-entry) · [rv6 Architecture § A user address space](../guides/rv6-architecture.md#a-user-address-space-memlayoutrs29-75-execrs671-687)
- **The trampoline: one page, the same virtual address in every table** — [User Mode I §4](../lectures/12-cs326-2026-11-10-user-mode-i-the-wall-trampoline-and-trapframe.md#4-the-trampoline-problem) · [Sv39 Paging § 5. The trampoline](../guides/sv39-paging.md#5-the-trampoline-0x3f_ffff_f000)
- **The trapframe and `sscratch`** — [User Mode I §5](../lectures/12-cs326-2026-11-10-user-mode-i-the-wall-trampoline-and-trapframe.md#5-the-trapframe) · [User Mode II §2](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#2-the-convention-across-the-wall)
- **The ABI: number in `a7`, result in `a0`** — [User Mode II §2](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#2-the-convention-across-the-wall) · [rv6 Architecture § The system call table](../guides/rv6-architecture.md#the-system-call-table)
- **`sepc += 4`: done versus retry** — [User Mode II §4](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#4-sepc-4-and-the-difference-between-done-and-retry)
- **A user pointer is not a kernel pointer** — [User Mode II §5](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#5-the-security-boundary) · [rv6 Architecture § Path 3](../guides/rv6-architecture.md#path-3-the-user-syscall-round-trip)

## Read before class

| What | Time |
|---|---|
| [User Mode I §2–§5](../lectures/12-cs326-2026-11-10-user-mode-i-the-wall-trampoline-and-trapframe.md#2-the-third-privilege-level) (privilege, address space, trampoline, trapframe) | 20 min |
| [User Mode II §1–§4](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#1-two-kinds-of-trap) (kinds of trap, the convention, the table, the +4) | 15 min |
| [User Mode II §5](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#5-the-security-boundary) | 10 min |
| [rv6 Architecture § Path 3: the user syscall round trip](../guides/rv6-architecture.md#path-3-the-user-syscall-round-trip) | 5 min |

## Mental model

One `getpid()` from a process whose pid is 7, end to end:

```text
user    0x20: li a7, 11 ; 0x24: ecall   # scause = 8, sepc = 0x24 (the ecall itself)
enter   uservec: csrrw a0, sscratch, a0 ; park 31 registers in TRAPFRAME
kernel  tf.epc = 0x24 + 4               # the work is done: never run ecall again
        tf.a0  = 7                      # the answer goes into RAM, not a register
leave   sret aimed at U-mode, sepc = tf.epc
user    0x28: a0 == 7                   # the value spent the whole trip as a u64 in a page
```

Every value that crosses the wall lives in the trapframe for the duration. Forget the +4 and the program makes the same call forever; a page fault is the opposite case: `sepc` stays put, so the load retries.

## Check yourself

1. A program passes `buf = 0x3F_FFFF_E000`, its own trapframe, to `write`. What happens, and which check stops it? <details><summary>Answer</summary>The page is mapped in the user's table, but without `PTE_U`, and `walkaddr` returns 0 for any PTE lacking that bit. The call returns -1; nothing leaks.</details>
2. The saved `epc` is left pointing at the `ecall`. What does the program do, and why is leaving `sepc` alone correct for a page fault? <details><summary>Answer</summary>It re-executes the `ecall` forever. A page fault reports a condition the kernel removes, so re-running the load is the point.</details>
3. The trampoline sits inside the user's address space. Why is it mapped without `PTE_U`, and how does the CPU ever get there? <details><summary>Answer</summary>Only a trap lands there, and a trap raises privilege to S before the first byte is fetched; with `PTE_U`, user code could jump past the `csrw satp` in `userret`.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Monday 11:59 pm** and submit again. Midterm 2 is next Thursday, Nov 19, and covers processes through this exercise.

## If you finish early

Work the [User Mode II Practice Problems](../lectures/13-cs326-2026-11-17-user-mode-ii-system-calls.md#practice-problems) on paper; they match Midterm 2's shape. Then start the next prep page, [Prep: Exec and File Descriptors](15-cs326-2026-12-03-prep-exec-and-file-descriptors.md).
