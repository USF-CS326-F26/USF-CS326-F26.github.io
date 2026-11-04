---
hide:
  - toc
---

# Three Gates and a Pending Bit

**Exercise:** `44k_interrupts` · **Fri Nov 6** · **Length:** 5:33 · **Lecture:** [Week 11 · Three gates and a pending bit](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#44k-gates) · **Explainer:** [Three Gates and a Pending Bit](https://claude.ai/artifact/TUYjAEYqa8g7VbRJKFk5mr)

A narrated walk through the explainer, for after the Nov 3 lecture and before
Friday's session: the timer speaks only to machine mode, so each tick takes a
detour; the kernel takes it only while three gates are open, and it stays
pending until the handler lowers it. The video follows a tick's detour through
`timervec`, reads `scause` top bit first, then steps through two ticks of the
given test: `mtime` and `mtimecmp`, the three gates, and the count. Two broken
cases follow, with what the test printed in real runs: the untouched skeleton,
and a pending bit never lowered. The video ends on the test's outcomes and what
the test cannot see. It shows no solution code: only the clock, the gates and
the trap registers at each step, with example numbers.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week11-three-gates.mp4" type="video/mp4">
  <track kind="captions" src="../week11-three-gates.vtt" srclang="en" label="English" default>
</video>

[Download the video](week11-three-gates.mp4){ download="week11-three-gates.mp4" } (MP4, 11 MB) · [Captions](week11-three-gates.vtt) (WebVTT) · [All five Week 11 videos](week11.md)
