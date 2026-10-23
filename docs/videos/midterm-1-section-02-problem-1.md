---
hide:
  - toc
---

# Midterm 1, Section 02, Problem 1: Short Questions

**Midterm 1, Section 02**, problem 1 of 5 · **Length:** 12:25 · **Exercises:** `01r_control_flow` (Week 1) · `04r_structs_impl` (Week 3) · `06r_collections` (Week 4) · `20a_asm_bridge` (Week 6) · **Exam:** [Section 02](../assignments/midterm-1-section-02.pdf) (PDF) · **Answer key:** [Solutions](../assignments/midterm-1-section-02-solutions.pdf) (PDF)

Four parts, worked on the exam's pages 2 and 3: (a) `pgroundup` and `checked_pgroundup` on two addresses and one near `usize::MAX`, and what the overflowing add does in a debug and a release build; (b) which line of a `Page` and `Pte` program fails to compile, why, and where the `Page` is dropped; (c) what `bytecopy` does when its `extern "C"` declaration reorders its arguments to `(dst, n, src)`, and why its first load faults; (d) `find_pid` on a process table of `Option` values, a `match` on its result, and two uses of it that fail. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../midterm-1-section-02-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-1-section-02-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](midterm-1-section-02-problem-1.mp4){ download="midterm-1-section-02-problem-1.mp4" } (MP4, 28 MB) · [Captions](midterm-1-section-02-problem-1.vtt) (WebVTT) · [All five problems](../assignments/midterm-1-solutions.md#section-02)
