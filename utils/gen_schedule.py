"""Generate docs/schedule.yml for CS 326 Fall 2026.

`sessions()` below is the source of truth for dates, types, topics, and the
exercises each session releases. Links are attached automatically by matching
a row's date against the filenames, so they cannot drift as pages are added or
renamed:

  - an exercise row gets the Prep page dated that day (docs/prep/);
  - a lecture row gets the lecture page dated that day as "Lecture", plus its
    deck as "Slides" — every lecture page is dated the Tuesday it is presented;
  - an exam row gets the page dated that day, if any, as "Optional reading"
    (the Dec 8 final-review page, which is read, not lectured).

Nothing else is attached by date. A lecture presented on a different day from
the sessions it serves (week 9's on Oct 13, week 15's first half on Nov 24) is
linked from those sessions by hand in `sessions()` ("Lecture · given Oct 13").
Meeting summaries in docs/summaries/ are attached by date too, as are the
handwritten notes in docs/notes/; the Zoom recordings they go with are listed
in RECORDINGS below, since no local file names those.

`utils/check_links.py` checks the result: one Lecture link per lecture row,
every lecture page dated to a lecture or exam row, and more.

Other generators import this module (`from gen_schedule import sessions`), so
keep the table inside `sessions()` and the file writing inside `main()`.

Run from the site repo root:  python3 utils/gen_schedule.py
"""
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LECTURES = ROOT / "docs/lectures"
PREP = ROOT / "docs/prep"
SUMMARIES = ROOT / "docs/summaries"
NOTES = ROOT / "docs/notes"
SECTIONS = ("01", "02")
MONTHS = {m: i for i, m in enumerate(
    ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
DAY_ABBR = {"tuesday": "Tue", "thursday": "Thu", "friday": "Fri"}

# Zoom cloud recordings, keyed by (date, section). The meeting summaries in
# docs/summaries/ are found on the filesystem by date, the way Prep and lecture
# pages are, but a recording is only a URL Zoom hands back — nothing local
# names it — so add a line here when one is published.
RECORDINGS = {
    ("Sep 1", "02"): "https://usfca.zoom.us/rec/share/1hTUJ5B9GP5HyW-5fH52i0WyYJqYUuyfUgCh1ni-YercJgl0x5rdIJ3gq26h5oug.L_6UlW_im3llbIip?startTime=1788300688000",
}


def stamp(date_str):
    """"Oct 6" -> "2026-10-06"."""
    mon, day = date_str.split()
    return f"2026-{MONTHS[mon]:02d}-{int(day):02d}"


def prep_links(date_str):
    """[("Prep", url)] for the prep page written for `date_str`, if any."""
    return [("Prep", f"prep/{md.stem}/")
            for md in sorted(PREP.glob(f"*-cs326-{stamp(date_str)}-prep-*.md"))]


def rel(url):
    """Site-root-relative form of an internal URL; external URLs pass through."""
    return url if url.startswith("http") else url.lstrip("/")


def lecture_links(date_str, label="Lecture"):
    """[(label, url), ("Slides", url)] for the lecture page dated `date_str`.

    The deck is added only when a `-slides.html` sits beside the page (the
    Dec 8 reading has none). `main()` calls this for lecture rows ("Lecture")
    and exam rows ("Optional reading") only.
    """
    out = []
    for md in sorted(LECTURES.glob(f"*-cs326-{stamp(date_str)}-*.md")):
        out.append((label, f"lectures/{md.stem}/"))
        if (LECTURES / f"{md.stem}-slides.html").exists():
            out.append(("Slides", f"lectures/{md.stem}-slides.html"))
    return out


def section_resources(date_str):
    """{"01": {"recording": url, "notes": url, "summary": url}, ...} for `date_str`.

    Sections with nothing published yet are left out, so a session carries a
    Sec01/Sec02 line only once it has one of the three.
    """
    out = {}
    for sec in SECTIONS:
        res = {}
        if url := RECORDINGS.get((date_str, sec)):
            res["recording"] = url
        # Handwritten notes, exported from class: "CS326-02 2026-09-01 Topic.pdf".
        # The topic is free text, so match on the section and date only.
        pdfs = sorted(NOTES.glob(f"CS326-{sec} {stamp(date_str)} *.pdf"))
        if pdfs:
            res["notes"] = f"notes/{pdfs[0].name}"
        md = SUMMARIES / f"cs326-{sec}-{stamp(date_str)}-summary.md"
        if md.exists():
            res["summary"] = f"summaries/{md.stem}/"
        if res:
            out[sec] = res
    return out


def short(name):
    """"33k_paging" -> "33k"."""
    return name.split("_")[0]


def sessions():
    """The confirmed Fall 2026 calendar, one dict per class meeting.

    type: lecture | exercise | exam | holiday
      lecture   Tuesday: the week's lecture, ending with a walk-through of the
                Thursday and Friday Prep pages. The lecture page and deck dated
                that day attach as "Lecture" and "Slides".
      exercise  Thursday / Friday: an exercise session. Its Prep page attaches
                by date; its lecture is the Tuesday row's, except where a
                manual "Lecture · given <date>" link below says otherwise.
      exam      in-class exam: the two midterms (Thursday) and the final,
                which is given in the last Tuesday slot, not in finals week.
                A page dated that day attaches as "Optional reading".
      holiday   no meeting
    exercises: the long names released at the start of the session
    extra:     extra-credit exercises released the same day
    due:       derived — the short forms, e.g. "12c, 13c · 14c extra credit"
    """
    S = []

    def add(week, day, date, typ, topic, exercises=(), extra=(), links=None):
        exercises, extra = list(exercises), list(extra)
        due = ", ".join(short(n) for n in exercises)
        if extra:
            ec = ", ".join(short(n) for n in extra)
            due = f"{due} · {ec} extra credit" if due else f"{ec} extra credit"
            ec_topic = " · ".join(f"{short(n)} {'_'.join(n.split('_')[1:])}" for n in extra)
            topic = f"{topic} · extra credit {ec_topic}"
        S.append(dict(week=week, day=day, date=date, type=typ, topic=topic,
                      exercises=exercises, extra=extra, due=due or None,
                      links=links or []))

    L = lambda *pairs: [{"text": t, "url": u} for t, u in pairs]

    # Week 9 has no Tuesday (fall break), so its lecture is given the Tuesday
    # before, Oct 13, and both of its sessions link back to it.
    WEEK9 = "/lectures/09-cs326-2026-10-13-processes-context-switch-and-scheduling"
    WEEK9_LECTURE = (("Lecture · given Oct 13", f"{WEEK9}/"),
                     ("Slides · given Oct 13", f"{WEEK9}-slides.html"))
    # Week 15 has five exercises and one Tuesday, so its Thursday half is
    # given the Tuesday before Thanksgiving, Nov 24; Dec 3 links back to it.
    WEEK15A = "/lectures/15-cs326-2026-11-24-exec-and-file-descriptors"
    WEEK15A_LECTURE = (("Lecture · given Nov 24", f"{WEEK15A}/"),
                       ("Slides · given Nov 24", f"{WEEK15A}-slides.html"))

    # ---- Module 1 : Rust, commands, and the bridges to bare metal ---------
    add(1, 'tuesday', 'Aug 25', 'lecture', 'Building an Operating System, and Your First Rust',
        links=L(("Syllabus", "/syllabus/"), ("Setup", "/assignments/setup/"),
                ("Dev Setup", "/guides/dev-setup/")))
    add(1, 'thursday', 'Aug 27', 'exercise', 'Setup session · 00r hello_rust',
        exercises=['00r_hello_rust'],
        links=L(("Setup", "/assignments/setup/"), ("Dev Setup", "/guides/dev-setup/"),
                ("Using OSlings", "/guides/oslings-usage/")))
    add(1, 'friday', 'Aug 28', 'exercise', '01r control_flow',
        exercises=['01r_control_flow'],
        links=L(("Rust for Systems", "/guides/rust-for-systems/")))

    add(2, 'tuesday', 'Sep 1', 'lecture', 'Ownership and Borrowing',
        links=L(("In-class slides", "/inclass/week02-slides.html"),
                ("Code and output", "/inclass/week02-examples.html")))
    add(2, 'thursday', 'Sep 3', 'exercise', '02r ownership', exercises=['02r_ownership'])
    add(2, 'friday', 'Sep 4', 'exercise', '03r borrowing', exercises=['03r_borrowing'])

    add(3, 'tuesday', 'Sep 8', 'lecture', 'Structs, impl, Enums, and match',
        links=L(("In-class slides", "/inclass/week03-slides.html"),
                ("Code and output", "/inclass/week03-examples.html")))
    add(3, 'thursday', 'Sep 10', 'exercise', '04r structs_impl', exercises=['04r_structs_impl'])
    add(3, 'friday', 'Sep 11', 'exercise', '05r enums_match', exercises=['05r_enums_match'])

    add(4, 'tuesday', 'Sep 15', 'lecture', 'Collections, Traits, Errors, and Your First Command',
        links=L(("In-class slides", "/inclass/week04-slides.html"),
                ("Code and output", "/inclass/week04-examples.html")))
    add(4, 'thursday', 'Sep 17', 'exercise', '06r collections · 07r traits',
        exercises=['06r_collections', '07r_traits'])
    add(4, 'friday', 'Sep 18', 'exercise', '08r errors · 10c echo',
        exercises=['08r_errors', '10c_echo'],
        links=L(("ulib and Commands", "/guides/ulib-and-commands/")))

    add(5, 'tuesday', 'Sep 22', 'lecture', 'Streams of Bytes: cat, wc, and grep',
        links=L(("Code and output", "/inclass/week05-examples.html")))
    add(5, 'thursday', 'Sep 24', 'exercise', '11c cat', exercises=['11c_cat'])
    add(5, 'friday', 'Sep 25', 'exercise', '12c wc · 13c grep',
        exercises=['12c_wc', '13c_grep'], extra=['14c_head'],
        links=L(("Extra Credit", "/assignments/extra-credit/")))

    add(6, 'tuesday', 'Sep 29', 'lecture', 'Below Rust: Assembly, unsafe, and no_std',
        links=L(("Code and output", "/inclass/week06-examples.html")))
    add(6, 'thursday', 'Oct 1', 'exercise', '20a asm_bridge — QEMU deadline',
        exercises=['20a_asm_bridge'],
        links=L(("RISC-V", "/guides/riscv/"), ("QEMU and GDB", "/guides/qemu-gdb/")))
    add(6, 'friday', 'Oct 2', 'exercise', '21r unsafe_bridge · 30k kernel_basics',
        exercises=['21r_unsafe_bridge', '30k_kernel_basics'],
        links=L(("Memory Map", "/guides/memory-map/")))

    # ---- Module 2 : Build the kernel --------------------------------------
    add(7, 'tuesday', 'Oct 6', 'lecture', 'From Reset to Page Tables: Boot, the Free List, and Sv39',
        links=L(("Practice Set 1", "/assignments/practice-set-01/"),
                ("Code and output", "/inclass/week07-examples.html")))
    add(7, 'thursday', 'Oct 8', 'exercise', '31k boot · 32k physical_memory',
        exercises=['31k_boot', '32k_physical_memory'])
    add(7, 'friday', 'Oct 9', 'exercise', '33k paging', exercises=['33k_paging'],
        links=L(("Sv39 Paging", "/guides/sv39-paging/")))

    add(8, 'tuesday', 'Oct 13', 'lecture', "Week 9's lecture: Processes, the Context Switch, and Scheduling",
        links=L(("Exam Prep", "/guides/exam-prep/"),
                ("Practice Set 1", "/assignments/practice-set-01/")))
    add(8, 'thursday', 'Oct 15', 'exam', 'MIDTERM 1 — Module 1 + kernel through 33k paging',
        links=L(("Midterm 1", "/assignments/midterm-1/"), ("Exam Prep", "/guides/exam-prep/")))
    add(8, 'friday', 'Oct 16', 'holiday', 'No class — exam week')

    add(9, 'tuesday', 'Oct 20', 'holiday', 'Fall Break — no class')
    add(9, 'thursday', 'Oct 22', 'exercise', '34k processes', exercises=['34k_processes'],
        links=L(*WEEK9_LECTURE))
    add(9, 'friday', 'Oct 23', 'exercise', '35k context_switch · 36k scheduling',
        exercises=['35k_context_switch', '36k_scheduling'],
        links=L(*WEEK9_LECTURE))

    add(10, 'tuesday', 'Oct 27', 'lecture', 'Locks, Semaphores, and Turning the MMU On')
    add(10, 'thursday', 'Oct 29', 'exercise', '37k spinlocks · 38k semaphores',
        exercises=['37k_spinlocks', '38k_semaphores'])
    add(10, 'friday', 'Oct 30', 'exercise', '39k virtual_memory',
        exercises=['39k_virtual_memory'],
        links=L(("QEMU and GDB", "/guides/qemu-gdb/")))

    add(11, 'tuesday', 'Nov 3', 'lecture', 'Files, Boot Order, and Traps')
    add(11, 'thursday', 'Nov 5', 'exercise', '40k filesystem',
        exercises=['40k_filesystem'], extra=['41k_devices'],
        links=L(("Extra Credit", "/assignments/extra-credit/")))
    add(11, 'friday', 'Nov 6', 'exercise', '42k boot_to_life · 43k traps · 44k interrupts',
        exercises=['42k_boot_to_life', '43k_traps', '44k_interrupts'],
        links=L(("Withdraw deadline", "/syllabus/")))

    add(12, 'tuesday', 'Nov 10', 'lecture', 'The Console, the Shell, and User Mode',
        links=L(("rv6 Architecture", "/guides/rv6-architecture/"),
                ("Practice Set 2", "/assignments/practice-set-02/")))
    add(12, 'thursday', 'Nov 12', 'exercise', '45k console · 46k shell',
        exercises=['45k_console', '46k_shell'], extra=['47k_file_commands'],
        links=L(("Extra Credit", "/assignments/extra-credit/")))
    add(12, 'friday', 'Nov 13', 'exercise', '48k user_mode', exercises=['48k_user_mode'])

    add(13, 'tuesday', 'Nov 17', 'lecture', 'Midterm 2 Review',
        links=L(("Exam Prep", "/guides/exam-prep/"),
                ("Practice Set 2", "/assignments/practice-set-02/")))
    add(13, 'thursday', 'Nov 19', 'exam', 'MIDTERM 2 — 34k processes through 48k user mode',
        links=L(("Midterm 2", "/assignments/midterm-2/"), ("Exam Prep", "/guides/exam-prep/")))
    add(13, 'friday', 'Nov 20', 'holiday', 'No class — exam week')

    add(14, 'tuesday', 'Nov 24', 'lecture', "Week 15's first lecture: exec and File Descriptors")
    add(14, 'thursday', 'Nov 26', 'holiday', 'Thanksgiving — no class')
    add(14, 'friday', 'Nov 27', 'holiday', 'Thanksgiving — no class')

    add(15, 'tuesday', 'Dec 1', 'lecture', 'fork, wait, and the User Shell')
    add(15, 'thursday', 'Dec 3', 'exercise', '49k exec · 50k file_descriptors',
        exercises=['49k_exec', '50k_file_descriptors'],
        links=L(*WEEK15A_LECTURE))
    add(15, 'friday', 'Dec 4', 'exercise',
        '51k fork_wait · 52k userland · 53k ship_your_commands',
        exercises=['51k_fork_wait', '52k_userland', '53k_ship_your_commands'],
        extra=['54k_elf_loader'],
        links=L(("Extra Credit", "/assignments/extra-credit/"),
                ("Practice Set 3", "/assignments/practice-set-03/")))

    add(16, 'tuesday', 'Dec 8', 'exam',
        'FINAL EXAM — cumulative, weighted toward 49k–53k',
        links=L(("Final Exam", "/assignments/final/"),
                ("Exam Prep", "/guides/exam-prep/"),
                ("Practice Set 3", "/assignments/practice-set-03/")))
    return S


def session_label(s):
    """"Thu Oct 1" — the form the exercises table uses."""
    return f"{DAY_ABBR[s['day']]} {s['date']}"


def q(text):
    return '"' + str(text).replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    S = sessions()
    out = ['# CS 326 Fall 2026 Schedule Data',
           '# Generated by utils/gen_schedule.py — edit sessions() there, not this file.',
           '# The table in docs/index.md renders these rows.',
           'semester: "Fall 2026"',
           'course: "CS 326 Operating Systems"',
           '',
           '# Weekly schedule data',
           '',
           'weeks:', '']
    weeks = {}
    for s in S:
        weeks.setdefault(s['week'], []).append(s)
    attached = set()  # lecture page stems that made it onto a row

    for w in sorted(weeks):
        out.append(f'# === WEEK {w} ===')
        out.append(f'  - week: {w}')
        for s in weeks[w]:
            # Auto-discovered links first: Prep, then the lecture page and its
            # deck, then the manual links. Each lecture page is dated the
            # Tuesday it is presented, so it attaches to that row as the
            # "Lecture". An exam row's page (the Dec 8 final review) is
            # revision nobody lectures, so it is labeled "Optional reading".
            # Exercise and holiday rows get no page by date; the sessions a
            # lecture is given away from (Oct 22/23, Dec 3) link it by hand.
            auto = prep_links(s["date"])
            label = {"lecture": "Lecture",
                     "exam": "Optional reading"}.get(s["type"])
            if label:
                page = lecture_links(s["date"], label)
                auto += page
                attached.update(u.split("/")[1] for t, u in page if t == label)
            # Internal links are written relative to the site root (no leading
            # slash): docs/index.md sits at the root, so they resolve whether
            # the site is served at a domain root or under a repo subpath.
            links = [{"text": t, "url": rel(u)} for t, u in auto] + \
                    [{"text": l["text"], "url": rel(l["url"])} for l in s["links"]]
            out.append(f'    {s["day"]}:')
            out.append(f'      date: {q(s["date"])}')
            out.append(f'      type: {q(s["type"])}')
            out.append(f'      topic: {q(s["topic"])}')
            if s['exercises']:
                out.append(f'      exercises: [{", ".join(s["exercises"])}]')
            if s['extra']:
                out.append(f'      extra: [{", ".join(s["extra"])}]')
            if s['due']:
                out.append(f'      due: {q(s["due"])}')
            for sec, res in section_resources(s["date"]).items():
                out.append(f'      section_{sec}:')
                for key in ("recording", "notes", "summary"):
                    if key in res:
                        out.append(f'        {key}: {q(res[key])}')
            if links:
                out.append('      links:')
                for l in links:
                    out.append(f'        - text: {q(l["text"])}')
                    out.append(f'          url: {q(l["url"])}')
            out.append('')
        out.append('')

    (ROOT / 'docs/schedule.yml').write_text('\n'.join(out))

    teaching = [s for s in S if s['type'] != 'holiday']
    print(f"sessions written: {len(S)}  (teaching: {len(teaching)}, holidays: {len(S)-len(teaching)})")
    print("by type:", dict(Counter(s['type'] for s in teaching)))
    print("weeks:", len(weeks))
    resources = [section_resources(s['date']) for s in S]
    have = lambda key: sum(1 for r in resources for res in r.values() if key in res)
    pages = sorted(md.stem for md in LECTURES.glob("*.md"))
    stray = [p for p in pages if p not in attached]
    print(f"lecture pages attached: {len(attached)} of {len(pages)}")
    for p in stray:
        print(f"  ! {p}.md is not dated to a lecture or exam row, so no row links it")
    print(f"section resources: {have('recording')} recordings, "
          f"{have('notes')} note sets, {have('summary')} summaries")
    n_ex = sum(len(s['exercises']) for s in S)
    n_ec = sum(len(s['extra']) for s in S)
    print(f"exercises scheduled: {n_ex} core + {n_ec} extra credit")
    missing_prep = [s for s in S if s['type'] == 'exercise' and not prep_links(s['date'])]
    if PREP.is_dir() and any(PREP.glob('*.md')):
        print(f"exercise rows without a Prep page: {len(missing_prep)}")
    else:
        print("no docs/prep/ pages yet — Prep links will attach as they are written")


if __name__ == "__main__":
    main()
