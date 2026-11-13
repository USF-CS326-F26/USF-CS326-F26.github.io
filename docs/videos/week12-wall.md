---
hide:
  - toc
---

# One Bit Is the Wall

**Exercise:** `48k_user_mode` · **Fri Nov 13** · **Length:** 5:56 · **Lecture:** [Week 12 · A private address space](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-address-space) · **Explainer:** [One Bit Is the Wall](https://claude.ai/artifact/D7rgr68HdWzKV2cADtnAg2)

A narrated walk through the explainer, for after the Nov 10 lecture and before
Friday's session: privilege decides which instructions may run, and the page
table decides which addresses exist; one bit in each leaf, U, decides whether
user mode may touch that page. The video reads an example process's own table,
its four leaves and the V and U bits of each, then steps through the given trip
down into user mode, through `usertrapret`, `userret` and `sret`, and through
the example program's first fetches and its first store, each checked against
the leaf it reaches. Two broken cases follow, each a leaf without U, with the
line the test prints for it: code without U, whose first fetch faults, and
stack without U, whose store fault is the stepper's picture, not a recording.
The video ends on what you write, the test's checks, and how to read the line
it prints. It shows no solution code: only the leaves, the mode, the control
registers and the pc at each step, with example addresses.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week12-wall.mp4" type="video/mp4">
  <track kind="captions" src="../week12-wall.vtt" srclang="en" label="English" default>
</video>

[Download the video](week12-wall.mp4){ download="week12-wall.mp4" } (MP4, 8 MB) · [Captions](week12-wall.vtt) (WebVTT) · [All six Week 12 videos](week12.md)
