---
hide:
  - toc
---

# Two Counts on One Page

**Exercise:** `38k_semaphores` · **Thu Oct 29** · **Length:** 5:13 · **Lecture:** [Week 10 · Semaphores and the heap](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#thu-38k) · **Explainer:** [Two Counts on One Page](https://claude.ai/artifact/EXGs5GbbrrPuzfrsdy2fhx)

A narrated walk through the explainer, for after the Oct 27 lecture and before
Thursday's session: an `Arc<Semaphore>` lives on one heap page, which the heap
takes from the page allocator. The video steps through the block's strong
count and permit count as owners are made, permits are taken and refused, one
comes back, and the owners drop. Two broken cases follow, with what the test
printed for each in a real run: a wait with no zero check, and a wait that
locks the count twice. The video ends on what you write and how to read the
line the test prints. It shows no solution code: only the block's words, the
owners and the free list, with numbers that are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week10-two-counts.mp4" type="video/mp4">
  <track kind="captions" src="../week10-two-counts.vtt" srclang="en" label="English" default>
</video>

[Download the video](week10-two-counts.mp4){ download="week10-two-counts.mp4" } (MP4, 13 MB) · [Captions](week10-two-counts.vtt) (WebVTT) · [All five Week 10 videos](week10.md)
