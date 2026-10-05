---
hide:
  - toc
---

# Sv39, Field by Field

**Exercise:** `33k_paging` · **Fri Oct 9** · **Length:** 4:28 · **Lecture:** [Week 7 · The page-table entry](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#33k-pte) · **Explainer:** [Sv39, Field by Field](https://claude.ai/artifact/Fnb8VPHZPKGMqBR9LX2wP3)

A narrated walk through the explainer, for before Tuesday's lecture and before
Friday's session: a virtual address as four fields, a page-table entry as a
page number and flags, and the same page number at bit 12 in an address and at
bit 10 in an entry. The stepper carries it in both directions, then reads it
once from the wrong bit. The video goes on to how an entry's flags make it a
branch or a leaf, and ends on the two lines check 0 can print. It shows no
solution code: only where each field sits before and after a step, with values
that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week07-sv39-fields.mp4" type="video/mp4">
  <track kind="captions" src="../week07-sv39-fields.vtt" srclang="en" label="English" default>
</video>

[Download the video](week07-sv39-fields.mp4){ download="week07-sv39-fields.mp4" } (MP4, 10 MB) · [Captions](week07-sv39-fields.vtt) (WebVTT) · [All four Week 7 videos](week07.md)
