---
hide:
  - toc
---

# OSlings Practice 40k-41k, Problem 2: Devices

**OSlings Practice 40k-41k**, problem 2 of 2 · **Length:** 6:23 · **Exercise:** `41k_devices` (Week 11) · **Problems:** [40k-41k](../assignments/oslings-40k-41k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-40k-41k-solutions.pdf) (PDF)

Two parts, worked on the set's pages 3 and 4: (a) what `tx_ready()`, `rx_ready()` and `getc()` return for three values read from the UART's `LSR`, by its THRE and DR bits; (b) (i) what decides whether the driver reads the received byte or sends one at offset 0, where `RBR` and `THR` both live, and (ii) what could go wrong if `putc` wrote `THR` without waiting for `tx_ready()`. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-40k-41k-problem-2.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-40k-41k-problem-2.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-40k-41k-problem-2.mp4){ download="oslings-40k-41k-problem-2.mp4" } (MP4, 12 MB) · [Captions](oslings-40k-41k-problem-2.vtt) (WebVTT) · [Both problems](../assignments/oslings-practice.md#40k-41k)
