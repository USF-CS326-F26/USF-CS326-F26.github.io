---
hide:
  - toc
---

# The Identity Map

**Exercise:** `39k_virtual_memory` · **Fri Oct 30** · **Length:** 5:50 · **Lecture:** [Week 10 · The next fetch is translated](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#39k-paradox) · **Explainer:** [The Identity Map](https://claude.ai/artifact/KyhnBTLZ8d97SXBw7Jwqd8)

A narrated walk through the explainer, for after the Oct 27 lecture and before
Friday's session: the kernel's page table maps every page the kernel touches to
itself. The video walks the given test's four probes through an example table,
level by level, and checks each leaf as the test does. Two broken cases follow,
with what the test printed for each in a real run: RAM without X, and RAM one
page long. Then why the test checks the table first: `39k` runs in machine
mode, and from `43k` on the fetch after the switch goes through the table. It
shows no solution code: only the table's entries along each walk, with numbers
that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week10-identity-map.mp4" type="video/mp4">
  <track kind="captions" src="../week10-identity-map.vtt" srclang="en" label="English" default>
</video>

[Download the video](week10-identity-map.mp4){ download="week10-identity-map.mp4" } (MP4, 15 MB) · [Captions](week10-identity-map.vtt) (WebVTT) · [All five Week 10 videos](week10.md)
