# Username sources — where candidate accounts come from

## Owned/seeded accounts — the cleanest source

- **your own account** — register one; it is a guaranteed known-good
- **a seeded/default account** — `admin`, `administrator`, `root`,
  `test`, `demo`, `user`, `guest`, `ctf`, the challenge name
- **an account the challenge hands you** — a supplied credential, a
  fixture user named in the description/source

Use your own account as `known-good` first — it cannot be locked out of
a victim's account and it is certainly real.

## App-leaked names — the second source

- **the front-end bundle** — `web-source-map` recovered `username`,
  `author`, `created_by`, a `{"user":"alice"}` fixture, a default
  `currentUser`, a hardcoded admin name
- **public content** — a blog `author=`, a forum username, a commenter's
  name, a `/users/` public list, a member directory
- **source/handout** — a `users` table seed, a `fixtures.json`, a
  `INSERT INTO users` line, a config `admin_user=`, a git author
- **emails** — `alice@target.corp` → the `alice`/`alice@target.corp`
  candidate; a contact/team page names staff
- **the error itself** — some apps leak a valid name in a debug error
- **an IDOR'd object** — a user object read through `web-idor` names
  real accounts

## Wordlists — bounded, not sprayed

On an authorized target, a small candidate list confirms the oracle
works — not a mass spray:

- `SecLists/Usernames/top-usernames-shortlist.txt`
- `xato-net-10-million-usernames` (a slice)
- the `cirt.net`/`Names`/`sao`/`burn` lists (a slice)
- a names list — `admin admin2 administrator root test demo user guest
  ctf flag service backup sysadm deploy jenkins gitlab ci bot`

**Never spray a real-wordlist at a shared or victim target** — that is
the brute-force run the throttle exists to stop, and the measurement
(no-signal vs 429) needs only a handful of candidates.

## The candidate-set rule

The oracle is proven with `known-good` + `known-bad`, not with a list.
The list is what a CONFIRMED oracle enumerates — and only on an
authorized, owned, or explicitly-scoped target, bounded by the throttle
measurement.
