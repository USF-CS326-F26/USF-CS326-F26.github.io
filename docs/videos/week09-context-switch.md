---
hide:
  - toc
---

# Save Here, Load There

**Exercise:** `35k_context_switch` · **Fri Oct 23** · **Length:** 5:14 · **Lecture:** [Week 9 · Friday · `35k` The context switch](../lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling.md#fri-35k) · **Explainer:** [Save Here, Load There](https://claude.ai/artifact/6egDZD6t2RrmoDoen2YuaJ)

A narrated walk through the explainer, for after the Oct 13 lecture and before
Friday's session: a context as fourteen words of 8 bytes, and why those
registers; then the context forged for a task that has never run, on the page
it will run on. One switch into the task and one back follow, step by step:
what the given save half keeps, what the registers hold once your half has
run, and where `ret` lands. Two broken cases follow, with what the test
printed for each in a real run: one with `sp` not loaded, which prints its ok
line and then hangs, and one with `ra` and `sp` swapped. The video ends on how
to read what the test prints, a timeout included. It shows no solution code:
only the machine's state and the test's output, with addresses that are
examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week09-context-switch.mp4" type="video/mp4">
  <track kind="captions" src="../week09-context-switch.vtt" srclang="en" label="English" default>
</video>

[Download the video](week09-context-switch.mp4){ download="week09-context-switch.mp4" } (MP4, 16 MB) · [Captions](week09-context-switch.vtt) (WebVTT) · [All four Week 9 videos](week09.md)
