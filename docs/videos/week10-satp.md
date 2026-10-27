---
hide:
  - toc
---

# Packing satp

**Exercise:** `39k_virtual_memory` · **Fri Oct 30** · **Length:** 5:25 · **Lecture:** [Week 10 · `satp` by hand](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-satp) · **Explainer:** [Packing satp](https://claude.ai/artifact/4Kx6PtPXmr9tegvpH7VUyz)

A narrated walk through the explainer, for after the Oct 27 lecture and before
Friday's session: one register, `satp`, names the whole page table. The video
builds a `satp` value from a root table's address, field by field, for two
example roots, then shows the test's two checks of that value. Two broken cases
follow, with what the test printed for each in a real run: the mode left out,
and the address left unshifted. Then the two given instructions that install
the value, and the TLB from `43k` on. It shows no solution code: only the
register's bits, with numbers that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week10-satp.mp4" type="video/mp4">
  <track kind="captions" src="../week10-satp.vtt" srclang="en" label="English" default>
</video>

[Download the video](week10-satp.mp4){ download="week10-satp.mp4" } (MP4, 12 MB) · [Captions](week10-satp.vtt) (WebVTT) · [All five Week 10 videos](week10.md)
