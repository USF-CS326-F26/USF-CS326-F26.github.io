# Prep: Turning the MMU On — 39k

**Session:** Fri Oct 30, 1h30 · **Exercises:** `39k_virtual_memory` · **Prep time:** ~20 min · **Lecture:** [Week 10 · Locks, Semaphores, and Turning the MMU On](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md)

## What you will build

The kernel's address space, handed to the hardware. Using `mappages` from `33k_paging`, you will identity-map everything the kernel touches after the switch: the UART page, the test-finisher page, and all of RAM from `KERNBASE` to `PHYSTOP`, page tables included. You will also pack the `satp` value that names the root table, for the given `csrw satp` and `sfence.vma` sequence. With the MMU still off, the harness walks each region to confirm it is present, identity-mapped, and correctly permissioned, checks that `satp` carries MODE 8 and the root's page number, then flips the switch and prints `OSLINGS:PASS`.

## Concepts you need

- **The bootstrap paradox: the fetch after `csrw satp` is translated** — [Week 10 · The next fetch is translated](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-paradox)
- **Identity mapping, `va == pa`** — [Week 10 · The next fetch is translated](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-paradox)
- **If the kernel will touch it, map it; the third argument is a size** — [Week 10 · The next fetch is translated](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-paradox) · [Sv39 Paging guide: The kernel page table on a fresh boot](../guides/sv39-paging.md#the-kernel-page-table-on-a-fresh-boot)
- **`satp`: MODE 8, ASID 0, root PPN; machine mode ignores it** — [Week 10 · `satp` by hand](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-satp), [Silence, and checking first](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-verify) · [Sv39 Paging guide: The `satp` register](../guides/sv39-paging.md#the-satp-register)
- **The TLB is not coherent; `sfence.vma` invalidates and orders** — [Week 10 · Two instructions, and the TLB](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-tlb) · [Sv39 Paging guide: `sfence.vma` and the TLB](../guides/sv39-paging.md#sfencevma-and-the-tlb)
- **Silence is the default failure; read `satp`, `pc`, `scause`, `stval` in GDB** — [Week 10 · Silence, and checking first](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-verify), [Reading the silence](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#deeper-silence) · [QEMU and GDB guide: Diagnostic playbook](../guides/qemu-gdb.md#diagnostic-playbook)

## Read before class

| What | Time |
|---|---|
| [Week 10 · Friday · `39k` Turning the MMU on](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#fri-39k) through [`satp` by hand](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-satp), with its recap of `33k` | 3 min |
| [Week 10 · Two instructions, and the TLB](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-tlb) and [Silence, and checking first](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-verify) | 3 min |
| [Week 10 · For the exam: Megapages, and 66 pages](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-megapages). Not needed today; on Midterm 2 | 1 min |
| [Sv39 Paging guide: The `satp` register](../guides/sv39-paging.md#the-satp-register) and [`sfence.vma` and the TLB](../guides/sv39-paging.md#sfencevma-and-the-tlb) | 4 min |
| [QEMU and GDB guide: Diagnostic playbook](../guides/qemu-gdb.md#diagnostic-playbook), the "It worked until I turned the MMU on" and "QEMU hangs" rows | 2 min |

## Mental model

A toy kernel, root table at `0x8700_0000`, next instruction at `0x8000_1234`:

```text
satp = (8 << 60) | (0x8700_0000 >> 12)
     = 0x8000_0000_0008_7000

csrw satp, t0          executes with translation OFF
fetch 0x8000_1234      translation ON: root[2] -> L1[0] -> L0[1]
                       leaf needs V=1, X=1, PPN<<12 == 0x8000_1000
sfence.vma zero, zero  runs only if that fetch succeeded
```

Nothing in RAM moved; the meaning of every register changed between two adjacent instructions. Under an identity map `0x8000_1234` translates to itself and the kernel does not notice. If that leaf is missing, the fetch faults, `stvec` is still zero, and the machine loops silently at address 0, because printing itself needs a fetch, a stack store, and the UART page. That is why the harness verifies with `walk` first, and why a silent kernel means `p/x $satp` in GDB, not another print.

## Check yourself

1. GDB shows `satp = 0x8000_0000_0008_7FFF`. Is paging on, and where is the root table? <details><summary>Answer</summary>Top nibble 8 is Sv39, so yes; ASID 0. PPN `0x87FFF` shifted left by 12 puts the root at `0x87FF_F000`, the highest page in RAM and the allocator's first.</details>
2. Your kernel survives the switch, prints `OSLINGS:PASS`, then QEMU never exits and `oslings` waits out its 10-second timeout. Which region is missing? <details><summary>Answer</summary>The test-finisher page at `0x10_0000`. Text and the UART must be mapped, since it ran and printed; the exit store is the first access outside them. `oslings` saw PASS, so the run still goes green: the wait is the only symptom. (In `39k` itself, which runs in machine mode, the check before the switch reports a missing region as a `[fail]` line instead.)</details>
3. Right after the switch, `scause` reads 1, not 12. Do you suspect a mapping or `satp`? <details><summary>Answer</summary>`satp`. A page fault (12) means your table refused the fetch; an access fault (1) means the hardware could not even read a PTE, classically a PPN field holding the root's address unshifted. On QEMU 10, though, that unshifted root reports 12 too, so read `satp` before blaming a mapping.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 10 · Problem 4: `satp` both ways](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#problem-4) and [Problem 5: Count the tables](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#problem-5) on paper, read [Week 10 · How xv6 and Linux do it](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#deeper-others) beside xv6 book sections 3.3–3.4, or start next Thursday's prep page, [Prep: Filesystem](11-cs326-2026-11-05-prep-filesystem.md).
