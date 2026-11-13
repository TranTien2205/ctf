# Auth enumeration & weak-credential surface

**When:** login, registration, password-reset, or SSO endpoints reveal
whether an account exists — or accept credentials you should not have.

## User enumeration

Submit the form twice: a guaranteed-bogus identifier, then likely-real
usernames. Any response delta — "unknown user" vs "wrong password",
different status/length/timing, a captcha that only appears for real
accounts — lets an attacker harvest a valid-user list.

`probe_enum(url, data, param)` automates the differential and then repeats
it, because the class requires each answer to be observed more than once -
one difference is a coincidence, a repeated one is a channel. It says so
when an answer does not reproduce; treat that as noise, not an oracle.

Still confirm a hit is a real account (password-reset response, profile
fetch) before recording. Cite the first and the repeat of BOTH answers: the
requirement is a repeated difference, not a single one.

Other enumeration channels worth one request each:

- Registration: "email already registered" vs clean form re-render
- Password reset: "reset link sent" vs "no account for that address" -
  a uniform message is the defense
- Timing: real users get a bcrypt verify (~100-300ms), unknown users
  return early - `probe_enum` measures this channel automatically
  (~2.5x+ slower = timing lead when error text is uniform)

## Weak credentials

- Default/vendor pairs only on systems that ship them (routers, CI,
  admin consoles): admin/admin, admin/password, root/root - document
  the exact default, never brute-force
- Password policy: a form accepting `a`/`123` proves no policy; record
  it as a weakness note, not a finding by itself
- Rate limiting: N failed logins without lockout/throttle is the
  finding - do not exceed a handful of attempts on a real target

## What does NOT count

- A generic "login failed" for everything (the defense working)
- Enumeration that only matters because MFA is absent - report the
  missing MFA as the finding, the enumeration as context

## Severity guide

Bulk-harvestable enumeration on a real user table: low-medium, higher
when combined with no lockout. Single-account confirmation: info-low.
