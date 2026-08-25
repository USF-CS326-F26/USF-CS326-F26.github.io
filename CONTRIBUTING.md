# Authoring conventions for the CS 326 site

This file exists because the CS 315 and CS 631 sites do not have one. Their
conventions are real and consistent, but they live only in the artifacts, so
every new page is written by imitation and drifts a little. Write them down
here instead.

## Building

```bash
pip install -r requirements.txt
mkdocs serve          # http://127.0.0.1:8000, live reload
mkdocs build --strict # what CI runs
```

`--strict` fails the build on any broken internal link. That is deliberate and
should not be relaxed: with 25+ cross-linked lecture pages it is the only
thing keeping the site honest. If CI is red, it is almost always a link to a
page that was renamed or never written.

## Repository layout

```
mkdocs.yml                  site config and nav
requirements.txt            pinned, not floored
docs/
  index.md                  the schedule page — a Jinja template over schedule.yml
  schedule.yml              THE schedule. One file. Edit sessions here.
  syllabus.md  staff.md
  assignments/              per-exercise-group specs, practice sets, exam info
  guides/                   the reference layer
  lectures/                 NN-cs326-YYYY-MM-DD-topic.md + matching -slides.html
  solutions/                exam + practice-set solutions ONLY (never exercise code)
  stylesheets/extra.css     USF palette + the schedule table
  javascripts/              schedule.js, mermaid-init.js, mathjax.js
overrides/                  the external-links header bar and the footer
```

## The schedule

`docs/schedule.yml` is the single source of truth. `docs/index.md` renders it;
do not hand-edit the table.

```yaml
  - week: 7
    tuesday:
      date: "Oct 6"
      type: "lecture"        # lecture | lab | exam | holiday
      topic: "L13 Processes and the PCB"
      due: "ex03"            # optional
      links:                 # optional
        - text: "Practice Set 1"
          url: "/assignments/practice-set-01/"
```

Day keys are `tuesday`, `thursday`, `friday`. Holidays get a row with
`type: "holiday"` so the week still reads correctly.

`schedule.js` highlights the current week automatically by parsing the `date`
strings, so keep the `"Mon DD"` format exactly.

## Lecture pages

Filename: `{WW}-cs326-{YYYY-MM-DD}-{kebab-topic}.md`, where `WW` is the
zero-padded **week** number, repeated across the sessions in that week. Each
gets a matching `-slides.html`.

Every lecture page uses the same seven sections, in this order. The
consistency is the point — students learn where to look.

```markdown
# <Descriptive Title>

## Overview
<one dense paragraph, 100-180 words: what this session covers, the arc it
 sits in, and links to the exercise and guides it relates to>

## Learning Objectives
- 6-8 bullets, each starting with a verb (Explain, Describe, Trace, Derive,
  Implement, Decode, Distinguish)

## Prerequisites
- 4-6 bullets naming prior lectures, exercises, or guides

---

## 1. <Numbered Section>
## 2. <Numbered Section>
### <sub-heading>

---

## Key Concepts
| Concept | Definition | Example |    <- 3 columns, 10-12 rows

---

## Practice Problems
### Problem 1: <short title>
<prose + code>
<details>
<summary>Click to reveal solution</summary>
<worked solution>
</details>
                                        <- 5-6 problems

---

## Further Reading
- course-internal links first, then external

---

## Summary
1. **Bold lead-in.** One or two sentences.
                                        <- 8 numbered items
```

Target 4,400–5,900 words. **No YAML front matter** — the page starts with
`# Title` on line 1.

### The contract with exercise READMEs

This matters more than anything else on this page.

Each exercise already ships a `README.md` inside OSlings that teaches *how* to
do it: what to type, what the markers mean, what API to call. **The lecture
page must not repeat that.** The lecture carries the concept, the hardware,
the history, the comparison to xv6 and Linux, the diagrams, and the practice
problems.

The test: a lecture page should be worth reading by someone who never opens
the exercise, and the exercise should be doable by someone who skipped the
lecture — with a worse experience. If you find yourself writing the
implementation steps, stop; that belongs in the exercise.

## Formatting conventions

- **Diagrams are mermaid or ASCII art**, inline. No image files in lectures.
  Use a ```mermaid fence (the custom `mermaid-diagram` class is configured in
  `mkdocs.yml`).
- **Asides are blockquotes** (`> Key distinction: ...`), not admonitions.
  CS 315 uses only 5 `!!!` blocks across 36 lecture pages and 95 blockquote
  lines; match that ratio. Reserve `!!!` for genuine warnings.
- **Practice problem solutions go in `<details><summary>Click to reveal
  solution</summary>`.** This is the single most characteristic device on the
  site and students rely on it.
- **Code fences are tagged**: `rust`, `asm`, `bash`, `text`, `mermaid`.
  Terminal transcripts, register dumps, and ASCII diagrams are `text`.
- **Cite kernel code as `file.rs:NNN`**, the way the CS 631 octox lecture
  does. Read the source; do not cite from memory.
- **Tables for anything enumerable.** Registers, bit fields, flags, addresses.

## Things not to copy from CS 315 / CS 631

These are known defects in the older sites. They are already fixed here; do
not reintroduce them.

1. **No `polyfill.io`.** That domain was sold in 2024 and served malware.
2. **No Jekyll attr-list syntax.** `{:target="_blank"}` and `{: width="100" }`
   render as visible literal text in MkDocs. Use `{ ... }` without the colon,
   or a plain link.
3. **Do not fork `partials/header.html`.** CS 315 forked Material's entire
   stock header for a one-line change and it will drift on every upgrade.
4. **Pin dependencies.** `requirements.txt` uses `==`, not `>=`.
5. **Do not add plugins that nothing uses.** CS 315 enables `meta` and `tags`
   with no `.meta.yml` files and no `tags:` front matter anywhere.

## Solutions

`docs/solutions/` holds **exam and practice-set solutions only**.

Exercise solutions are never published. They live in the private instructor
repository, and students unlock one per exercise with `oslings solution <ex>`
after passing it. Publishing them would defeat the release gate that the whole
integrity model rests on.
