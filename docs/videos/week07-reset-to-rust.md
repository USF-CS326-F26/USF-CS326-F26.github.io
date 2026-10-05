---
hide:
  - toc
---

# Reset to Rust

**Exercise:** `31k_boot` · **Thu Oct 8** · **Length:** 4:56 · **Lecture:** [Week 7 · Thursday · `31k` Boot](../lectures/07-cs326-2026-10-06-boot-physical-pages-and-sv39.md#thu-31k) · **Explainer:** [Reset to Rust](https://claude.ai/artifact/B9yNe3QyxKETWh6vx4NEMo)

A narrated walk through the explainer, for before Tuesday's lecture and before
Thursday's session: the `virt` machine's address map, the hart at reset, and the
linker script that places `.entry` first; then the boot, step by step. The stub
is drawn as empty slots, `sp` reaches the top of the 16 KiB boot stack before
any Rust runs, each printed byte is a store to the UART, and a last store to
the test finisher ends the run. Two broken boots follow as QEMU really ran
them, one with no stack and one with `sp` at the stack's low end, and the video
ends on how to read what `oslings` reports. It shows no solution code: only the
machine's state, the given code and the test's output, with addresses that are
examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week07-reset-to-rust.mp4" type="video/mp4">
  <track kind="captions" src="../week07-reset-to-rust.vtt" srclang="en" label="English" default>
</video>

[Download the video](week07-reset-to-rust.mp4){ download="week07-reset-to-rust.mp4" } (MP4, 12 MB) · [Captions](week07-reset-to-rust.vtt) (WebVTT) · [All four Week 7 videos](week07.md)
