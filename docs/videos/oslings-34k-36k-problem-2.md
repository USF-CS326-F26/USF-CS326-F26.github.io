---
hide:
  - toc
---

# OSlings Practice 34k-36k, Problem 2: Context Switch

**OSlings Practice 34k-36k**, problem 2 of 3 · **Length:** 6:48 · **Exercise:** `35k_context_switch` (Week 9) · **Problems:** [34k-36k](../assignments/oslings-34k-36k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-34k-36k-solutions.pdf) (PDF)

Three parts, worked on the set's pages 2 and 3: (a) the byte offset of `s7` in a `Context`, and why `swtch` saves `ra`, `sp` and `s0`-`s11` but not the `t` and `a` registers; (b) what kmain's `swtch` runs next, on which stack, and when and how it returns; (c) what goes wrong if the restore half loads from `a0`, if `init_context` is passed `stack` instead of `stack + PGSIZE`, or if `#[repr(C)]` is removed. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-34k-36k-problem-2.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-34k-36k-problem-2.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-34k-36k-problem-2.mp4){ download="oslings-34k-36k-problem-2.mp4" } (MP4, 14 MB) · [Captions](oslings-34k-36k-problem-2.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#34k-36k)
