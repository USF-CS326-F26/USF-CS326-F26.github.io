---
hide:
  - toc
---

# One Atomic Step

**Exercise:** `37k_spinlocks` · **Thu Oct 29** · **Length:** 5:31 · **Lecture:** [Week 10 · One indivisible step](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-cas) · **Explainer:** [One Atomic Step](https://claude.ai/artifact/R7FQ5qGPtLLYMmANurEaDJ)

A narrated walk through the explainer, for after the Oct 27 lecture and before
Thursday's session: a spinlock is one word beside the data it guards, and the
hardware gives one step on that word that nothing can split. Two harts race for
a two-word record, first taking the lock with that step, then with a read and a
separate write. Then one hart, and an interrupt handler that spins on the lock
its own hart holds. The course's test runs on one hart, so all three are
pictures of the machine's state, not recorded runs. The video ends on what you
write, and on the explainer that walks the test. It shows no solution code, and
its numbers are examples, not the lecture's.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../week10-atomic-step.mp4" type="video/mp4">
  <track kind="captions" src="../week10-atomic-step.vtt" srclang="en" label="English" default>
</video>

[Download the video](week10-atomic-step.mp4){ download="week10-atomic-step.mp4" } (MP4, 12 MB) · [Captions](week10-atomic-step.vtt) (WebVTT) · [All five Week 10 videos](week10.md)
