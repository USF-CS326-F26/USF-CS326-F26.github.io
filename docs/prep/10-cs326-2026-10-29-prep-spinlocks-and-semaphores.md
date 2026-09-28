# Prep: Spinlocks and Semaphores — 37k · 38k

**Session:** Thu Oct 29, 1h45 · **Exercises:** `37k_spinlocks`, `38k_semaphores` · **Prep time:** ~30 min · **Lecture:** [Week 10 · Locks, Semaphores, and Turning the MMU On](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md)

## What you will build

Two layers of synchronization, bottom up. First a spinlock: an `AtomicBool` beside an `UnsafeCell<T>`, claimed by compare-and-exchange, whose only path to the data is a guard that unlocks itself in `Drop`. Second, a counting semaphore built on that lock, non-blocking since nobody can be woken yet, and with it the kernel's first heap: a page-per-allocation `#[global_allocator]` that makes `Box`, `Vec`, and `Arc` usable, so two owners can share one semaphore.

## Concepts you need

- **A race lives in the interleaving; more code cannot close the window** — [Week 10 · A race, built by hand](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-race) · [Key Concepts: race condition](../guides/key-concepts.md#race-condition)
- **Compare-and-exchange vs. test-and-set; `Acquire` on take, `Release` on release** — [Week 10 · One indivisible step](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-cas), [Test-and-set versus CAS](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-tas) · [Key Concepts: atomicity](../guides/key-concepts.md#atomicity)
- **`UnsafeCell`, interior mutability, and the RAII guard** — [Week 10 · Shared, yet mutable: `UnsafeCell`, `Send` and `Sync`](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-cell), [The guard unlocks for you](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-guard) · [Rust for Systems: The guard pattern](../guides/rust-for-systems.md#the-guard-pattern)
- **`Send`, `Sync`, and what `unsafe impl Sync` promises** — [Week 10 · Shared, yet mutable: `UnsafeCell`, `Send` and `Sync`](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-cell) · [Unsafe guide: `Send` and `Sync`](../guides/rust-unsafe-nostd.md#send-and-sync)
- **Counting semaphores: permits, P and V, the lost wakeup** — [Week 10 · Permits: P and V](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#38k-permits), [The lost wakeup](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-lost-wakeup) · [Key Concepts: semaphore](../guides/key-concepts.md#semaphore)
- **The heap arrives: `GlobalAlloc`, one page per allocation, `Arc`** — [Week 10 · The heap arrives](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#38k-heap), [`Arc`: one value, many owners](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#38k-arc) · [Key Concepts: heap](../guides/key-concepts.md#heap)

## Read before class

| What | Time |
|---|---|
| [Week 10 · This week](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#this-week), then [Thursday · `37k` Spinlocks](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#thu-37k) through [One indivisible step](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-cas) | 4 min |
| [Week 10 · Shared, yet mutable: `UnsafeCell`, `Send` and `Sync`](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-cell), [The guard unlocks for you](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-guard) and [Interrupts off while you hold it](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#37k-interrupts) | 4 min |
| [Week 10 · Thursday · `38k` Semaphores and the heap](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#thu-38k), all three sections | 4 min |
| [Week 10 · For the exam](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam): [Test-and-set versus CAS](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-tas), [Deadlock](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-deadlock), [The lost wakeup](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-lost-wakeup) and [Bounded buffers](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-bounded). Not needed today; on Midterm 2 | 2 min |
| [Unsafe guide: `UnsafeCell`](../guides/rust-unsafe-nostd.md#unsafecell) and [`Send` and `Sync`](../guides/rust-unsafe-nostd.md#send-and-sync) | 3 min |
| [Key Concepts guide: Concurrency](../guides/key-concepts.md#concurrency), then [heap](../guides/key-concepts.md#heap) | 4 min |

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

`oslings run` is green, then `oslings submit` before you leave. Not green? Submit anyway — the tests that pass earn their share — then finish it at a make-up session (office hours, on the class network) for three quarters, or anywhere else for half, and submit again.

## If you finish early

Work [Week 10 · Problem 2: When does the guard drop?](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#problem-2) and [Problem 3: A bounded buffer of two](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#problem-3) on paper and read [Week 10 · Deadlock](../lectures/10-cs326-2026-10-27-locks-semaphores-and-the-mmu-on.md#exam-deadlock) on single-hart deadlock (Midterm 2 material), then chapter 6, "Locking," of the xv6 book, or start Friday's [Prep: Virtual Memory](10-cs326-2026-10-30-prep-virtual-memory.md).
