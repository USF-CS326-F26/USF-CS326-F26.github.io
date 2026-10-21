---
hide:
  - toc
---

# Round Robin, by the Cursor

**Exercise:** `36k_scheduling` · **Fri Oct 23** · **Length:** 4:56 · **Lecture:** [Week 9 · Round robin, by its rules](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#36k-round-robin) · **Explainer:** [Round Robin, by the Cursor](https://claude.ai/artifact/VxxxuK5B3AEeHFCZdZGfFL)

A narrated walk through the explainer, for after the Oct 13 lecture and before
Friday's session: scheduling as a mechanism and a policy, and the one field
the round-robin policy keeps between calls, its cursor. The process table is
drawn as a ring, and each call is a walk from the cursor: past every slot that
is not `Runnable`, around the end of the table, to the slot it returns. Two
broken cases follow, with what the test printed for each in a real run: one
that never wraps and one that begins every walk at slot 0. Then a lap with
nothing to run. The video ends on what the test checks and how to read the
line it prints. It shows no solution code: only the table and the cursor
around each call, with numbers that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week09-round-robin.mp4" type="video/mp4">
  <track kind="captions" src="../week09-round-robin.vtt" srclang="en" label="English" default>
</video>

[Download the video](week09-round-robin.mp4){ download="week09-round-robin.mp4" } (MP4, 13 MB) · [Captions](week09-round-robin.vtt) (WebVTT) · [All four Week 9 videos](week09.md)
