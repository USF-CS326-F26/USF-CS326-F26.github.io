---
hide:
  - toc
---

# OSlings Practice 42k-44k, Problem 2: Traps

**OSlings Practice 42k-44k**, problem 2 of 3 · **Length:** 5:23 · **Exercise:** `43k_traps` (Week 11) · **Problems:** [42k-44k](../assignments/oslings-42k-44k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-42k-44k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 3 and 4: (a) for an `ebreak` at `0x8000_0568`, `sepc` when `kerneltrap` starts and when it returns, the address the CPU jumps to, and where `sret` resumes; (b) what happens after `sret` when `kerneltrap` counts the breakpoint but never advances `sepc`, and why. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-42k-44k-problem-2.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-42k-44k-problem-2.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-42k-44k-problem-2.mp4){ download="oslings-42k-44k-problem-2.mp4" } (MP4, 8 MB) · [Captions](oslings-42k-44k-problem-2.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#42k-44k)
