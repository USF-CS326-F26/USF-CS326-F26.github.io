"""Generate docs/schedule.yml for CS 326 Fall 2026.

The session map below is the source of truth for dates, types, topics, and due
items. Links to the lecture page and slide deck for each session are attached
automatically by matching the date against the filenames in docs/lectures/, so
they cannot drift as lectures are added or renamed.

Run from the site repo root:  python3 utils/gen_schedule.py
"""
import re
from pathlib import Path

LECTURES = Path(__file__).resolve().parent.parent / "docs/lectures"
MONTHS = {m: i for i, m in enumerate(
    ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def lecture_links(date_str):
    """[(text, url), ...] for the lecture delivered on `date_str` ("Oct 6")."""
    mon, day = date_str.split()
    stamp = f"2026-{MONTHS[mon]:02d}-{int(day):02d}"
    out = []
    for md in sorted(LECTURES.glob(f"*-cs326-{stamp}-*.md")):
        out.append(("Lecture", f"/lectures/{md.stem}/"))
        if (LECTURES / f"{md.stem}-slides.html").exists():
            out.append(("Slides", f"/lectures/{md.stem}-slides.html"))
    return out


# (week, day, "Mon DD", type, topic, due, links)
# type: lecture | work | lab | exam | holiday
#   lecture  Tuesday: ~70 min lecture, then a guided start on the exercise
#   work     Thursday: working session; that week's lecture page is the reading
#   lab      Friday: working session
S = []
def add(week, day, date, typ, topic, due=None, links=None):
    S.append(dict(week=week, day=day, date=date, type=typ, topic=topic, due=due, links=links or []))

L = lambda *pairs: [{"text": t, "url": u} for t, u in pairs]

# ---- Module 1 : Rust, commands, assembly ----------------------------------
add(1,'tuesday','Aug 25','lecture','L01 Building an Operating System',None,
    L(("Lab 00 Setup","/assignments/lab00-setup/"),("Dev Setup","/guides/dev-setup/"),("Syllabus","/syllabus/")))
add(1,'thursday','Aug 27','work','Work session · read L02 Rust I: Values, Types, Control Flow','Lab 00 setup checkpoint',
    L(("r00 · r01","/assignments/exercises/"),("Rust for Systems","/guides/rust-for-systems/")))
add(1,'friday','Aug 28','lab','Lab: Ownership and moves','r00, r01',
    L(("Using OSlings","/guides/oslings-usage/")))
add(2,'tuesday','Sep 1','lecture','L03 Ownership, Borrowing, and Lifetimes','r02')
add(2,'thursday','Sep 3','work','Work session · read L04 Structs, impl, and const fn','r03')
add(2,'friday','Sep 4','lab','Lab: Enums, Option, and match','r04, r05')
add(3,'tuesday','Sep 8','lecture','L05 Collections, Traits, and Errors','r06')
add(3,'thursday','Sep 10','work','Work session · read L06 Traits and the ulib façade','r07, r08')
add(3,'friday','Sep 11','lab','Lab: echo and cat — your first commands',None,
    L(("ulib and Commands","/guides/ulib-and-commands/")))
add(4,'tuesday','Sep 15','lecture','L07 Buffers, Bytes, and Line-Oriented I/O','c00, c01')
add(4,'thursday','Sep 17','work','Work session · read L08 RISC-V Registers and the Calling Convention','c02, c03, c04',
    L(("RISC-V","/guides/riscv/")))
add(4,'friday','Sep 18','lab','Lab: the assembly bridge — add3, bytecopy, baby_swtch','a00')

# ---- Module 2 : Build the kernel from scratch ------------------------------
add(5,'tuesday','Sep 22','lecture','L09 Leaving std: no_std and Bare-Metal Rust','r09',
    L(("Unsafe Rust and no_std","/guides/rust-unsafe-nostd/")))
add(5,'thursday','Sep 24','work','Work session · read L10 Boot: From Reset to kmain','ex00',
    L(("Memory Map","/guides/memory-map/")))
add(5,'friday','Sep 25','lab','Lab: the boot sequence','ex01')
add(6,'tuesday','Sep 29','lecture','L11 Physical Memory and the Free List',None)
add(6,'thursday','Oct 1','work','Work session · read L12 Virtual Memory I: Sv39 Page Tables','ex02',
    L(("Sv39 Paging","/guides/sv39-paging/")))
add(6,'friday','Oct 2','lab','Lab: the page table walk',None)
add(7,'tuesday','Oct 6','lecture','L13 Processes and the PCB','ex03',
    L(("Practice Set 1","/assignments/practice-set-01/")))
add(7,'thursday','Oct 8','work','Work session · Practice Set 1 review + processes','ex04')
add(7,'friday','Oct 9','lab','Lab: context switch and the scheduler','ex05')
add(8,'tuesday','Oct 13','exam','MIDTERM 1 — Module 1 + ex00–ex04',None,
    L(("Exam Prep","/guides/exam-prep/")))
add(8,'thursday','Oct 15','work','Work session · read L14 The Context Switch and the Scheduler','ex06')
add(8,'friday','Oct 16','lab','Lab: spinlocks',None)
add(9,'tuesday','Oct 20','holiday','Fall Break — no class')
add(9,'thursday','Oct 22','work','Work session · read L15 Locks, Semaphores, and the Kernel Heap','ex07')
add(9,'friday','Oct 23','lab','Lab: Debugging rv6 with QEMU and GDB — catch-up','ex08',
    L(("QEMU and GDB","/guides/qemu-gdb/")))
add(10,'tuesday','Oct 27','lecture','L16 Virtual Memory II: Turning the MMU On','ex09')
add(10,'thursday','Oct 29','work','Work session · read L17 Filesystems, Devices, and the Boot Sequence','ex10')
add(10,'friday','Oct 30','lab','Lab: boot to life — cargo run boots rv6','ex11, ex12')
add(11,'tuesday','Nov 3','lecture','L18 Traps, Privilege Modes, and Interrupts',None)
add(11,'thursday','Nov 5','work','Work session · read L19 Device Interrupts, the PLIC, and the Console','ex13')
add(11,'friday','Nov 6','lab','Lab: the interrupt-driven console','ex14, ex15',
    L(("Withdraw deadline","/syllabus/")))

# ---- Module 3 : Extend a complete kernel -----------------------------------
add(12,'tuesday','Nov 10','lecture','L20 Shells, and the Module 2 → 3 handoff',None,
    L(("rv6 Architecture","/guides/rv6-architecture/")))
add(12,'thursday','Nov 12','work','Work session · read L21 File Commands over a Filesystem API','ex16')
add(12,'friday','Nov 13','lab','Lab: touch, cat, echo >, rm, rmdir','ex17')
add(13,'tuesday','Nov 17','lecture','L22 User Mode I: The Wall, Trampoline, Trapframe',None,
    L(("Practice Set 2","/assignments/practice-set-02/")))
add(13,'thursday','Nov 19','work','Work session · read L23 User Mode II: System Calls',None)
add(13,'friday','Nov 20','lab','Lab: user mode (2 of 2) + Practice Set 2 review','ex18')
add(14,'tuesday','Nov 24','exam','MIDTERM 2 — Module 2 + ex16–ex18')
add(14,'thursday','Nov 26','holiday','Thanksgiving — no class')
add(14,'friday','Nov 27','holiday','Thanksgiving — no class')
add(15,'tuesday','Dec 1','lecture','L24 exec, File Descriptors, fork and wait',None)
add(15,'thursday','Dec 3','work','Work session · read L25 exec as a System Call, and Userland','ex19, ex20')
add(15,'friday','Dec 4','lab','Lab: fork/wait and the multi-process scheduler','ex21',
    L(("Practice Set 3","/assignments/practice-set-03/")))
add(16,'tuesday','Dec 8','lecture','L26 Pipes, the Payoff, and Final Review','ex22 · extra credit',
    L(("Extra Credit","/assignments/extra-credit/")))

# ---------------------------------------------------------------------------
out = ['# CS 326 Fall 2026 Schedule Data',
       '# Generated — edit sessions here, the table in docs/index.md renders them.',
       'semester: "Fall 2026"',
       'course: "CS 326 Operating Systems"',
       '',
       '# Weekly schedule data',
       '',
       'weeks:', '']
weeks = {}
for s in S:
    weeks.setdefault(s['week'], []).append(s)

for w in sorted(weeks):
    out.append(f'# === WEEK {w} ===')
    out.append(f'  - week: {w}')
    for s in weeks[w]:
        # Prepend the auto-discovered lecture links for this date.
        s["links"] = [{"text": t, "url": u} for t, u in lecture_links(s["date"])] + s["links"]
        out.append(f'    {s["day"]}:')
        out.append(f'      date: "{s["date"]}"')
        out.append(f'      type: "{s["type"]}"')
        out.append(f'      topic: "{s["topic"]}"')
        if s['due']:
            out.append(f'      due: "{s["due"]}"')
        if s['links']:
            out.append('      links:')
            for l in s['links']:
                out.append(f'        - text: "{l["text"]}"')
                out.append(f'          url: "{l["url"]}"')
        out.append('')
    out.append('')

open('docs/schedule.yml','w').write('\n'.join(out))

teaching = [s for s in S if s['type'] != 'holiday']
print(f"sessions written: {len(S)}  (teaching: {len(teaching)}, holidays: {len(S)-len(teaching)})")
from collections import Counter
print("by type:", dict(Counter(s['type'] for s in teaching)))
print("weeks:", len(weeks))
