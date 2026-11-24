---
hide:
  - toc
---

# Midterm 2, Section 01, Problem 2: The Kernel Page Table

**Midterm 2, Section 01**, problem 2 of 5 · **Length:** 13:02 · **Exercise:** `39k_virtual_memory` (Week 10) · **Exam:** [Section 01](../assignments/midterm-2-section-01.pdf) (PDF) · **Answer key:** [Solutions](../assignments/midterm-2-section-01-solutions.pdf) (PDF)

Four parts, worked on pages 4 and 5: (a) the value `make_satp` returns for the root page table, with the work shown, and why `>> 12` loses nothing; (b) five virtual addresses translated through `kvmmake`'s table, index by index, to a physical address or a page fault, in a table; (c) two more device mappings: their indexes, and whether `walk` allocates a new level-1 or level-0 table; (d) a `kvmmake` that maps the UART's page without `PTE_W`: the flags in a leaf entry, and what happens next. The answer key's handwriting is written onto the exam page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="https://cs326-f26.cs.usfca.edu/USF-CS326-F26-media/videos/midterm-2-section-01-problem-2.mp4" type="video/mp4">
  <track kind="captions" src="../midterm-2-section-01-problem-2.vtt" srclang="en" label="English" default>
</video>

[Download the video](https://cs326-f26.cs.usfca.edu/USF-CS326-F26-media/videos/midterm-2-section-01-problem-2.mp4){ download="midterm-2-section-01-problem-2.mp4" } (MP4, 30 MB) · [Captions](midterm-2-section-01-problem-2.vtt) (WebVTT) · [All five problems](../assignments/midterm-2-solutions.md#section-01)
