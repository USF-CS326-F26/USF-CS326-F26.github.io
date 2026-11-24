---
hide:
  - toc
---

# Midterm 2, Section 01, Problem 5: User Mode and System Calls

**Midterm 2, Section 01**, problem 5 of 5 · **Length:** 13:41 · **Exercise:** `48k_user_mode` (Week 12) · **Exam:** [Section 01](../assignments/midterm-2-section-01.pdf) (PDF) · **Answer key:** [Solutions](../assignments/midterm-2-section-01-solutions.pdf) (PDF)

Four parts, worked on pages 10 and 11: (a) which handler `dispatch` calls and what the program gets back in `a0` for five system calls, in a table; (b) the `getpid` call at `0x14` traced through `usertrap`: `sepc`, `scause`, the trapframe's `epc` and `a0`, and where it resumes, with the work shown, and what happens without `epc += 4`; (c) a code page mapped without `PTE_X`: what happens when the program starts, and that trap's `scause`; (d) why the trampoline and trapframe pages have no `PTE_U`, and why the trampoline sits at the same virtual address in every page table. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="https://cs326-f26.cs.usfca.edu/USF-CS326-F26-media/videos/midterm-2-section-01-problem-5.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-2-section-01-problem-5.vtt" srclang="en" label="English" default>
</video>

[Download the video](https://cs326-f26.cs.usfca.edu/USF-CS326-F26-media/videos/midterm-2-section-01-problem-5.mp4){ download="midterm-2-section-01-problem-5.mp4" } (MP4, 30 MB) · [Captions](midterm-2-section-01-problem-5.vtt) (WebVTT) · [All five problems](../assignments/midterm-2-solutions.md#section-01)
