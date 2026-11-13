---
hide:
  - toc
---

# Step Past the Breakpoint

**Exercise:** `43k_traps` · **Fri Nov 6** · **Length:** 5:32 · **Lecture:** [Week 11 · Re-run or step past](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#43k-sepc) · **Explainer:** [Step Past the Breakpoint](https://claude.ai/artifact/1DoaeiwFVGQfNmPjucggQz)

A narrated walk through the explainer, for after the Nov 3 lecture and before
Friday's session: a trap is the hardware's jump into the kernel; it saves
almost nothing, and `sret` goes back to the address it saved. The video follows
the given handoff from machine mode down to supervisor mode, then steps through
the test's one breakpoint: what the hardware writes, the given vector's
128-byte frame, the handler, and `sret`. A broken case follows, `sepc` left
where it was, with what the test printed in a real run. The video ends on where
`sret` resumes, what reading and writing a control register does to its bits,
and the test's two checks. It shows no solution code: only the trap registers,
the stack frame and the pc at each step, with example addresses.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week11-step-past.mp4" type="video/mp4">
  <track kind="captions" src="../week11-step-past.vtt" srclang="en" label="English" default>
</video>

[Download the video](week11-step-past.mp4){ download="week11-step-past.mp4" } (MP4, 8 MB) · [Captions](week11-step-past.vtt) (WebVTT) · [All five Week 11 videos](week11.md)
