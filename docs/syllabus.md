# CS 326 Operating Systems — Fall 2026

**4 units · University of San Francisco · Department of Computer Science**

| | |
|---|---|
| **Instructor** | Greg Benson |
| **Teaching Assistant** | Ankit Mukhopadhyay |
| **Term** | Fall 2026 — August 25 through December 9 |
| **Meetings** | Tuesday & Thursday (lecture / work), Friday (lab) |
| **Final exam** | December 11–17, in the registrar's assigned slot |

---

## Course Description

The design and implementation of operating systems: processes, threads,
scheduling, synchronization, interprocess communication, device drivers,
memory management, and file systems.

This offering teaches those topics by **building an operating system**. Over
the semester you implement `rv6`, a small Unix-like kernel for the RISC-V
architecture, written in Rust. By the end it boots on an emulated 64-bit
RISC-V machine, manages memory with page tables, schedules multiple processes,
handles interrupts and system calls, and runs a shell in user mode — and the
programs that shell runs are programs you wrote in the first month of the
course.

Nothing is a simulation. Every exercise compiles for real hardware and runs on
a real (emulated) machine.

## Learning Outcomes

After completing this course you will be able to:

1. Write systems software in Rust, including the `unsafe` subset needed to
   touch hardware, and explain what ownership and borrowing buy a kernel.
2. Explain the RISC-V privilege model and the calling convention, and read and
   write the assembly a kernel requires.
3. Implement physical memory allocation and Sv39 virtual memory, and translate
   an address by hand.
4. Implement context switching and a scheduler, and explain how one CPU is
   multiplexed across many processes.
5. Implement kernel synchronization primitives and reason about race
   conditions and deadlock.
6. Implement the trap path — exceptions, interrupts, and system calls — and
   trace a system call from user code to kernel and back.
7. Implement process creation, program loading, and file descriptors, and
   explain why Unix separates `fork` from `exec`.

## How This Course Works

**All programming work happens in class. There is no homework.**

Each session releases one exercise. You work it in the room, with the
instructor and TA present, and you run `oslings submit` before you leave —
whether or not it passes. That submit is your progress record and your
attendance.

| Day | Length | Shape |
|---|---|---|
| **Tuesday** | 1h45 | ~70 min lecture, then a guided start on the session's exercise |
| **Thursday** | 1h45 | Working session |
| **Friday** | 1h30 | Lab — working session |

One lecture is delivered live each week, on Tuesday. The second lecture page for
that week is posted with its slides and is **reading**, to be done before the
Thursday session — that reading and preparation is what your time outside of
class is for.

Exercises are delivered by **OSlings**, a command-line tool that stages each
exercise into your repository, runs its test, and gives progressive hints. An
exercise is released at the start of the session that works it and does not
exist in your repository before then.

### Nothing cascades

Every exercise's starting point contains the *reference* completed code for
all earlier exercises. If you do not finish an exercise — or miss a session
entirely — the next session still starts you from a working kernel.

**A missed exercise costs you that exercise. It cannot cost you the
semester.** This is the single most important thing to understand about the
course structure, and it is why you should keep coming even after a session
that went badly.

Your own work is never lost either: it is archived in `my-work/` and
`oslings goto <exercise>` returns you to exactly where you left off.

## Assignments and Grading

| Component | Weight |
|---|---|
| Attendance & in-class participation | 10% |
| Module 1 exercises (`r00`–`r09`, `c00`–`c04`, `a00`) | 10% |
| Module 2 exercises (`ex00`–`ex15`) | 20% |
| Module 3 exercises (`ex16`–`ex21`) | 15% |
| **Midterm 1** — Tuesday, October 13 | 10% |
| **Midterm 2** — Tuesday, November 24 | 15% |
| **Final exam** — December 11–17 | 20% |
| *Extra credit* (`ex22`, pipes, porting your commands, optional exercises) | *up to +4%* |

### How exercises are scored

Each exercise is graded independently by re-running its real test against the
snapshot you committed. Grading rebuilds and reboots your code, so a pass in
class is a pass at grading time and editing local state cannot manufacture
one.

| | Criterion | Score |
|---|---|---|
| **Pass** | The exercise's test is green | 100% |
| **Substantial** | Compiles, markers meaningfully attempted, archived in `my-work/` | 60% |
| **Absent** | Nothing submitted | 0% |

**The lowest two exercise scores in each module are dropped automatically.**
That is the no-questions-asked absence policy: it covers illness, interviews,
and the session where the toolchain simply would not cooperate. You do not
need to email about it.

### Make-up work

An exercise may be completed later, in office hours with the TA present, for
**75%** within one week of its session and **50%** after that, through the last
day of classes. Supervision is part of the policy, not an inconvenience — see
*Academic Integrity* below.

### Attendance

Attendance is recorded mechanically: a session counts as attended if a
`submit` commit lands from it. **Working and not finishing earns full
attendance credit.** The lowest three attendance days are dropped.

### Exams

Both midterms and the final are **in class, on paper, closed book**, with one
permitted reference: the course cheatsheet, which is published on this site
and which you may print. No electronic devices.

