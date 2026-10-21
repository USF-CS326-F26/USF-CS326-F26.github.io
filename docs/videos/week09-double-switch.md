---
hide:
  - toc
---

# The Double Switch

**Exercise:** `36k_scheduling` · **Fri Oct 23** · **Length:** 5:04 · **Lecture:** [Week 9 · The double switch](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#36k-double-switch) · **Explainer:** [The Double Switch](https://claude.ai/artifact/WZFaf1My4MZTrudwutMTEy)

A narrated walk through the explainer, for after the Oct 13 lecture and before
Friday's session: a context in each slot of the process table, and the
scheduler's own, `SCHED_CTX`. Three example processes take turns through the
given scheduler loop and `task`: the scheduler switches into one, the process
writes its pid in the run log and switches back, and the scheduler resumes at
the same point every time. A turn is two switches, and none goes from process
to process. Then a slot whose context was never set up, and what happens if the
policy picks it. The video ends on how to read the lines the test prints. It
shows no solution code: only what the machine holds at each switch, with
addresses that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week09-double-switch.mp4" type="video/mp4">
  <track kind="captions" src="../week09-double-switch.vtt" srclang="en" label="English" default>
</video>

[Download the video](week09-double-switch.mp4){ download="week09-double-switch.mp4" } (MP4, 15 MB) · [Captions](week09-double-switch.vtt) (WebVTT) · [All four Week 9 videos](week09.md)
