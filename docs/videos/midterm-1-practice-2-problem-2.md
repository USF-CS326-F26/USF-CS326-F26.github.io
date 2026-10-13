---
hide:
  - toc
---

# Practice Exam 2, Problem 2: The Assembly Bridge

**Midterm 1 practice exam 2**, problem 2 of 5 · **Length:** 12:13 · **Exercises:** `20a_asm_bridge` (Week 6) · **Answer key:** [Solutions](../assignments/midterm-1-practice-2-solutions.pdf) (PDF)

Worked on pages 6 to 10, with the two RISC-V tables and the code beside each part: (a) `bytecopy` traced over three bytes, and why a sign-extending load does not spoil the copy; (b) `bytecopy` edited into `wordcopy`, its registers on return, which registers a caller may still rely on, and why a leaf can skip the stack; (c) `baby_swtch` between the test and `co_entry`: the registers at two moments, what each `Ctx` holds, and what a new field at the top of `Ctx` breaks. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../midterm-1-practice-2-problem-2.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-1-practice-2-problem-2.vtt" srclang="en" label="English" default>
</video>

[Download the video](midterm-1-practice-2-problem-2.mp4){ download="midterm-1-practice-2-problem-2.mp4" } (MP4, 49 MB) · [Captions](midterm-1-practice-2-problem-2.vtt) (WebVTT) · [All five problems](../assignments/practice-set-01.md#solution-videos-2)
