---
hide:
  - toc
---

# Each Command Decides

**Exercise:** `47k_file_commands` (extra credit) · **Thu Nov 12** · **Length:** 5:51 · **Lecture:** [Week 12 · Extra credit · `47k`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#ec-47k) · **Explainer:** [Each Command Decides](https://claude.ai/artifact/69tjrJXenApSEWYXf8Vxdx)

A narrated walk through the explainer, for after the Nov 10 lecture and before
Thursday's session, for the extra credit: the filesystem reports facts, such as
a name that is not there, a name that is taken, or an inode that is a
directory, and never says what to do about one. Each command decides which
facts are errors, so the same fact can be fine for one command and an error for
another. The video reads what each call can report, then steps through an
example session typed under `cargo run`, one command at a time: the fact that
decides it, its verdict, and the inode table and directory entries after it.
A table of facts, each with its verdicts, follows, then three wrong kernels
the test cannot tell from a right one, each in a typed run. The video ends on
what you write and the test's checks. It shows no solution code: only each
command's deciding fact and verdict, the inode table and the directory entries,
with example names, or the test's own.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week12-facts.mp4" type="video/mp4">
  <track kind="captions" src="../week12-facts.vtt" srclang="en" label="English" default>
</video>

[Download the video](week12-facts.mp4){ download="week12-facts.mp4" } (MP4, 11 MB) · [Captions](week12-facts.vtt) (WebVTT) · [All three Week 12 videos](week12.md)
