---
hide:
  - toc
---

# Names Live in Directories

**Exercise:** `40k_filesystem` · **Thu Nov 5** · **Length:** 5:23 · **Lecture:** [Week 11 · A file is not its name](../lectures/11-cs326-2026-11-03-filesystems-boot-order-and-traps.md#40k-inodes) · **Explainer:** [Names Live in Directories](https://claude.ai/artifact/RSj4CPZFpb9qJHD6USUH8P)

A narrated walk through the explainer, for after the Nov 3 lecture and before
Thursday's session: an inode records what a file is and what it holds, never
its name; names live in directories, and a path is one lookup per name. The
video looks at an example inode table and one stored name, its 14 bytes and its
length, then walks three paths through the example tree one lookup at a time:
one that is found, one that is not there, and one that asks a file for an
entry. A create follows, as the given code makes it. The video ends on what you
write and what it must do. It shows no solution code: only the records and
entries at each lookup, with example names and numbers, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week11-names.mp4" type="video/mp4">
  <track kind="captions" src="../week11-names.vtt" srclang="en" label="English" default>
</video>

[Download the video](week11-names.mp4){ download="week11-names.mp4" } (MP4, 7 MB) · [Captions](week11-names.vtt) (WebVTT) · [All five Week 11 videos](week11.md)
