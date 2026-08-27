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
- **Have a GitHub account**, and know which one you are signed in as. Your repo
  is created for you against the username you gave on the sign-up form, so
  invitations only work from that account.
- **Bring a charged laptop** running **macOS**, **Linux**, or **Windows with
  WSL2**. (Native Windows will not work; install WSL2 and use Ubuntu inside
  it.) You need a terminal you are comfortable opening.
- **Read this page and the Prep page for Thursday**, so you know what you are
  about to do before you sit down. <!-- TODO link prep page -->

## 1. Sign in to the classroom network

Exercise sessions run on their own Wi-Fi, **cs326**. You sign in once per
laptop; after that it recognises you and there is nothing to do.

1. Join the **cs326** Wi-Fi. The password is given in class.
2. Open **<http://signin.cs326>** in Safari, Chrome or Firefox — your own
   browser, not the small Wi-Fi pop-up window.
3. Press **Sign in with Google**. Google opens in a second tab and asks for the
   code shown on the first one; enter it, press **Continue**, then choose your
   USF account.

About thirty seconds, and no phone or second device is needed.

!!! tip "If Safari says you are not connected but everything else works"
    Turn off iCloud Private Relay for this network: **System Settings → Wi-Fi →
    cs326 → Details… → uncheck "Limit IP address tracking"**.

The network reaches GitHub, the Rust toolchain, the Rust documentation and this
site — and very little else. See
[The Classroom Network](../guides/classroom-network.md) for the full list, what
is recorded about you, and what to do when something does not work.

## 2. Install Rust

If you do not already have `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Then restart your terminal, or run `source "$HOME/.cargo/env"`. Check it:

```bash
rustc --version
```

## 3. Accept your two GitHub invitations

Your repository has already been created for you. You do not make one.

Check the email for your GitHub account, or go straight to both links. **Accept
both** — they are separate, and each does a different job:

| | Accept at | What it is |
|---|---|---|
| 1 | `https://github.com/USF-CS326-F26/oslings-<your-github-username>` | **Your** repo. Your work is pushed here, and it is what we grade. |
| 2 | <https://github.com/USF-CS326-F26/oslings-course/invitations> | The **course** repo, read-only. Exercises are released here and you pull them from it. |

The second one is the one people miss. Without it `oslings update` fails with
`could not read from remote repository`, which looks like a broken SSH key and
is not one.

!!! warning "If either link shows a 404"
    You are signed in to GitHub as a different account than the one you gave on
    the sign-up form. Sign out, sign back in as that account, and open the link
    again. Invitations are bound to one specific account.

The instructor and TA already have access to your repo — there is nothing for
you to share.

## 4. Clone **your** repository

```bash
git clone git@github.com:USF-CS326-F26/oslings-<your-github-username>.git oslings
cd oslings
```

Use your own username, not the literal text. If you have not set up an SSH key,
use the HTTPS form instead:

```bash
git clone https://github.com/USF-CS326-F26/oslings-<your-github-username>.git oslings
```

Do **not** clone `oslings-course`. That is the read-only course repo; your
clone attaches to it automatically in step 5, and `oslings` refuses to work in a
clone of it.

## 5. Run the setup script

```bash
./setup.sh
```

This installs the Rust nightly toolchain, the `riscv64gc-unknown-none-elf`
target on both toolchains, the `rust-src` and `llvm-tools` components, offers
to install QEMU, and builds the `oslings` command.

It then attaches your clone to the course repo and pulls whatever has been
released so far, so you finish this step with today's exercise already in place.
If that last part fails, it is almost always invitation 2 from step 3 — accept
it, then run `oslings update`.

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

## 7. Confirm the two remotes

`setup.sh` did this for you; this step is a check, not work. Run:

```bash
git remote -v
```

You should see both, with `origin` pointing at **your** repo:

```text
course  git@github.com:USF-CS326-F26/oslings-course.git   (fetch)
origin  git@github.com:USF-CS326-F26/oslings-<you>.git    (fetch)
origin  git@github.com:USF-CS326-F26/oslings-<you>.git    (push)
```

If `course` is missing, add it (it takes no argument — the URL travels in the
course files):

```bash
oslings init-repo
```

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

`oslings update` is not optional on a fresh clone. Before it runs, your repo
contains **no exercises at all**, and `oslings` will tell you so:

```text
error: no exercises have been released yet.

Receive the ones your instructor has released:
  oslings update
```

You write your answers in **`warmup/src/lib.rs`**. It is not in the repo you
cloned: `oslings` creates it when you open the app, by copying the exercise's
starter code into place. So if `warmup/src` looks empty, open `oslings` — that
is the step that puts the file there. Do not edit anything under `exercises/`
— that is read-only course material, the skeleton in it is only the template
that gets copied to `warmup/src/lib.rs`, and editing it changes nothing except
breaking your next `oslings update`.

Then check github.com and confirm the commit is really there.

## Deliverables

| | |
|---|---|
| ☐ | Both GitHub invitations accepted — your repo **and** `oslings-course` |
| ☐ | `oslings doctor` green (QEMU lines may be pending — tell the TA) |
| ☐ | `git remote -v` shows both `course` and `origin` |
| ☐ | `00r_hello_rust` submitted — the commit is visible on github.com |

## Submit before you leave

**Run `oslings submit` before you leave every session, whether or not the
exercise passed.**

What is committed by the end of the session is what earns credit: a passing
exercise earns 100%, and substantial progress on one earns 50%. An exercise you
finish at a make-up session — office hours with the instructor or TA, on the
**cs326** network, before the next session — earns 75%. An exercise that
was never submitted earns nothing.
