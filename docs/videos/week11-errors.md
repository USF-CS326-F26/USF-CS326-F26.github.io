---
hide:
  - toc
---

# Errors Are Values

**Exercise:** `40k_filesystem` · **Thu Nov 5** · **Length:** 5:50 · **Lecture:** [Week 11 · Errors as values, behind one lock](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-errors) · **Explainer:** [Errors Are Values](https://claude.ai/artifact/Cb9F5ZqKSTVrQN4U1mxwBP)

A narrated walk through the explainer, for after the Nov 3 lecture and before
Thursday's session: every call that can fail answers with a value, `Ok` with a
number or `Err` with the fact that went wrong. The video steps through the
given `dircreate`, where one `Err` is the answer a create wants, then through
the given `40k` test call by call, watching each answer and each check. Three
broken cases follow, with what the test printed for each in a real run: the
untouched skeleton, a lookup that compares all 14 bytes, and a write that never
sets the size. The video ends on the test's checks, how to read the line it
prints, and what the test cannot see. It shows no solution code: only the inode
table and each call's `Result`, with the given test's own names.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week11-errors.mp4" type="video/mp4">
  <track kind="captions" src="../week11-errors.vtt" srclang="en" label="English" default>
</video>

[Download the video](week11-errors.mp4){ download="week11-errors.mp4" } (MP4, 9 MB) · [Captions](week11-errors.vtt) (WebVTT) · [All five Week 11 videos](week11.md)
