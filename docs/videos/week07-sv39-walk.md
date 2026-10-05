---
hide:
  - toc
---

# Sv39, Level by Level

**Exercise:** `33k_paging` · **Fri Oct 9** · **Length:** 5:45 · **Lecture:** [Week 7 · The walk](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#33k-walk) · **Explainer:** [Sv39, Level by Level](https://claude.ai/artifact/PGDBiEroHNUFMc9BqeucV9)

A narrated walk through the explainer, for before Tuesday's lecture and before
Friday's session: page tables are ordinary pages, each read as 512 slots; three
lookups from the root find one address's page, and a second address stops at an
empty slot, not mapped. Then a mapping under a bare root: for each missing
table a page is taken, zeroed, and only then linked in. Two pictures show why a
page is not a table until it is zeroed, and the video ends on what `walk` is
given and hands back, and how to read the line a failed check prints. It shows
no solution code: only what the tables hold at each step, with numbers that are
examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week07-sv39-walk.mp4" type="video/mp4">
  <track kind="captions" src="../week07-sv39-walk.vtt" srclang="en" label="English" default>
</video>

[Download the video](week07-sv39-walk.mp4){ download="week07-sv39-walk.mp4" } (MP4, 15 MB) · [Captions](week07-sv39-walk.vtt) (WebVTT) · [All four Week 7 videos](week07.md)
