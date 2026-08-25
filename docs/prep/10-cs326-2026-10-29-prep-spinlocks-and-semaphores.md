# Prep: Spinlocks and Semaphores — 37k · 38k

**Session:** Thu Oct 29, 1h45 · **Exercises:** `37k_spinlocks`, `38k_semaphores` · **Prep time:** ~55 min · **Lecture:** [Locks, Semaphores, and the Kernel Heap](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md)

## What you will build

Two layers of synchronization, bottom up. First a spinlock: an `AtomicBool` beside an `UnsafeCell<T>`, claimed by compare-and-exchange, whose only path to the data is a guard that unlocks itself in `Drop`. Second, a counting semaphore built on that lock, non-blocking since nobody can be woken yet, and with it the kernel's first heap: a page-per-allocation `#[global_allocator]` that makes `Box`, `Vec`, and `Arc` usable, so two owners can share one semaphore.

## Concepts you need

- **A race lives in the interleaving; more code cannot close the window** — [Locks and Semaphores §1](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#1-constructing-a-race-condition) · [Key Concepts § race condition](../guides/key-concepts.md#race-condition)
- **Compare-and-exchange vs. test-and-set; `Acquire` on take, `Release` on release** — [Locks and Semaphores §2](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#2-atomicity-what-the-hardware-gives-you) · [Key Concepts § atomicity](../guides/key-concepts.md#atomicity)
- **`UnsafeCell`, interior mutability, and the RAII guard** — [Locks and Semaphores §4](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#4-the-guard-turning-discipline-into-a-type) · [Rust for Systems § The guard pattern](../guides/rust-for-systems.md#the-guard-pattern)
- **`Send`, `Sync`, and what `unsafe impl Sync` promises** — [Locks and Semaphores §4, Send and Sync](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#send-sync-and-a-promise-the-compiler-cannot-check) · [Unsafe Rust § Send and Sync](../guides/rust-unsafe-nostd.md#send-and-sync)
- **Counting semaphores: permits, P and V, the lost wakeup** — [Locks and Semaphores §6](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#6-semaphores) · [Key Concepts § semaphore](../guides/key-concepts.md#semaphore)
- **The heap arrives: `GlobalAlloc`, one page per allocation, `Arc`** — [Locks and Semaphores §7](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#7-the-kernel-heap-comes-online) · [Key Concepts § heap](../guides/key-concepts.md#heap)

## Read before class

| What | Time |
|---|---|
| Locks and Semaphores §1–§2 (the race traced, CAS, the compiled lock) | 15 min |
| Locks and Semaphores §3–§4 (ordering, `UnsafeCell`, the guard, `Send`/`Sync`) | 15 min |
| Locks and Semaphores §6–§7 (semaphores, lost wakeup, the heap, `Arc`) | 15 min |
| Unsafe Rust guide: `UnsafeCell`, `Send`/`Sync` | 5 min |
| Key Concepts guide: Concurrency cluster, heap | 5 min |

## Mental model

Two harts decrement a ticket count under one spinlock:

```text
 time  hart A                                hart B                            locked  tickets
   1   CAS false->true  -> Ok                .                                 true    3
   2   ld 3; addi -1; sd 2                   CAS false->true  -> Err(true)     true    2
   3   guard dropped: fence rw,w; sb false   pause; CAS false->true -> Ok      true    2
   4   .                                     ld 2; addi -1; sd 1               true    1
   5   .                                     guard dropped                     false   1
```

Only one CAS can win the `false → true` transition, so B's read-modify-write cannot slide between A's load and store. A's `Release` at drop and B's `Acquire` on its winning CAS are why B loads 2, not a stale 3: the pair protects the data, not merely the flag. A counting semaphore is this picture plus one rule: the count never goes below zero, and a caller who finds zero is refused, not put to sleep, since on one hart nobody else would run to return the permit.

## Check yourself

1. `if !busy { busy = true; }` guards a critical section on rv6's single hart, interrupts enabled. Why can it still fail? <details><summary>Answer</summary>It is a load, a branch, and a store; an interrupt between load and store runs a handler that also reads `false` and enters. Only an operation with no interior, one `amoor.w.aq`, closes the window.</details>
2. A struct holds an `UnsafeCell<T>`. Why does the compiler reject `static X: ThatStruct`, and what does `unsafe impl<T: Send> Sync for ThatStruct` claim? <details><summary>Answer</summary>A `static` must be `Sync`; `UnsafeCell` is deliberately `!Sync`, so the struct is too. The `unsafe impl` is the author's promise that the lock serializes every access.</details>
3. After `let b = Arc::clone(&a);`, how many copies of the value exist, and how can either mutate it? <details><summary>Answer</summary>One. `Arc::clone` copies a pointer and atomically bumps the strong count. `Arc<T>` yields only `&T`, so mutation needs interior mutability inside `T`: a lock.</details>

## What "done" looks like

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway (substantial credit), then finish by **Thursday 11:59 pm** and submit again.

## If you finish early

Work [Practice Problems 3 and 4](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#practice-problems) and read [Locks and Semaphores §5](../lectures/09-cs326-2026-10-22-locks-semaphores-and-the-kernel-heap.md#5-deadlock-lock-order-and-interrupts) on single-hart deadlock, then chapter 6, "Locking," of the xv6 book, or start Friday's [Prep: Virtual Memory](10-cs326-2026-10-30-prep-virtual-memory.md).
