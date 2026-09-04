# The Classroom Network

Exercise sessions run on their own Wi-Fi network, **cs326**, which reaches
GitHub, the Rust toolchain and the Rust documentation, and very little else.
This page is the reference for it: how to sign in the first time, what the
network can and cannot reach, what the class server records about you, and what
to do when something does not work. You sign in **once per laptop** — after
that you join and the network recognises you, with nothing to run and nothing to
type.

Why the network exists at all is a separate question, answered on
[Academic Integrity and AI](integrity-policy.md).

## Signing in, once per laptop

```
Join cs326  →  open http://signin.cs326  →  Sign in with Google
            →  enter the code, Continue   →  choose your USF account
```

1. **Join the `cs326` Wi-Fi.** The password is given in class.
2. **Open `http://signin.cs326`** in Safari, Chrome or Firefox. (Your own
   browser, not the small Wi-Fi pop-up window — see below for why.) The bare
   address `http://signin` works too.
3. **Press "Sign in with Google".** Google opens in a second tab. The first tab
   stays where it is, with your code still on screen.
4. **Google asks for the code first, and only then for an account.** Type the
   code from the first tab, press **Continue**, and pick your USF account on the
   next screen. If you are signed out you will go through the usual USF login
   and Duo.

That is the whole thing, about thirty seconds. **You do not need a phone or a
second device**, and there is nothing to install.

From then on, opening your laptop in the room is enough. The network knows this
machine and lets it through. You only see the sign-in page again if you bring a
different laptop, or if you tell macOS to forget the network.

## What the network reaches

| | |
|---|---|
| **GitHub** | `github.com` and `api.github.com`, so `oslings update` and `oslings submit` work, and so you can use the web UI |
| **Rust packages** | crates.io and `static.rust-lang.org`, so `cargo` and `rustup` work |
| **Rust documentation** | the official docs, docs.rs, Comprehensive Rust, Rustlings and the playground — the full list, with links, is on [Rust References](rust-references.md) |
| **This site** | every page, including the lecture slides |
| **Signing in** | Google's sign-in pages and USF's own login |

Both of those points — why the playground is reachable, and why `rustup doc` is
still faster — are covered where the sites themselves are listed, on
[Rust References](rust-references.md).

## What it does not reach

Everything else, including every AI assistant. **GitHub Copilot is blocked by
name** — `api.githubcopilot.com` and its companions — as are the chat and API
endpoints of the other assistants. That is not a hint; it is the same rule the
[integrity policy](integrity-policy.md) states, enforced where it can be.

A blocked name fails immediately with "server not found" rather than hanging.
That is the network telling you no, not a broken connection.

**The restriction is not airtight**, and this page will not pretend otherwise.
A phone hotspot defeats it completely. The rule is written as conduct for
exactly that reason: reaching the open Internet during a session is an integrity
violation whether or not anything stopped you.

## What the class server records

Disclosed here rather than collected quietly, in the same spirit as
[what OSlings records](integrity-policy.md#what-oslings-records).

When you register a laptop, the classroom router stores:

| Field | Where it comes from |
|---|---|
| Your name | Google, when you sign in |
| Your USF email | Google, when you sign in |
| Your GitHub username | the roster you filled in at the start of term |
| That laptop's network address | the laptop itself |

While you are connected during a session it also records **that the laptop was
connected, and for how long**.

That is the whole list. No browsing history and no page contents are kept: the
connections are encrypted, and nothing about what you visit is stored.

**It is not scored, not ranked, and not part of your grade.** There is no
attendance component in this course — the grading table in the
[syllabus](../syllabus.md) is the whole grade. It exists so that the exercise
can be released to the room, and so that if a question arises later about a
session there is a record of who was on the network.

You may ask to see your own record, and to have it deleted, at any time.
Registrations and connection logs are erased at the end of the semester.

## When it does not work

### Safari says you are not connected, but everything else works

You have **iCloud Private Relay** switched on. Safari sends its traffic through
an Apple relay that the classroom network cannot reach, so Safari alone fails
while the rest of your Mac is fine.

Turn it off for this network: **System Settings → Wi-Fi → cs326 → Details… →
uncheck "Limit IP address tracking"**.

### The sign-in page offers no account to choose from

You are in the small Wi-Fi pop-up window rather than a browser. That window has
no Google session of its own, so it cannot show you your accounts, and it cannot
open the second tab the sign-in needs.

Open **Safari or Chrome** and go to `http://signin.cs326` — the same page, in a
browser where you are already signed in.

### "We do not have a GitHub username on file for you"

Your GitHub username is not on the class roster, so the sign-in has nothing to
tie your laptop to. Tell the instructor or TA; they can register the laptop by
hand in a moment, and it is worth fixing the roster afterwards.

### `oslings update` or `cargo` cannot reach the network

Check you are on **cs326** and not another network, and that you have signed in.
An unregistered laptop reaches the sign-in page and nothing else. If you are
signed in and something still fails, say so in the room — the block list is
deliberate but not infallible, and a missing host is a one-line fix.

## The staff network

There is a second network, **cs326-staff**, for the instructor and TA. It is not
restricted, and it is not for student laptops.
