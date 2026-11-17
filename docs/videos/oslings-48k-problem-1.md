---
hide:
  - toc
---

# OSlings Practice 48k, Problem 1: User Mode and System Calls

**OSlings Practice 48k**, its one problem · **Length:** 8:29 · **Exercise:** `48k_user_mode` (Week 12) · **Problems:** [48k](../assignments/oslings-48k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-48k-solutions.pdf) (PDF)

Three parts, worked on all four of the set's pages: (a) for four system calls, which handler `dispatch` calls and what the program gets back in `a0`; (b) what happens after the first `write` when `usertrap` leaves out `(*tf).epc += 4`, and why; (c) (i) what happens when the code page is mapped without `PTE_U`, and (ii) why the trampoline and trapframe pages are mapped without it. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-48k-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-48k-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-48k-problem-1.mp4){ download="oslings-48k-problem-1.mp4" } (MP4, 15 MB) · [Captions](oslings-48k-problem-1.vtt) (WebVTT) · [The set](../assignments/oslings-practice.md#48k)
