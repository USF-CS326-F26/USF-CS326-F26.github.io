---
hide:
  - toc
---

# OSlings Practice 34k-36k, Problem 1: Processes

**OSlings Practice 34k-36k**, problem 1 of 3 · **Length:** 6:15 · **Exercise:** `34k_processes` (Week 9) · **Problems:** [34k-36k](../assignments/oslings-34k-36k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-34k-36k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 1 and 2: (a) `allocproc` and `freeproc` traced through seven calls on a four-slot table: the slot and pid each call gets, and every slot's state and pid at the end; (b) `create_pagetable` runs out of memory at line 6: what `allocproc` returns, what it leaves in the slot, why that is a problem for the rest of the kernel, and the fix. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-34k-36k-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-34k-36k-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-34k-36k-problem-1.mp4){ download="oslings-34k-36k-problem-1.mp4" } (MP4, 13 MB) · [Captions](oslings-34k-36k-problem-1.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#34k-36k)
