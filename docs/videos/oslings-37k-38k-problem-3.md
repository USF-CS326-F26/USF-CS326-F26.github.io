---
hide:
  - toc
---

# OSlings Practice 37k-38k, Problem 3: The Kernel Heap

**OSlings Practice 37k-38k**, problem 3 of 3 · **Length:** 7:30 · **Exercise:** `38k_semaphores` (Week 10) · **Problems:** [37k-38k](../assignments/oslings-37k-38k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-37k-38k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 5 and 6: (a) eight lines of code run against 38k's heap, which hands out one whole page per allocation, in a table: the page each line allocates or frees, and the page at the head of the free list afterwards; (b) what happens, and why, in three cases: (i) `Vec::<u64>::with_capacity(512)`, then `(513)`; (ii) `kmain` forgetting `kalloc::init()` before the first `Arc::new`; (iii) how many bytes of its page line 1's `Box` uses. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-37k-38k-problem-3.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-37k-38k-problem-3.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-37k-38k-problem-3.mp4){ download="oslings-37k-38k-problem-3.mp4" } (MP4, 13 MB) · [Captions](oslings-37k-38k-problem-3.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#37k-38k)
