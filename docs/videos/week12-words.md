---
hide:
  - toc
---

# The First Word Decides

**Exercise:** `46k_shell` · **Thu Nov 12** · **Length:** 6:02 · **Lecture:** [Week 12 · One match, and `&mut dyn Out`](../lectures/12-cs326-2026-11-10-console-shell-and-user-mode.md#46k-dispatch) · **Explainer:** [The First Word Decides](https://claude.ai/artifact/JD4PbgeJoyTEqSwFRSW6RW)

A narrated walk through the explainer, for after the Nov 10 lecture and before
Thursday's session: a line becomes words, and the first word picks a handler.
The video starts at the keys, typed under `cargo run`, and the line the given
read loop hands on at Enter, then steps through an example script line by
line: the line's bytes, its words as a start and a length, the handler the
first word picks, and what that handler writes. A broken case follows, the
whole line taken as the command, with what the test printed for it in a real
run. The video ends on the given test, line by line, what you write, and what
the test cannot see. It shows no solution code: only the line, its words, the
shell's current directory and the example tree at each step, with example
names, or the test's own.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week12-words.mp4" type="video/mp4">
  <track kind="captions" src="../week12-words.vtt" srclang="en" label="English" default>
</video>

[Download the video](week12-words.mp4){ download="week12-words.mp4" } (MP4, 11 MB) · [Captions](week12-words.vtt) (WebVTT) · [All six Week 12 videos](week12.md)
