# CS 326 — improvements for next time

A running list of changes to make before the course is taught again. Written
while F26 is in flight, when the reason is still fresh; nothing here is applied
to the semester in progress unless it is marked **applied**.

Each entry says what to change, why, and what else moves with it. Keep the
"Evidence" lines — they are what makes an entry checkable a year later, when the
memory of the session has gone.

---

## Move the `Drop` material from `04r_structs_impl` into `03r_borrowing`

**Status:** proposed for the next offering. F26 shipped the interim version —
see "What F26 actually did" below.

**Change.** Teach `Drop` in `03r_borrowing`, where the guard is already being
built, and take it back out of `04r_structs_impl`.

**Why.** `Drop` is introduced in the ownership lecture
(`docs/lectures/02-cs326-2026-09-01-ownership-borrowing-and-lifetimes.md`, §3
"Drop: Where `free()` Went") and it is load-bearing there — it is what makes the
three-part ownership rule true rather than asserted, it is the only honest
definition of the `Copy` dividing line, and it is one of the three legs of the
`SpinLockGuard` argument the lecture converges on in §6.1. But in F26 the
exercises did not touch it for another seven weeks, so it arrived at `37k` as
recall rather than recognition.

`03r_borrowing` is where it belongs, because the exercise already builds the
object that wants it. `Guard<'a> { slot: &'a mut u64 }` has `new`/`get`/`set`
and no `Drop` impl, so it teaches the lifetime-and-exclusivity half of the guard
pattern and stops. Its own README already forward-references the missing half
("holding the guard *is* holding the lock, and dropping it unlocks"), and
`hints.md` mentions "a `Drop` that releases a lock" — both describing something
the student never writes.

**Evidence (F26, verified 2026-09-07).**

- `grep -rn "Drop" exercises/02r_ownership exercises/03r_borrowing` matched only
  prose: the READMEs' "dropped here" comment and the two forward references
  above. No `impl Drop`, in skeleton, solution or tests.
- The first `impl Drop` anywhere in `exercises/` was
  `37k_spinlocks/skeleton/spinlock.rs`, and it was *given*, not written by the
  student. Every later `spinlock.rs` is a copy of it.
- `04r`–`08r` did not mention `Drop` at all.
- Across the lecture set, `Drop` appeared 20× in the Sep 1 ownership lecture and
  next in `09-…-locks-semaphores-and-the-kernel-heap.md` (Oct 22, 8×), the
  lecture paired with `37k`.
- The exercise the lecture cites for its `Guard<'a>` (Problem 4b,
  `the_borrow_ends_when_the_guard_goes_out_of_scope`) tests that the *borrow*
  ends at the closing brace. Nothing runs there.

**What the `03r` version should look like.**

- Add `impl Drop for Guard<'_>` with an observable release. The counter the
  guard already borrows is enough: have `Drop` write a sentinel, or have the
  guard hold `&'a mut Vec<usize>` (a free list) and push the page back, which is
  the shape `04r` used in F26 and which reads as `kfree`.
- Add a test that the release ran, and ran exactly *once* — a count, not a
  boolean. "Exactly once" is the half of the property that `Copy`/`Drop`
  exclusion exists to protect, and a boolean cannot see it.
- Add a test that drops early by moving the guard into a by-value method with an
  empty body, so `std::mem::drop` stops being a curiosity: release travels with
  ownership.
- The `Copy`/`Drop` exclusion is worth a paragraph in the README at that point,
  since `04r` introduces `#[derive(Copy)]` the very next session and the
  contrast lands better forwards than backwards.

**What moves with it.**

- `docs/prep/03-cs326-2026-09-04-prep-borrowing…` (or its successor): add the
  `Drop`/RAII concept bullet, and drop it from the `04r` prep page.
- `utils/gen_exercises.py`, the `WHAT` blurb for both exercises, then
  regenerate `docs/assignments/exercises.md`.
- `docs/guides/rust-for-systems.md`: the exercise/topic map row for `03r`
  and `04r`.
- `04r`: remove Section 3 (`PageGuard`) and its three tests, and decide whether
  `page_align_up`/`MemRegion::page_list` stay. They should — see the next entry.

**Risk to weigh.** `03r` is already the densest of the early Rust exercises: it
carries `&`/`&mut`, slices, the aliasing rule, non-lexical lifetimes and a
lifetime-annotated struct. Adding `Drop` may push it past a session. If it does,
the thing to move out is the slice material, which `06r_collections` covers
again anyway — not the guard.

---

## Keep the page-arithmetic markers in `04r`, wherever `Drop` ends up

**Status:** proposed. Applied in F26 as part of the entry above.

`page_align_up` (xv6's `PGROUNDUP`, as a `const fn`) and `MemRegion::page_list`
(`kinit` in miniature) are `04r` material on their own terms: masking, `const
fn`, and a loop whose boundary condition is the entire lesson. They also give
`04r` its one marker that is longer than a single expression. Keep them even
after `PageGuard` moves to `03r`; `page_list` is then just a `Vec<usize>` the
`Pte` section can use, rather than the feedstock for a guard.

---

## What F26 actually did (2026-09-07)

`03r_borrowing` was already completed by students by the time this came up, so
the interim fix went into `04r_structs_impl`, which was not yet released (due
Thu Sep 10). `04r` grew from five `IMPLEMENT` markers to eleven:

- `page_align_up` and `MemRegion::page_list` in Section 1;
- a new Section 3 — `PageGuard<'a>`, holding one page borrowed from a free
  list, with `take`, `region`, `entry` and `impl Drop` as markers, and `pa`,
  `free_len` and `release` given;
- the preview `Context` section renumbered to Section 4.

The three sections now chain: a `MemRegion` produces a free list, the free list
produces a `PageGuard`, and the guard produces the `Pte` that maps its page —
so markers 9 and 10 are one call each into the student's own earlier code.

**Loose end from that change.** The Sep 3 lecture
(`02-…-structs-impl-and-const-fn.md`) does not mention `Drop`, and §9 "Where
This Lands" was updated to name the guard but the body of the lecture was not.
If `Drop` stays in `04r` next time, that lecture wants a short section on it; if
it moves to `03r` as proposed above, the Sep 1 ownership lecture already covers
it and nothing needs adding.
