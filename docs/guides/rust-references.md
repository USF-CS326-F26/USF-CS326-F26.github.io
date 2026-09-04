# Rust References

These are the reference sites the **cs326** network reaches during an exercise
session. The list is not a recommendation of where to look first — it is the
whole set. Anything not on it fails immediately with "server not found", which
is the network saying no rather than a broken connection. See
[The Classroom Network](classroom-network.md) for how the network works and
[Academic Integrity and AI](integrity-policy.md) for why it is shaped this way.

Everything here is readable during a session, including during a quiz or an
exam, unless the instructions for that particular exercise say otherwise.

## The official documentation

### [doc.rust-lang.org](https://doc.rust-lang.org/std/)

The whole of the official Rust documentation set, and the one to reach for
mid-exercise when you need the exact signature or the exact guarantee.

- [The Standard Library](https://doc.rust-lang.org/std/) — API docs for every
  type in `std`, with examples on nearly every page
- [The Book](https://doc.rust-lang.org/book/) — the tutorial the course follows
  for ownership, borrowing and lifetimes
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/) — the same
  ground as the Book, taught through runnable programs
- [The Reference](https://doc.rust-lang.org/reference/) — the precise
  language definition, for when the Book is not specific enough

`rustup doc` opens the same standard library offline, and is faster than the
network. It is no longer the only way to read it.

### [docs.rs](https://docs.rs/)

Generated API documentation for every crate published to crates.io, at the exact
version you depend on. This is where you read a dependency rather than guessing
from its source.

### [crates.io](https://crates.io/)

The package registry itself: what a crate is, who publishes it, which versions
exist, and a link to its docs.rs page. Mostly `cargo` talks to it for you, but
the web pages are here when you want to look a crate up by hand.

## Learning and practice

### [Comprehensive Rust](https://google.github.io/comprehensive-rust/)

Google's four-day Rust course, including the bare-metal and concurrency days
that line up with the second half of CS 326. Its **Run** buttons work, because
they compile on the playground below.

### [Rustlings](https://rustlings.rust-lang.org/)

Small failing programs you fix one at a time until they compile. The closest
thing to OSlings in the wider Rust world, and useful practice for the same
muscles.

### [rust-exercises.com](https://rust-exercises.com/)

Exercise sets on ownership, traits and error handling, worked in the browser.
Good for the week before a midterm when you want problems rather than prose.

### [The Rust Playground](https://play.rust-lang.org/)

Compile and run a snippet in a browser tab, with no project and no `cargo`.
This is what the **Run** buttons throughout the Book and Comprehensive Rust use.

Your exercise code belongs in your own repository and your own compiler, where
the test harness can see it — but nobody will object to you trying a five-line
example here.

## Around the edges

### [rust-lang.org](https://www.rust-lang.org/)

The project's front page: release announcements, the install instructions, and
the links out to everything above. Rarely what you want mid-exercise, and
reachable so that the links from the other sites do not dead-end.

The two Rust discussion forums, `users.rust-lang.org` and
`internals.rust-lang.org`, are **not** reachable, even though they sit under the
same name. Links to them from the pages above will fail.

### [asciinema.org](https://asciinema.org/)

Recorded terminal sessions, played back as text rather than video. Reachable
because the Rustlings landing page embeds one; you are unlikely to need it
directly.

## What is not here

Every AI assistant, by name and by address. Search engines. The forums above.
Anything else at all.

This is deliberate and it is the same rule as the
[integrity policy](integrity-policy.md), enforced where it can be. The
restriction is also not airtight — a phone hotspot defeats it completely — which
is exactly why the rule is written as conduct: reaching the open Internet during
a session is a violation whether or not anything stopped you.

One cosmetic side effect worth knowing, so you do not report it as a fault: a
few pages here load images or analytics from hosts the network blocks. The
Comprehensive Rust landing page shows three broken badge icons for this reason.
The pages themselves are complete.
