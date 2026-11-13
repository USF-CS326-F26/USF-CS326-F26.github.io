---
hide:
  - toc
---

# A Number in a7

**Exercise:** `48k_user_mode` · **Fri Nov 13** · **Length:** 5:56 · **Lecture:** [Week 12 · The system-call ABI](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#48k-abi) · **Explainer:** [A Number in a7](https://claude.ai/artifact/GEDojfRveMi5jn7Sm7sXuG)

A narrated walk through the explainer, for after the Nov 10 lecture and before
Friday's session: a system call is a number in `a7` and up to three arguments
in `a0` to `a2`; the kernel picks a handler by the number, and the answer comes
back in `a0`, though `exit` never comes back at all. The video reads one
example `write`, before and after, and the three numbers rv6 knows, then steps
through an example program's four calls, one of them a number rv6 does not
know, watching the program's registers, the handler each number picks, if
any, and each answer that comes back. A broken case follows, `dispatch` as
you receive it, with what the test prints for it; then four broken kernels
that make the test print the same line. The video ends on what you write, the
test's checks and what each failed one prints, and what the test cannot see.
It shows no solution code: only the program's registers and each call's
answer at each step, with example numbers.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week12-a7.mp4" type="video/mp4">
  <track kind="captions" src="../week12-a7.vtt" srclang="en" label="English" default>
</video>

[Download the video](week12-a7.mp4){ download="week12-a7.mp4" } (MP4, 8 MB) · [Captions](week12-a7.vtt) (WebVTT) · [All six Week 12 videos](week12.md)
