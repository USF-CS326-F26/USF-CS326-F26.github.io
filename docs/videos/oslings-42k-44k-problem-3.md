---
hide:
  - toc
---

# OSlings Practice 42k-44k, Problem 3: Interrupts

**OSlings Practice 42k-44k**, problem 3 of 3 · **Length:** 5:34 · **Exercise:** `44k_interrupts` (Week 11) · **Problems:** [42k-44k](../assignments/oslings-42k-44k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-42k-44k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 5 and 6: (a) a timer tick's `scause`, `0x8000_0000_0000_0001`: its top bit, whether it is an interrupt or an exception, its code, and what `kerneltrap` does with it; (b) what happens after `sret` when the handler counts the tick but never clears SSIP, and why. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-42k-44k-problem-3.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-42k-44k-problem-3.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-42k-44k-problem-3.mp4){ download="oslings-42k-44k-problem-3.mp4" } (MP4, 10 MB) · [Captions](oslings-42k-44k-problem-3.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#42k-44k)
