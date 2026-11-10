---
hide:
  - toc
---

# OSlings Practice 37k-38k, Problem 2: Semaphores and Arc

**OSlings Practice 37k-38k**, problem 2 of 3 · **Length:** 6:58 · **Exercise:** `38k_semaphores` (Week 10) · **Problems:** [37k-38k](../assignments/oslings-37k-38k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-37k-38k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 3 and 4: (a) nine lines on a semaphore made with one permit and shared through an `Arc`, in a table: what each line returns, `available()` after it, and the owners (`strong_count`); then what is unusual after line 6, and whether any code stops it; (b) whether `*c2 += 1` compiles on a clone of an `Arc<i64>`, why `s2.post()` can change a count shared through an `Arc` when that increment can't, and the fix. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-37k-38k-problem-2.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-37k-38k-problem-2.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-37k-38k-problem-2.mp4){ download="oslings-37k-38k-problem-2.mp4" } (MP4, 15 MB) · [Captions](oslings-37k-38k-problem-2.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#37k-38k)