Exams test understanding rather than recall: tracing registers through a
context switch, decoding a page table entry, ordering the steps of a boot
sequence, explaining why a race condition occurs. Practice sets in the same
style are distributed and worked in class before each exam.

You must average C or better across the exams to pass the course.

### Letter grades

Assigned without rounding or curving:

| | | | | | |
|---|---|---|---|---|---|
| A 100–93.33 | A− <93.33–90 | B+ <90–86.67 | B <86.67–83.33 | B− <83.33–80 | C+ <80–76.67 |
| C <76.67–73.33 | C− <73.33–70 | D+ <70–66.67 | D <66.67–63.33 | D− <63.33–60 | F <60 |

C is the minimum grade for the CS major.

## Course Policies

### Academic integrity and the use of AI

This course is unusual, and the reason is worth stating plainly.

`rv6` is modeled on xv6 and Octox, which are public and are in the training
data of every large language model. An AI assistant can produce a working
version of nearly any exercise in this course instantly. **That is precisely
why all work happens in class.**

So the policy is simple, and the line is drawn at **the session**:

- **Exercises are done in the room, during the session, on your own keyboard.**
  Exercises are not released before the session that works them, so there is
  nothing to pre-solve.
- **During a session: no Internet and no AI assistant.** The lab network
  reaches GitHub and the Rust package registry — which `oslings` and `cargo`
  need — and nothing else. No chat window, no editor autocomplete that writes
  code for you, no phone. What you have in the room is the lecture notes, the
  guides on the course site, `oslings hint`, the compiler, and the instructor
  and TA.
- **Outside a session: use AI freely, and often.** Ask it to explain a concept,
  walk you through code you are reading, generate practice problems, or decode
  a compiler error. That is genuinely useful, it is where a good deal of your
  preparation should happen, and you are encouraged to do it.
- **Do not share your solutions with other students.** Explaining a concept to
  a classmate is good and welcome. Handing over code is not.

The restriction is stated as conduct rather than as a claim about the network,
because a phone hotspot defeats any network restriction and nobody is pretending
otherwise. Reaching the open Internet or using an AI assistant during a session
is an integrity violation whether or not anything stopped you.

You should only submit work you fully understand and can explain. The TA may
ask you to walk through code you submitted; being unable to is treated as an
integrity matter.

### Data recorded by OSlings

OSlings records, alongside each passing submission, when the session started,
how long the exercise took, and how many times you ran the test. This is
disclosed here rather than collected silently.

It is **not scored, not ranked, and not part of your grade**, and it does not
appear in any report the course produces. It exists so that if a question ever
arises about a submission there is context for a conversation. It is a
starting point for a discussion, never proof of anything.

### Laptops and the lab network

Sessions run on a restricted network that reaches GitHub and the Rust package
registry and not much else, so that `oslings update`, `oslings submit` and
`cargo` all work and very little else does. Keeping the room off the open
Internet is the rule, not just the router's default; see
[Academic Integrity and AI](guides/integrity-policy.md) for why it is written
that way round.

### Communication

Course questions go on Campuswire so everyone benefits from the answer.
Personal matters go by email.

---

## Texts and Resources

No textbook is required. All course material is on this site.

Recommended, and free:

- **[xv6: a simple, Unix-like teaching operating system](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf)** — MIT.
  `rv6` follows its structure closely; the book explains the *why* behind
  nearly every design decision you will implement.
- **[The Rust Programming Language](https://doc.rust-lang.org/book/)** — the
  official book. Chapters 1–10 cover everything Module 1 teaches.
- **[The RISC-V Instruction Set Manual, Volume II: Privileged Architecture](https://riscv.org/technical/specifications/)**
  — the authority on the CSRs and privilege model.
- **Operating Systems: Three Easy Pieces** — free online; excellent on
  concepts, though it uses a different codebase.

Run `rustup doc` for the standard library documentation offline.

---

## University Policies

**Students with disabilities.** If you have a disability for which
accommodations may be required, please contact Student Disability Services
(sds@usfca.edu, 415-422-2613) as early in the term as possible. Accommodations
are arranged through SDS and are not retroactive.

**Academic integrity.** The USF Honor Code applies to all work in this course.
See the [Academic Integrity policy](https://myusf.usfca.edu/academic-integrity/).

**Behavioral expectations.** All students are expected to behave in accordance
with the Student Conduct Code and other University policies.

**Counseling and Psychological Services (CAPS).** CAPS provides confidential,
free counseling to student members of our community. Personal counseling and
consultation are available at 415-422-6352.

**Confidentiality, mandatory reporting, and sexual assault.** As instructors,
one of our responsibilities is to help create a safe learning environment.
University policy requires that we disclose to the Title IX office any
information about sexual misconduct shared with us. Confidential resources are
available at CAPS and the Student Health Center.

**Learning, Writing, and Speaking Centers.** Free tutoring and academic support
are available to all students.

**USF Food Pantry.** Free groceries are available to any student who needs
them, no questions asked. Details on myUSF.
