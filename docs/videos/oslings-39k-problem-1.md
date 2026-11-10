---
hide:
  - toc
---

# OSlings Practice 39k, Problem 1: Turning on Virtual Memory

**OSlings Practice 39k**, its one problem · **Length:** 9:34 · **Exercise:** `39k_virtual_memory` (Week 10) · **Problems:** [39k](../assignments/oslings-39k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-39k-solutions.pdf) (PDF)

Three parts, worked on all four of the set's pages: (a) what `make_satp` returns for a root page table at `0x87fff000`, what its MODE and PPN fields hold, and why the address is shifted right by 12; (b) (i) the `px` index at each level for the device pages `UART0` and `TEST_FINISHER`, and (ii) whether `walk` allocates a new level-1 or level-0 table while mapping `TEST_FINISHER` right after `UART0`; (c) two addresses translated with `kvmmake`'s table, and why the kernel will keep running normally once its addresses are translated. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-39k-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-39k-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-39k-problem-1.mp4){ download="oslings-39k-problem-1.mp4" } (MP4, 22 MB) · [Captions](oslings-39k-problem-1.vtt) (WebVTT) · [The set](../assignments/oslings-practice.md#39k)
