---
hide:
  - toc
---

# `baby_swtch`, Step by Step

**Exercise:** `20a_asm_bridge` · **Thu Oct 1** · **Length:** 8:50 · **Lecture:** [Week 6 · A `ret` that lands somewhere else](../lectures/06-cs326-2026-09-29-below-rust-assembly-unsafe-and-no-std.md#20a-resume) · **Explainer:** [The RISC-V Assembly Bridge](https://claude.ai/artifact/PJa4qsFhcmyyrg8w1fGLJS)

A narrated walk through the explainer's switch stepper: why a call cannot pause
one thread and run another, the memory map and the four-register `Ctx`, every
step of the round trip from `main` to `co_entry` and back, and two broken
versions run for real in QEMU. It ends on what `swtch` in `35k_context_switch`
adds: ten more saved registers, and the same shape.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../babyswtch.mp4" type="video/mp4">
  <track kind="captions" src="../babyswtch.vtt" srclang="en" label="English" default>
</video>

[Download the video](babyswtch.mp4){ download="babyswtch.mp4" } (MP4, 39 MB) · [Captions](babyswtch.vtt) (WebVTT)
