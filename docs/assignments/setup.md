# Setup

**Thursday, August 27 — the first exercise session.** Budget about 45 minutes
for setup, then work `00r_hello_rust`.

By the end of the session you will have your own private repository, a working
toolchain, and your first exercise submitted. Everything after this depends on
it.

If something breaks, that is expected — the instructor and TA are in the room,
and there is a troubleshooting table at the bottom of the
[Dev Setup guide](../guides/dev-setup.md).

## Before class

- **Install `rustup` if you can** (step 2 below). It is a large download, and
  doing it at home saves class time. If it does not work, we will do it in
  class.
- **Have a GitHub account.** Create one at github.com if you do not.
- **Bring a charged laptop** running **macOS**, **Linux**, or **Windows with
  WSL2**. (Native Windows will not work; install WSL2 and use Ubuntu inside
  it.) You need a terminal you are comfortable opening.
- **Read this page and the Prep page for Thursday**, so you know what you are
  about to do before you sit down. <!-- TODO link prep page -->

## 1. Register your laptop on the classroom network

!!! warning "Placeholder"
    CS 326 uses a registration client and server on the classroom router to
    deliver exercise releases to your laptop. The registration tool is not
    ready yet. Instructions will be given in class.

## 2. Install Rust

If you do not already have `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Then restart your terminal, or run `source "$HOME/.cargo/env"`. Check it:

```bash
rustc --version
```

## 3. Create your repository

On github.com, create a **new repository**:

- Name it exactly **`oslings-<your-github-username>`** — for example
  `oslings-jsmith`. The grading tools find your repo by this name.
- Make it **Private**.
- Do **not** add a README, .gitignore, or license. It must start empty.

Then, under **Settings → Collaborators**, add **both** the instructor and the
TA. If we cannot read your repository, we cannot grade it.

## 4. Clone the course repository

```bash
git clone https://github.com/USF-CS326-F26/oslings-course.git oslings
cd oslings
```

This is the shared course repository. It is where exercises arrive from.

## 5. Run the setup script

```bash
./setup.sh
```

This installs the Rust nightly toolchain, the `riscv64gc-unknown-none-elf`
target on both toolchains, the `rust-src` and `llvm-tools` components, offers
to install QEMU, and builds the `oslings` command.

It is safe to re-run at any time.

## 6. Check your environment

```bash
oslings doctor
```

Every line should be green. If any is not, the message tells you the exact
command that fixes it. **Do not move on until this is clean** — or, if only
the QEMU lines are red, see the note below.

!!! note "If QEMU will not install today"
    You are not blocked. Every exercise for the first five weeks runs as plain
    `cargo test` on your own machine — no QEMU, no kernel. Flag it to the TA
    and keep going; we will sort it out during an exercise session.

    The hard deadline for a working QEMU is **Thursday, October 1**, when
    `20a_asm_bridge` (the assembly bridge) needs it.

## 7. Point this clone at your own repository

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

## 8. Get the first exercise and submit

```bash
oslings update      # receive whatever has been released
oslings             # open the app; work 00r_hello_rust
oslings submit      # commit and push
```

Then check github.com and confirm the commit is really there.

## Deliverables

| | |
|---|---|
| ☐ | A private repo named `oslings-<username>` with the instructor and TA added |
| ☐ | `oslings doctor` green (QEMU lines may be pending — tell the TA) |
| ☐ | `oslings init-repo` run, so `git remote -v` shows both `course` and `origin` |
| ☐ | `00r_hello_rust` submitted — the commit is visible on github.com |

## Submit before you leave

**Run `oslings submit` before you leave every session, whether or not the
exercise passed.**

What is committed by the end of the session is what earns credit: a passing
exercise earns 100%, and substantial progress on one earns 50%. An exercise you
finish afterwards and submit by the deadline — Thursday 11:59 pm for a Thursday
exercise, Monday 11:59 pm for a Friday exercise — earns 75%. An exercise that
was never submitted earns nothing.
