# Prep: Turning the MMU On — 39k

**Session:** Fri Oct 30, 1h30 · **Exercises:** `39k_virtual_memory` · **Prep time:** ~45 min · **Lecture:** [Virtual Memory II: Turning the MMU On](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md)

## What you will build

The kernel's address space, handed to the hardware. Using `mappages` from `33k_paging`, you will identity-map everything the kernel touches after the switch: the UART page, the test-finisher page, and all of RAM from `KERNBASE` to `PHYSTOP`, page tables included. You will also pack the `satp` value that names the root table, for the given `csrw satp` and `sfence.vma` sequence. With the MMU still off, the harness walks each region to confirm it is present, identity-mapped, and correctly permissioned, checks that `satp` carries MODE 8 and the root's page number, then flips the switch and prints `OSLINGS:PASS`.

## Concepts you need

- **The bootstrap paradox: the fetch after `csrw satp` is translated** — [Virtual Memory II §1.1](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#11-the-paradox-stated-plainly), [§1.2](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#12-why-there-is-no-one-to-catch-you)
- **Identity mapping, `va == pa`, and what it is not** — [Virtual Memory II §1.3](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#13-identity-mapping), [§1.4](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#14-three-things-identity-mapping-is-not)
- **If the kernel will touch it, map it; the third argument is a size** — [Virtual Memory II §2.1](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#21-the-rule), [§2.3](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#23-ram-in-one-call) · [Sv39 Paging § The kernel page table on a fresh boot](../guides/sv39-paging.md#the-kernel-page-table-on-a-fresh-boot)
- **`satp`: MODE 8, ASID 0, root PPN; machine mode ignores it** — [Virtual Memory II §3.1](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#31-the-encoding), [§3.4](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#34-the-genuinely-confusing-part-machine-mode) · [Sv39 Paging § The satp register](../guides/sv39-paging.md#the-satp-register)
- **The TLB is not coherent; `sfence.vma` invalidates and orders** — [Virtual Memory II §4.2](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#42-the-tlb-is-not-coherent-with-memory), [§4.3](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#43-when-you-must-flush) · [Sv39 Paging § sfence.vma and the TLB](../guides/sv39-paging.md#sfencevma-and-the-tlb)
- **Silence is the default failure; read `satp`, `pc`, `scause`, `stval` in GDB** — [Virtual Memory II §5.1](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#51-why-silence-is-the-default-answer), [§5.4](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#54-reading-the-silence) · [QEMU and GDB § Diagnostic playbook](../guides/qemu-gdb.md#diagnostic-playbook)

## Read before class

| What | Time |
|---|---|
| Virtual Memory II §1 | 10 min |
| Virtual Memory II §2.1–§2.3, §2.5 | 10 min |
| Virtual Memory II §3.1, §3.3–§3.4, §4.2–§4.3 | 10 min |
| Virtual Memory II §5.1–§5.2, §5.4 | 5 min |
| Sv39 Paging guide: The satp register; sfence.vma and the TLB | 5 min |
| QEMU and GDB guide: Diagnostic playbook | 5 min |

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
2. Your kernel survives the switch, prints `OSLINGS:PASS`, then QEMU never exits and the harness times out. Which region is missing? <details><summary>Answer</summary>The test-finisher page at `0x10_0000`. Text and the UART must be mapped, since it ran and printed; the exit store is the first access outside them.</details>
3. Right after the switch, `scause` reads 1, not 12. Do you suspect a mapping or `satp`? <details><summary>Answer</summary>`satp`. A page fault (12) means your table refused the fetch; an access fault (1) means the hardware could not even read a PTE, classically a PPN field holding the root's address unshifted.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish it at a make-up session — office hours, on the class network — before the next session, and submit again.

## If you finish early

Work the lecture's [Practice Problems](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#practice-problems), read [§6 How Others Do It](../lectures/10-cs326-2026-10-27-virtual-memory-ii-turning-the-mmu-on.md#6-how-others-do-it) beside xv6 book sections 3.3–3.4, or start next Thursday's prep page, [Prep: Filesystem](11-cs326-2026-11-05-prep-filesystem.md).
