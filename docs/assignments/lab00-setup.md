# Lab 00 — Setup

**Due: end of Thursday, August 27**

By the end of this lab you will have your own private repository, a working
toolchain, and your first commit pushed. Everything after this depends on it.

Budget about 45 minutes. If something breaks, that is expected — the
instructor and TA are in the room, and there is a troubleshooting table at the
bottom of the [Dev Setup guide](../guides/dev-setup.md).

## What you need first

- A laptop running **macOS**, **Linux**, or **Windows with WSL2**. (Native
  Windows will not work; install WSL2 and use Ubuntu inside it.)
- A **GitHub account**.
- A terminal you are comfortable opening.

## 1. Install Rust

If you do not already have `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Then restart your terminal, or run `source "$HOME/.cargo/env"`. Check it:

```bash
rustc --version
```

## 2. Create your repository

On github.com, create a **new repository**:

- Name it exactly **`oslings-<your-github-username>`** — for example
  `oslings-jsmith`. The grading tools find your repo by this name.
- Make it **Private**.
- Do **not** add a README, .gitignore, or license. It must start empty.

Then, under **Settings → Collaborators**, add **both** the instructor and the
TA. If we cannot read your repository, we cannot grade it.

## 3. Clone the course repository

```bash
git clone https://github.com/USF-CS326-F26/oslings-course.git oslings
cd oslings
```

This is the shared course repository. It is where exercises arrive from.

## 4. Run the setup script

```bash
./setup.sh
```

This installs the Rust nightly toolchain, the `riscv64gc-unknown-none-elf`
target on both toolchains, the `rust-src` and `llvm-tools` components, offers
to install QEMU, and builds the `oslings` command.

It is safe to re-run at any time.

## 5. Check your environment

```bash
oslings doctor
```

Every line should be green. If any is not, the message tells you the exact
command that fixes it. **Do not move on until this is clean** — or, if only
the QEMU lines are red, see the note below.

!!! note "If QEMU will not install today"
    You are not blocked. Every exercise for the first four weeks runs as plain
    `cargo test` on your own machine — no QEMU, no kernel. Flag it to the TA
    and keep going; we will sort it out during a lab.

    The hard deadline for a working QEMU is **Friday, September 18**, when the
    assembly bridge exercise needs it.

## 6. Point this clone at your own repository

```bash
oslings init-repo https://github.com/<your-username>/oslings-<your-username>.git
```

This renames the existing remote to `course` (where exercises come *from*) and
sets `origin` to your repository (where your work goes *to*), then pushes.

You now have two remotes, and that is deliberate:

```text
  oslings-course  ──(oslings update)──▶  your clone  ──(oslings submit)──▶  oslings-<you>
   read-only                                                                 yours
```

## 7. Get the first exercise and submit

```bash
oslings update      # receive whatever has been released
oslings             # open the app; work r00
oslings submit      # commit and push
```

Then check github.com and confirm the commit is really there.

## Deliverables

| | |
|---|---|
| ☐ | A private repo named `oslings-<username>` with the instructor and TA added |
| ☐ | `oslings doctor` green (QEMU lines may be pending — tell the TA) |
| ☐ | `oslings init-repo` run, so `git remote -v` shows both `course` and `origin` |
| ☐ | At least one commit pushed to your repository |

## The habit to build now

**Run `oslings submit` at the end of every single session, whether or not the
exercise passed.**

There is no homework in this course, so that commit is the only record that
you were in the room and working — it is how attendance is taken — and it is
what lets you pick up exactly where you left off. An unfinished exercise that
was submitted earns substantial credit. An unfinished exercise that was never
submitted earns nothing.
