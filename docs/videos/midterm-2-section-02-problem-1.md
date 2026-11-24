---
hide:
  - toc
---

# Midterm 2, Section 02, Problem 1: Round-Robin Scheduling

**Midterm 2, Section 02**, problem 1 of 5 · **Length:** 12:08 · **Exercises:** `35k_context_switch` (Week 9) · `36k_scheduling` (Week 9) · `44k_interrupts` (Week 11) · **Exam:** [Section 02](../assignments/midterm-2-section-02.pdf) (PDF) · **Answer key:** [Solutions](../assignments/midterm-2-section-02-solutions.pdf) (PDF)

Three parts, worked on pages 2 and 3: (a) six calls to `pick_next` traced in a table, from `self.next` = 5, with the process in slot 3 waking up partway; (b) what changes when `pick_next` sets `self.next = (i + 2) % n`: the order of nine turns, with the work shown, and what broke; (c) a process that spins without ever calling `swtch`, under cooperative scheduling: what happens to the others, why, and what change would let them run. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="https://cs326-f26.cs.usfca.edu/USF-CS326-F26-media/videos/midterm-2-section-02-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-2-section-02-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](https://cs326-f26.cs.usfca.edu/USF-CS326-F26-media/videos/midterm-2-section-02-problem-1.mp4){ download="midterm-2-section-02-problem-1.mp4" } (MP4, 22 MB) · [Captions](midterm-2-section-02-problem-1.vtt) (WebVTT) · [All five problems](../assignments/midterm-2-solutions.md#section-02)
