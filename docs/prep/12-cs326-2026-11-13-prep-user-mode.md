# Prep: User Mode — 48k

**Session:** Fri Nov 13, 1h30 · **Exercises:** `48k_user_mode` · **Prep time:** ~25 min · **Lecture:** [Week 12 · The Console, the Shell, and User Mode](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md)

## What you will build

rv6 runs its first user program: a dozen lines of assembly in a private address space with a code page and a stack page it may touch, plus the trampoline and trapframe it cannot. The kernel clears `sstatus.SPP` and executes its first `sret`; the program prints through a system call, asks for its pid, and exits with that pid plus 41. You finish the crossing in both directions. The self-check expects `hello from user mode` on the console and exit status 42 from pid 1.

## Concepts you need

- **U-mode, and the ways back: an `ecall`, an interrupt, or a fault** — [Week 12 · Why a wall, and what user mode may not do](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-wall)
- **`PTE_U` is the wall, in both directions** — [Week 12 · A private address space](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-address-space) · [Sv39 Paging guide: The page-table entry](../guides/sv39-paging.md#the-page-table-entry) · [rv6 Architecture: A user address space](../guides/rv6-architecture.md#a-user-address-space-memlayoutrs-build_addrspace-in-execrs) (its layout is `49k`'s)
- **The trampoline: one page, the same virtual address in every table** — [Week 12 · The trampoline](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-trampoline), [Two pages at the top](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#exam-top-pages) · [Sv39 Paging guide: The trampoline](../guides/sv39-paging.md#5-the-trampoline-0x3f_ffff_f000)
- **The trapframe and `sscratch`** — [Week 12 · The trapframe, and why not the user's stack](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-trapframe), [`sscratch`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#exam-sscratch)
- **The ABI: number in `a7`, result in `a0`** — [Week 12 · The system-call ABI](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-abi) · [rv6 Architecture: The system call table](../guides/rv6-architecture.md#the-system-call-table)
- **Done versus retry: the +4 after a finished `ecall`** — [Week 12 · Done versus retry](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-retry)
- **A user pointer is not a kernel pointer** — [Week 12 · One program, end to end](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-round-trip) · [rv6 Architecture: Path 3, the user syscall round trip](../guides/rv6-architecture.md#path-3-the-user-syscall-round-trip)

## Read before class

| What | Time |
|---|---|
| [Week 12 · Friday · `48k` User mode](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#fri-48k) through [A private address space](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-address-space) | 3 min |
| [Week 12 · The trapframe, and why not the user's stack](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-trapframe) and [The trampoline](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-trampoline) | 3 min |
| [Week 12 · The system-call ABI](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-abi) and [Done versus retry](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-retry) | 3 min |
| [Week 12 · One program, end to end](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-round-trip), with its sequence diagram | 3 min |
| [Week 12 · For the exam: Two pages at the top](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#exam-top-pages) and [`sscratch`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#exam-sscratch). Not needed today; on Midterm 2 | 2 min |
| [rv6 Architecture: Path 3, the user syscall round trip](../guides/rv6-architecture.md#path-3-the-user-syscall-round-trip) | 5 min |

## Mental model

One `getpid()` from a process whose pid is 7, end to end:

```text
user    0x20: li a7, 11 ; 0x24: ecall   # scause = 8, sepc = 0x24 (the ecall itself)
enter   uservec: csrrw a0, sscratch, a0 ; park 31 registers in TRAPFRAME
kernel  saved pc: 0x24 -> 0x28          # the work is done: never run ecall again
        saved a0: 7                     # the answer goes into RAM, not a register
leave   sret aimed at U-mode, at the saved pc
user    0x28: a0 == 7                   # the value spent the whole trip as a u64 in a page
```

Every value that crosses the wall lives in the trapframe for the duration. Forget the +4 and the program makes the same call forever; a page fault is the opposite case: `sepc` stays put, so the load retries once a kernel maps the page (rv6 maps nothing on demand, so it ends the program).

## Check yourself

1. A program passes `buf = 0x3F_FFFF_E000`, its own trapframe, to `write`. What happens, and which check stops it? <details><summary>Answer</summary>The page is mapped in the user's table, but without `PTE_U`, and `walkaddr` returns 0 for any PTE lacking that bit. The call returns -1; nothing leaks.</details>
2. The saved `epc` is left pointing at the `ecall`. What does the program do, and why is leaving `sepc` alone correct for a page fault? <details><summary>Answer</summary>It re-executes the `ecall` forever. A page fault reports a condition a kernel can remove by mapping the page, so re-running the load is the point; rv6 maps nothing on demand, so it ends the program instead.</details>
3. The trampoline sits inside the user's address space. Why is it mapped without `PTE_U`, and how does the CPU ever get there? <details><summary>Answer</summary>Only a trap lands there, and a trap raises privilege to S before the first byte is fetched. `PTE_U` would break that very path: S-mode never executes code from a U page, so the first trap would fault in `uservec`.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again. Midterm 2 is next Thursday, Nov 19, and covers processes through this exercise.

## If you finish early

Work [Week 12 · Problem 3: The two top pages](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#problem-3) and [Problem 4: Where does the program resume?](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#problem-4) on paper; they match Midterm 2's shape. Then start the next prep page, [Prep: Exec and File Descriptors](15-cs326-2026-12-03-prep-exec-and-file-descriptors.md).
