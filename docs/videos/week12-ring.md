---
hide:
  - toc
---

# Four Bytes, One Claim

**Exercise:** `45k_console` · **Thu Nov 12** · **Length:** 6:20 · **Lecture:** [Week 12 · A ring between two worlds](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#45k-ring) · **Explainer:** [Four Bytes, One Claim](https://claude.ai/artifact/TYhow86F3N4K4R9cAqY7SH)

A narrated walk through the explainer, for after the Nov 10 lecture and before
Thursday's session: a key reaches the kernel as an interrupt; the handler only
fills the ring and never waits, and the reader takes from the ring later, or
sleeps until there is something to take. The video reads the ring's two
counters, each written by one side only, then steps through one claim on an
example paste into `cargo run`, and through the given test's own world, where
nothing traps. Two broken cases follow, with what the test printed in
real runs: the skeleton as you receive it, and a handler that reads the byte
but buffers nothing. The video ends on the wrap and the full ring, what the
test cannot see, and what you write. It shows no solution code: only the UART,
source 10 at the PLIC, and the ring's slots and counters at each step, with
example numbers, or the test's own.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week12-ring.mp4" type="video/mp4">
  <track kind="captions" src="../week12-ring.vtt" srclang="en" label="English" default>
</video>

[Download the video](week12-ring.mp4){ download="week12-ring.mp4" } (MP4, 12 MB) · [Captions](week12-ring.vtt) (WebVTT) · [All six Week 12 videos](week12.md)
