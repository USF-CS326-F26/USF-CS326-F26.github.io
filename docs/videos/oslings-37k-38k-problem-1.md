---
hide:
  - toc
---

# OSlings Practice 37k-38k, Problem 1: Spinlocks

**OSlings Practice 37k-38k**, problem 1 of 3 · **Length:** 7:33 · **Exercise:** `37k_spinlocks` (Week 10) · **Problems:** [37k-38k](../assignments/oslings-37k-38k.pdf) (PDF) · **Answer key:** [Solutions](../assignments/oslings-37k-38k-solutions.pdf) (PDF)

Three parts, worked on the set's pages 1 and 2: (a) a `try_lock` that checks the lock with a load and claims it with a separate store: an order of the two steps on two CPUs in which both get a guard, what goes wrong once both hold one, and why `compare_exchange` fixes it; (b) 34k's `NEXTPID` moved into a `SpinLock`, with an `alloc_pid` that locks it twice: what happens on the first call, a fix, and why a one-statement update works; (c) the guard's `DerefMut`: which field of `SpinLock` lets a `lock(&self)` guard write through a shared reference, and why that is safe. The answer key's handwriting is written onto the page as each step is worked.

<video controls preload="metadata" playsinline width="1920" height="1080" style="width:100%;height:auto">
  <source src="../oslings-37k-38k-problem-1.mp4" type="video/mp4">
  <track kind="captions" src="../oslings-37k-38k-problem-1.vtt" srclang="en" label="English" default>
</video>

[Download the video](oslings-37k-38k-problem-1.mp4){ download="oslings-37k-38k-problem-1.mp4" } (MP4, 16 MB) · [Captions](oslings-37k-38k-problem-1.vtt) (WebVTT) · [All three problems](../assignments/oslings-practice.md#37k-38k)
