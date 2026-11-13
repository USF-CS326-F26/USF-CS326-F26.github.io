---
hide:
  - toc
---

# Needs This First

**Exercise:** `42k_boot_to_life` · **Fri Nov 6** · **Length:** 5:33 · **Lecture:** [Week 11 · Boot is a dependency graph](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#42k-graph) · **Explainer:** [Needs This First](https://claude.ai/artifact/4Ca1P5C4ww4eG7tfNp628U)

A narrated walk through the explainer, for after the Nov 3 lecture and before
Friday's session: boot brings each part up after everything it uses. The video
reads rv6's boot as a graph of needs, then steps through the boot of an example
machine and the given self-check's three checks, watching what each part holds.
Two broken cases follow, with what the test printed in real runs: `kinit` as
you receive it, and the table built before the allocator, beside the same order
recorded in the `43k` kernel. The video ends on the two builds of one kernel,
the self-check's checks and what they cannot see. It shows no solution code:
only the state of each part, with example addresses.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week11-boot-order.mp4" type="video/mp4">
  <track kind="captions" src="../week11-boot-order.vtt" srclang="en" label="English" default>
</video>

[Download the video](week11-boot-order.mp4){ download="week11-boot-order.mp4" } (MP4, 8 MB) · [Captions](week11-boot-order.vtt) (WebVTT) · [All five Week 11 videos](week11.md)
