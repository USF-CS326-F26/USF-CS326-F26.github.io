# CS 326 Operating Systems — Fall 2026

**4 units · University of San Francisco · Department of Computer Science**

| | |
|---|---|
| **Instructor** | Greg Benson |
| **Teaching Assistant** | Ankit Mukhopadhyay |
| **Term** | Fall 2026 — August 25 through December 8 |
| **Meetings** | Tuesday 1h45 (lecture) · Thursday 1h45 (exercise session) · Friday 1h30 (exercise session) |
| **Final exam** | Tuesday, December 8, in class — the last day of the term |

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

**Tuesday is lecture. Thursday and Friday are exercise sessions, and the
programming happens there, in the room.** Your time outside class is for
reading.

| Day | Length | Shape |
|---|---|---|
| **Tuesday** | 1h45 | Lecture. Ends with a short walk-through of Thursday's Prep page. |
| **Thursday** | 1h45 | Exercise session |
| **Friday** | 1h30 | Exercise session |

One lecture is delivered live each week, on Tuesday. The second lecture page
for that week is posted with its slides and is **reading**.

Every exercise session has a **Prep page**, linked from its row on the
[schedule](index.md). It says what you will build, which lecture sections and
guides to reread, and what to check that you understand before you arrive.
**Read the Prep page before class.** It is the bridge between the lecture and
the exercise: a student who has read it spends the session writing code, and a
student who has not spends it reading.

Exercises are delivered by **OSlings**, a command-line tool that stages each
exercise into your repository, runs its test, and gives hints. An exercise is
released at the start of the session that works it and does not exist in your
repository before then. Before you leave the room you run `oslings submit`,
whether or not the exercise passes — that submit is your record of the
session. See [Using OSlings](guides/oslings-usage.md) and the
[Setup](assignments/setup.md) page for the first session.

Sessions run on their own Wi-Fi, **cs326**. You sign in to it once per laptop —
join the network, open <http://signin.cs326>, and sign in with your USF Google
account. After that it recognizes your laptop and there is nothing to do at the
start of a session. See [The Classroom Network](guides/classroom-network.md).

Exercise work happens only while connected to that network. You complete an
exercise in the classroom during its session or, if you did not finish, at a
**make-up session** — office hours with the instructor or TA, connected to the
same **cs326** network — before the next exercise session begins. Exercise code
written anywhere else earns no credit.

Your own work is archived in `my-work/`, and `oslings goto <name>` returns you
to it.

## Assignments and Grading

| Component | Weight |
|---|---|
| Module 1 exercises (`00r`–`21r`: Rust, commands, bridges to bare metal) | 20% |
| Module 2 exercises (`30k`–`53k`: the kernel) | 30% |
| **Midterm 1** — Thursday, October 15 | 15% |
| **Midterm 2** — Thursday, November 19 | 15% |
| **Final exam** — Tuesday, December 8 | 20% |
| *Extra credit* (`14c`, `41k`, `47k`, `54k`, `55k`) | *up to +3%* |

### How exercises are scored

Each exercise is graded independently by re-running its real test against the
snapshot you committed. Grading rebuilds and reboots your code, so a pass in
class is a pass at grading time and editing local state cannot manufacture
one.

| | Criterion | Score |
|---|---|---|
| **Pass** | The test is green in the `oslings submit` you ran during the session | 100% |
| **Completed at a make-up session** | Not passing in the session; you finish it at office hours with the instructor or TA, connected to the **cs326** network, **before the next exercise session begins**. Run `oslings submit` there. | 75% |
| **Substantial** | Submitted from the session: compiles, markers meaningfully attempted, test not green | 50% |
| **Nothing submitted** | Nothing by the time the next session begins | 0% |

The lowest two exercise scores in each module are dropped. The make-up session
is the only make-up path; exercise work done off the classroom network earns no
credit.

### Solutions

The reference solution for an exercise is released with the next exercise —
the point at which its make-up window closes — into `exercises/<name>/solution/` in your
repository; `oslings solution <name>` prints it. Before that it exists in no
repository you can fetch. Exam and practice-set solutions are posted on the
site under [Solutions](solutions/index.md).

### Exams

All three exams are given in class. The midterms fall on a **Thursday** —
October 15 and November 19 — in the Thursday session's slot, and there is no
Friday session in an exam week. The final is on **Tuesday, December 8**, the
last day of class, in the Tuesday slot. **There is no exam during finals
week.**

