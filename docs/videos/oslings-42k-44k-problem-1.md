---
hide:
  - toc
---

# OSlings Practice 42k-44k, Problem 1: Boot Order

**OSlings Practice 42k-44k**, problem 1 of 3 · **Length:** 4:58 · **Exercise:** `42k_boot_to_life` (Week 11) · **Problems:** [42k-44k](../assignments/oslings-42k-44k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-42k-44k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 1 and 2: (a) what `kvmmake()` returns when `kinit` builds the page table before `kalloc::init()`, and why, then the fixed order; (b) why `uart::init()` comes first, and why the idle loop runs `wfi` instead of spinning in an empty `loop {}`. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-42k-44k-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-42k-44k-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-42k-44k-problem-1.mp4){ download="oslings-42k-44k-problem-1.mp4" } (MP4, 8 MB) · [Captions](oslings-42k-44k-problem-1.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#42k-44k)
