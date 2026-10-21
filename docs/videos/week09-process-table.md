---
hide:
  - toc
---

# The Process Table

**Exercise:** `34k_processes` · **Thu Oct 22** · **Length:** 5:11 · **Lecture:** [Week 9 · Thursday · `34k` Processes](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#thu-34k) · **Explainer:** [The Process Table](https://claude.ai/artifact/2facgHTFnageeBWSvgYVPY)

A narrated walk through the explainer, for after the Oct 13 lecture and before
Thursday's session: a process as one record, a `Proc`, and a table of 64 slots
that holds them, with `NEXTPID` outside it. A run of claims and give-backs
follows: a claim takes the first `Unused` slot, a new pid and one page, and a
give-back leaves the slot reading `Unused` only once it owns nothing. A slot
is reused, but a pid never is, and a page goes with a process, not a slot. Two
broken cases follow, with what the test printed for each in a real run: one
that always claims slot 0 and one that never sets the slot back to `Unused`.
Then a full table and the claim it refuses. The video ends on what the test
checks and what it cannot see. It shows no solution code: only what the table
holds after each step, with numbers that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week09-process-table.mp4" type="video/mp4">
  <track kind="captions" src="../week09-process-table.vtt" srclang="en" label="English" default>
</video>

[Download the video](week09-process-table.mp4){ download="week09-process-table.mp4" } (MP4, 14 MB) · [Captions](week09-process-table.vtt) (WebVTT) · [All four Week 9 videos](week09.md)
