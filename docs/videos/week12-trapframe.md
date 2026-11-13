---
hide:
  - toc
---

# Parked in the Trapframe

**Exercise:** `48k_user_mode` · **Fri Nov 13** · **Length:** 6:22 · **Lecture:** [Week 12 · The trapframe, and why not the user's stack](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-trapframe) · **Explainer:** [Parked in the Trapframe](https://claude.ai/artifact/UtJxmBPPaTWJvHHdxymvo2)

A narrated walk through the explainer, for after the Nov 10 lecture and before
Friday's session: for the length of a system call, the program's registers
exist only in its trapframe, a page of the process's own, not the program's
stack. The video reads the trapframe's slots, then steps through one `getpid`
in an example process, from its `ecall` through the given `uservec` and
`usertrap`, your `ecall` branch, and the given `usertrapret` to `userret` and
back to user mode, watching the trap registers, the slots, and where the
program's values are at each step. A broken case follows, a resume pc that
lands inside the `ecall`, with what the program meets there; then where
`stvec` points on each part of the trip. A second case, an answer that never
reaches the program, passes the test and is wrong: keys typed into
`cargo run`, for it and for the reference, show the difference. The video
ends on what you write and the test's checks. It shows no solution code: only
the registers, the trapframe's slots and the pc at each step, with example
numbers.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week12-trapframe.mp4" type="video/mp4">
  <track kind="captions" src="../week12-trapframe.vtt" srclang="en" label="English" default>
</video>

[Download the video](week12-trapframe.mp4){ download="week12-trapframe.mp4" } (MP4, 9 MB) · [Captions](week12-trapframe.vtt) (WebVTT) · [All six Week 12 videos](week12.md)
