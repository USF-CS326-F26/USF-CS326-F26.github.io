---
hide:
  - toc
---

# Practice Exam 2, Problem 3: From Reset to kmain

**Midterm 1 practice exam 2**, problem 3 of 5 · **Length:** 11:42 · **Exercises:** `31k_boot` (Week 7), with `21r_unsafe_bridge` and `30k_kernel_basics` (Week 6) · **Answer key:** [Solutions](../assignments/midterm-1-practice-2-solutions.pdf) (PDF)

Worked on pages 11 to 14, with the kernel's layout kept beside the work: (a) the boot trampoline's register table, where `kmain` saves `ra`, and why `sp` starts at the top of `STACK0`; (b) an `_entry` without its `add`: where the stack lands, what it overwrites, and why the passing test proves nothing; (c) the UART's stores for a short string, `exit_failure`, the value it stores, and the error without its loop. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../midterm-1-practice-2-problem-3.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-1-practice-2-problem-3.vtt" srclang="en" label="English" default>
</video>

[Download the video](midterm-1-practice-2-problem-3.mp4){ download="midterm-1-practice-2-problem-3.mp4" } (MP4, 43 MB) · [Captions](midterm-1-practice-2-problem-3.vtt) (WebVTT) · [All five problems](../assignments/practice-set-01.md#solution-videos-2)
