---
hide:
  - toc
---

# OSlings Practice 45k-47k, Problem 1: Console Input

**OSlings Practice 45k-47k**, problem 1 of 3 · **Length:** 5:43 · **Exercise:** `45k_console` (Week 12) · **Problems:** [45k-47k](../assignments/oslings-45k-47k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-45k-47k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 1 and 2: (a) one call to `intr()` with `h` and `i` both waiting in the UART, in a table: with the `while let` loop and with an `if let` instead, how many times the loop body runs, what lands in `BUF[0]` and `BUF[1]`, the `TAIL` value and the bytes left in the UART; then why the loop stops, and how the `i` gets in with `if let`; (b) what happens after a key is pressed when `intr` never reads the UART, and why. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-45k-47k-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-45k-47k-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-45k-47k-problem-1.mp4){ download="oslings-45k-47k-problem-1.mp4" } (MP4, 10 MB) · [Captions](oslings-45k-47k-problem-1.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#45k-47k)
