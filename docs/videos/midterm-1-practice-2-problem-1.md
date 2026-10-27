---
hide:
  - toc
---

# Practice Exam 2, Problem 1: Short Questions

**Midterm 1 practice exam 2**, problem 1 of 5 · **Length:** 11:27 · **Exercises:** `20a_asm_bridge` (Week 6) · `21r_unsafe_bridge` (Week 6) · `30k_kernel_basics` (Week 6) · **Answer key:** [Solutions](../assignments/midterm-1-practice-2-solutions.pdf) (PDF)

Four parts, worked on the exam's pages 2 to 5: (a) which line of a `write_reg` test fails to compile, why a checked write needs no `unsafe`, and what a write past the end of the array does; (b) what an optimizing compiler may do to a UART send loop written with plain accesses, and the volatile rewrite; (c) which compiler message each change to the `30k` kernel produces, and why `#[no_std]` without its `!` fails; (d) what happens when `bytecopy`'s `extern "C"` declaration lists its arguments in the wrong order. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../midterm-1-practice-2-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-1-practice-2-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](midterm-1-practice-2-problem-1.mp4){ download="midterm-1-practice-2-problem-1.mp4" } (MP4, 28 MB) · [Captions](midterm-1-practice-2-problem-1.vtt) (WebVTT) · [All five problems](../assignments/practice-set-01.md#solution-videos-2)
