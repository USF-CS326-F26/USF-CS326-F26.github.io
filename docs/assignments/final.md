# Final Exam

**December 11–17 — in the registrar's assigned slot**

Check the official final exam schedule for the exact date, time, and room. It
is set by the registrar, not by the course.

## Format

Pencil and paper, closed book. One permitted reference: the
[Cheatsheet](../guides/cheatsheet.md), printed. No electronic devices.

Worth 20% of the course grade.

## Scope

**Cumulative, weighted toward `49k`–`53k`.** Everything from both midterms may
appear as a building block. The new material — and the bulk of the exam — is:

- **`exec` and program loading**: building a fresh address space, copying the
  image, mapping a stack, pushing `argv`, and pointing the trapframe at the
  entry point
- **File descriptors**: the fd as an unforgeable capability the kernel
  translates; the per-process fd table vs the system-wide open-file table; why
  sharing an offset between them makes `dup` and inheritance work; fds 0/1/2;
  reference counting
- **`fork`, `exit`, `wait`**: the call that returns twice; what a child
  inherits vs copies; zombies and reaping; the process tree and reparenting;
  why `wait` exists
- **`fork` + `exec` together**: why Unix splits process creation in two, and
  what that split makes possible that a single `spawn` would not
- **Userland**: `init` as pid 1, and what it means for the shell to be an
  ordinary unprivileged program
- **Pipes**, at the design level only: a bounded ring buffer behind two
  descriptors; blocking; how `a | b` falls out of fork + dup + exec. `55k_pipes`
  is extra credit and no question depends on having built it

## The question you should expect

There is always one long question that walks a single operation through every
layer of the system. Past form: *trace `rv6$ ls` from the keypress that
finishes the line to the moment `ls` exits*, naming at each step which
component acts, which CSR or data structure is involved, and what the
alternative would have cost.

Prepare for it by being able to tell that story out loud. If you can narrate
the whole path — console interrupt, line assembly, shell read, `fork`, `exec`,
address space construction, `sret` into user mode, the `write` syscall,
`exit`, `wait` — you are ready for the exam regardless of what else is on it.

## How to prepare

1. Do [Practice Set 3](practice-set-03.md) on paper. It is built from the
   final's material specifically.
2. Reread [rv6 Architecture](../guides/rv6-architecture.md) end to end. It is
   the single best revision document in the course.
3. Boot your own kernel and drive it. Being able to picture what actually
   happens when you type at the prompt is worth more than another read-through.
4. Skim [Key Concepts](../guides/key-concepts.md) as a final checklist.
