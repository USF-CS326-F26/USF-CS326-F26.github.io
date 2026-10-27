---
hide:
  - toc
---

# The Guard Holds It

**Exercise:** `37k_spinlocks` · **Thu Oct 29** · **Length:** 5:26 · **Lecture:** [Week 10 · The guard unlocks for you](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-guard) · **Explainer:** [The Guard Holds It](https://claude.ai/artifact/4AGctGPCFZQM4SLvpv16tK)

A narrated walk through the explainer, for after the Oct 27 lecture and before
Thursday's session: a guard is the only way to a spinlock's data. The video
steps through the given `37k` test call by call and watches the lock word read
true exactly while a guard is alive. Three broken cases follow, with what the
test printed for each in a real run: the untouched skeleton, a try that claims
without asking, and a try that waits. The video ends on the test's checks, how
to read the line it prints, and what the test cannot see. It shows no solution
code: only the lock's two words and the guards alive at each call, with the
given test's own numbers.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week10-guard.mp4" type="video/mp4">
  <track kind="captions" src="../week10-guard.vtt" srclang="en" label="English" default>
</video>

[Download the video](week10-guard.mp4){ download="week10-guard.mp4" } (MP4, 14 MB) · [Captions](week10-guard.vtt) (WebVTT) · [All five Week 10 videos](week10.md)
