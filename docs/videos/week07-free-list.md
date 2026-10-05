---
hide:
  - toc
---

# The Free List

**Exercise:** `32k_physical_memory` · **Thu Oct 8** · **Length:** 4:47 · **Lecture:** [Week 7 · Thursday · `32k` The free list](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#thu-32k) · **Explainer:** [The Free List](https://claude.ai/artifact/27NDxWWruWL9fM7HsicED7)

A narrated walk through the explainer, for before Tuesday's lecture and before
Thursday's session: RAM in pages, and `end` rounded up to the next page
boundary; a list that lives in its own free pages, with a head outside them and
a link in each page's first 8 bytes; then allocations and frees on a toy pool
of six pages, each shown as the words it changes, and the LIFO order that
results. One broken free moves the head first, and the video ends on the
self-test's five checks and how to read the line a failed one prints. It shows
no solution code: only what memory holds after each step, with numbers that are
examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week07-free-list.mp4" type="video/mp4">
  <track kind="captions" src="../week07-free-list.vtt" srclang="en" label="English" default>
</video>

[Download the video](week07-free-list.mp4){ download="week07-free-list.mp4" } (MP4, 11 MB) · [Captions](week07-free-list.vtt) (WebVTT) · [All four Week 7 videos](week07.md)
