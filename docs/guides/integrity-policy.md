# Academic Integrity and AI

This page is the long version of the integrity policy in the syllabus — the
reasoning, not just the rule. Read it once in week one. It explains why the
programming in this course happens in the room, what you are positively
encouraged to use AI for, what OSlings records about your sessions and why,
and what happens when you miss a session or do not finish in it. If you are
trying to decide whether something you are about to do is allowed, the tables
below are the short answer.

## The uncomfortable fact this course is built around

`rv6` is modeled on [xv6](https://pdos.csail.mit.edu/6.828/2023/xv6/) and on
Octox. Both are public, both have been on GitHub for years, and both are in the
training data of every large language model you have access to. A model can
produce a working page allocator, context switch, or `fork` for a kernel of this
shape in seconds, without you.

That is not a suspicion about you. It is a fact about the material, and
pretending otherwise would insult everyone in the room. It is also **precisely
why the programming happens in class**. If the exercises went home they would
be an honor-system exam with the answers already published, and the only
students disadvantaged would be the ones who did the work themselves. Doing the
work in the session removes the dilemma instead of policing it.

The corollary matters as much: because the structure carries the integrity, you
are not under individual suspicion.

## The rules

| | |
|---|---|
| **Where** | Exercises are worked in the session, in the room, on your own keyboard. |
| **When** | During the session. An exercise is released at the start of the session that works it, so there is nothing to pre-solve. |
| **What** | During a session: no Internet beyond GitHub and the package registry, and no AI assistant. |
| **Whose** | The code you submit is yours, and you can explain any line of it. |

### AI: it depends entirely on when

The dividing line is **the session**, not the tool and not the question.

| Outside a session — encouraged | During a session — not |
|---|---|
| "Explain what an ASID is and why Sv39 has one." | Any AI assistant, for any purpose |
| "Walk me through this `unsafe` block I am reading." | Editor autocomplete that writes code for you |
| "What does this borrow-checker error mean?" | Pasting an exercise README, or an error, into a chat window |
| "Give me five practice problems on page-table decoding." | A browser tab open to anything but the docs you were given |
| "Compare `Cell`, `RefCell`, and `UnsafeCell`." | A phone doing any of the above |

**Outside the session, use AI freely and often.** Ask it to explain a concept,
walk you through code you are reading, decode a compiler error, generate practice
problems. It is genuinely good at that — available at 2am, infinitely patient
with follow-up questions — and the reading and preparation you do between
sessions is where most of that happens. None of it is discouraged. Some of it is
the assignment.

**During the session, you work with what is in front of you**: the lecture notes,
the Prep page, the guides on this site, `oslings hint`, the compiler, and the two
people paid to be in the room with you. Nothing else.

The reason for the line is not suspicion, and it is not that asking a model to
explain something is wrong — outside the session it is encouraged on this very
page. It is that the exercises are small, the sessions are short, and a model
that is *right there* will answer before you have finished being confused. Being
confused for four minutes and then not being confused is the entire mechanism by
which this material goes in. The room exists to protect those four minutes.

### Classmates: same shape

Explaining a concept to someone next to you is good and welcome — talk about how
the scheduler picks the next process, draw the page table on the whiteboard,
argue about lock ordering. Handing over your code is not, in either direction,
including "just to look at". A person who reads your `swtch` and then writes
their own from memory has learned something. A person who copies it has not, and
you have taken that from them.

Progressive hints exist for exactly this reason. `oslings hint` gives you the
next nudge without giving you the answer: two hints are released per exercise,
and the third — the one that spells out the code — is never released. See
[Using OSlings](oslings-usage.md). Asking the TA or the instructor is always in
bounds and never counts against you.

## Why exercises are not released early

Not a date, not a flag, not an honor request. An unreleased exercise **exists in
no commit you can fetch**. The course repository gains one `exercises/<name>/`
directory and one `info.toml` block at the start of the session that works it,
and you pick it up with `oslings update`. Before that moment there is nothing in
your repository to read ahead, and nothing to spoof.

```text
instructor repo (private, every exercise + every solution)
        │  oslings release <name>   ← at the start of your session
        ▼
course repo (public read; each session adds the new exercises
        │                and the solutions whose deadline has passed)
        │  oslings update
        ▼
your private repo
```

This design is deliberate about the AI problem: a skeleton leaked early would be
an AI-solvable skeleton, so absence is the only gate that actually holds. The
same gate holds solutions back. The reference solution for an exercise is
released with the next exercise, after its completion deadline, into
`exercises/<name>/solution/`, and `oslings solution <name>` prints it. Until
then it is in no repository you can clone — see [Solutions](../solutions/index.md).

## The classroom network

Sessions run on a restricted network. GitHub and the Rust toolchain are
reachable, because `oslings update` and `oslings submit` need the first and
`cargo` needs the second. So is the Rust documentation — the Book, Rust by
Example, the standard library, rustlings and the playground — and this site.
Very little else is, and **every AI assistant is blocked by name**, GitHub
Copilot included.

You sign in to that network once per laptop: join **cs326**, open
<http://signin.cs326>, and sign in with your USF Google account. After that it
recognises your laptop. [The Classroom Network](classroom-network.md) has the
full list of what is reachable, what the class server records, and what to do
when it does not work.

`rustup doc` still opens the standard library offline and is faster than the
network. The guides on this site were written so that the restriction costs you
nothing.

**The restriction is not airtight, and this page is not going to pretend it is.**
A laptop with a phone hotspot defeats it completely, and no router configuration
can detect a second interface.

Which is exactly why the rule is written as conduct rather than as a claim about
the network. **Reaching the open Internet during a session — by hotspot, by
phone, by anything — or using an AI assistant during a session, is an academic
integrity violation**, whether or not the network stopped you. The router is a
convenience that saves you from having to resist a browser tab. The rule is the
rule.

## What OSlings records

Disclosed here rather than collected quietly. When an exercise passes, OSlings
writes `submissions/<name>/oslings-meta.toml` next to your snapshotted source
(`snapshot_submission` in `oslings-cli/src/model.rs`):

```toml
exercise = "37k_spinlocks"
passed_at = "2026-10-29T18:42:11Z"
passed_at_unix = 1793299331
difficulty = "guided"
hints_used = 2
session_started_unix = 1793295802
elapsed_secs = 3529
test_runs = 14
```

| Field | Meaning |
|---|---|
| `session_started_unix` | When you first ran the test for this exercise |
| `elapsed_secs` | From that first run to the pass |
| `test_runs` | How many times the harness ran |
| `hints_used` | How many hints you revealed |

The clock starts on your first test run, not on the wall clock of the session
(`State::note_test_run` in `model.rs`), which is why a slow start costs you nothing.

**This is never scored, never ranked, and appears in no report the course
produces.** It is not a productivity metric, and a long `elapsed_secs` with a
high `test_runs` is what a hard exercise honestly looks like. It exists so that
if a question ever arises about one submission, there is context for a
conversation — a starting point for a discussion, never proof of anything.

You can read the file; it is in your own repository. Editing it changes nothing,
because grading re-runs the real harness against your snapshotted source rather
than trusting any recorded state (`stage_from_dir` in `model.rs`, called by `oslings grade`). See
[Git and Submission](git-and-submission.md) for what else lands in your repo.

## Understanding what you submit

Submit only work you can explain. The TA or instructor may ask you to walk
through code you turned in — this is normal, it happens to people who are doing
fine, and it is the conversation you would have in an interview. Not being able
to explain your own submission is treated as an integrity matter, and it is the
one signal that does not depend on any of the machinery above.

## Missing a session

Missing class is not an integrity problem. Here is what happens to the
exercise.

| Situation | What happens |
|---|---|
| Unfinished in class | Run `oslings submit` before you leave anyway: a compiling, meaningfully attempted exercise scores **50%**. Get the test green by the deadline — Thursday exercises by Thursday 11:59 pm, Friday exercises by Monday 11:59 pm — run `oslings submit` again, and it scores **75%**. |
| Missed the session | The exercise was released at the start of the session; `oslings update` fetches it. Pass it by the same deadline for **75%**. After the deadline it scores 0. |
| Resuming old work | `oslings goto <name>` restores your own work from `my-work/`, exactly as you left it. |

There is no supervised make-up. Finishing after class is on your honor, and the
same integrity rules apply: your own work, explainable line by line.