| Exam | Covers |
|---|---|
| **Midterm 1** — Thursday, October 15 | Module 1 (`00r`–`21r`) and the kernel through paging (`30k`–`33k`) |
| **Midterm 2** — Thursday, November 19 | Processes (`34k`) through user mode (`48k`) |
| **Final** — Tuesday, December 8 | Cumulative, weighted toward `49k`–`53k` |

All three are **on paper, closed book**, with one permitted reference: the
course cheatsheet, which is published on this site and which you may print.
No electronic devices.

Exams test understanding rather than recall: tracing registers through a
context switch, decoding a page table entry, ordering the steps of a boot
sequence, explaining why a race condition occurs. Practice sets in the same
style are distributed before each exam.

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
why the programming happens in class.**

So the policy is simple, and the line is drawn at **the session**:

- **Exercises are done in the room, during the session, on your own keyboard.**
  Exercises are not released before the session that works them, so there is
  nothing to pre-solve.
- **During a session: no Internet and no AI assistant.** The classroom network
  reaches GitHub, the Rust toolchain, the Rust documentation — the Book, Rust
  by Example, the standard library, rustlings and the playground — and this
  site. Very little else, and every AI assistant is blocked by name. No chat
  window, no editor autocomplete that writes code for you, no phone. What you
  have in the room is the lecture notes, the guides on the course site,
  `oslings hint`, the compiler, and the instructor and TA. The full list is on
  [The Classroom Network](guides/classroom-network.md).
- **Hints are limited.** `oslings hint` gives two hints per exercise. The third
  is never released.
- **Outside a session: use AI freely, and often.** Ask it to explain a concept,
  walk you through code you are reading, generate practice problems, or decode
  a compiler error. That is genuinely useful, it is where a good deal of your
  preparation should happen, and you are encouraged to do it.
- **Finishing an unfinished exercise happens at a make-up session**, on the
  classroom network, under the same rules: your own work, which you can explain
  line by line.
- **Do not share your solutions with other students.** Explaining a concept to
  a classmate is good and welcome. Handing over code is not.

The restriction is stated as conduct rather than as a claim about the network,
because a phone hotspot defeats any network restriction and nobody is pretending
otherwise. Reaching the open Internet or using an AI assistant during a session
is an integrity violation whether or not anything stopped you.

You should only submit work you fully understand and can explain. The TA or
instructor may ask you to walk through code you submitted; being unable to is
treated as an integrity matter.

### Data recorded by OSlings

OSlings records, alongside each passing submission, when the session started,
how long the exercise took, and how many times you ran the test. This is
disclosed here rather than collected silently.

It is **not scored, not ranked, and not part of your grade**, and it does not
appear in any report the course produces. It exists so that if a question ever
arises about a submission there is context for a conversation. It is a
starting point for a discussion, never proof of anything.

### Data recorded by the class server

When you sign in to the `cs326` network, the classroom router stores your name,
your USF email and your GitHub username — the first two supplied by Google when
you sign in, the third from the roster you filled in at the start of term —
together with that laptop's network address. While you are connected during a
session it records that the laptop was connected, and for how long.

That is the whole list. No browsing history and no page contents are kept: the
connections are encrypted, and nothing about what you visit is stored.

**It is not scored, not ranked, and not part of your grade.** There is no
attendance component in this course; the table above is the whole grade. It
exists so that the exercise can be released to the room, and so that if a
question arises later about a session there is a record of who was on the
network.

You may ask to see your own record, and to have it deleted, at any time.
Registrations and connection logs are erased at the end of the semester.

### Laptops and the classroom network

Sessions run on a restricted network that reaches GitHub, the Rust toolchain and
documentation, and this site — so that `oslings update`, `oslings submit` and
`cargo` all work and very little else does. You sign in to it once per laptop,
and it recognises you after that.

[The Classroom Network](guides/classroom-network.md) covers signing in, the full
list of what is reachable, what the class server records about you, and what to
do when it does not work. Keeping the room off the open Internet is the rule,
not just the router's default; see [Academic Integrity and AI](guides/integrity-policy.md)
for why it is written that way around.

### Communication

Course questions go on [Zulip](https://usfca-cs326-f26.zulipchat.com/) so
everyone benefits from the answer.
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

Optional Rust practice, for early finishers and anyone who wants more
repetitions than the exercises give:

- **[Rustlings](https://github.com/rust-lang/rustlings)** — small exercises
  that run from the command line, in the same spirit as OSlings.
- **[100 Exercises To Learn Rust](https://rust-exercises.com/100-exercises/)**
  — a test-driven tour of the language, one concept at a time.

Neither is required or graded.

Run `rustup doc` for the standard library documentation offline — faster than
the network, and it works anywhere. `doc.rust-lang.org` is reachable from the
classroom network too.

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
