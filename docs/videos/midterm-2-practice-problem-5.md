---
hide:
  - toc
---

# Midterm 2 Practice Exam, Problem 5: User Mode and System Calls

**Midterm 2 practice exam**, problem 5 of 6 · **Length:** 7:44 · **Exercise:** `48k_user_mode` (Week 12) · **Problems:** [Practice exam](../assignments/midterm-2-practice.pdf) (PDF) · **Answer key:** [Solutions](../assignments/midterm-2-practice-solutions.pdf) (PDF)

Three parts, worked on the exam's pages 12 to 14: (a) which handler `dispatch` calls and what the program gets back in `a0` for four system calls; (b) why `usertrap` adds 4 to `epc` for an `ecall` but not for a timer interrupt; (c) what happens when `map_user_pages` swaps the code and stack pages. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../midterm-2-practice-problem-5.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-2-practice-problem-5.vtt" srclang="en" label="English" default>
</video>

[Download the video](midterm-2-practice-problem-5.mp4){ download="midterm-2-practice-problem-5.mp4" } (MP4, 14 MB) · [Captions](midterm-2-practice-problem-5.vtt) (WebVTT) · [All six problems](../assignments/practice-set-02.md#solution-videos)
