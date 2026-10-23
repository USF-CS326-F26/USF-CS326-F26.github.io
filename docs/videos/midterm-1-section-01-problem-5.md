---
hide:
  - toc
---

# Midterm 1, Section 01, Problem 5: The Free List and a Page Table

**Midterm 1, Section 01**, problem 5 of 5 · **Length:** 12:18 · **Exercises:** `32k_physical_memory` (Week 7) · `33k_paging` (Week 7) · **Exam:** [Section 01](../assignments/midterm-1-section-01.pdf) (PDF) · **Answer key:** [Solutions](../assignments/midterm-1-section-01-solutions.pdf) (PDF)

Four parts, worked on pages 10 and 11: (a) four `kalloc` and `kfree` calls traced on the free list; (b) the three PTEs `map_page` writes as it takes fresh tables from `kalloc`; (c) a translation by hand through those tables, and an address that faults; (d) a PTE decoded by hand: its flags, its physical address, leaf or branch, and where an entry sits in its table. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../midterm-1-section-01-problem-5.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-1-section-01-problem-5.vtt" srclang="en" label="English" default>
</video>

[Download the video](midterm-1-section-01-problem-5.mp4){ download="midterm-1-section-01-problem-5.mp4" } (MP4, 29 MB) · [Captions](midterm-1-section-01-problem-5.vtt) (WebVTT) · [All five problems](../assignments/midterm-1-solutions.md#section-01)
