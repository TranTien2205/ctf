# Verified chains — the honest record

## Status: catalogue

No challenge in this toolkit has been solved through `web-user-enum`.
This class is **catalogue** — standard published knowledge, not local
experience. Nothing here is a remembered solve.

## The nearest local analogue

`knowledge/chains/htb-phonebook-ldap-prefix-oracle.json` — an LDAP-backed
login whose typed error (a prefix oracle on the bind) distinguishes
accounts/attributes. It is the closest verified shape: an
authentication backend whose response reveals existence. It is filed
under its own class (`web-auth-session`/LDAP injection family), not
this one — but it is the same idea: a typed error that leaks account
state.

## What would promote this class

A real solve where:
1. a differential oracle (text/status/timing/side) on an
   account-touching form confirmed a real account name, verbatim,
2. the confirmed name fed the chain (a spray, a reset, an IDOR, a weak
   password) to the flag, or
3. an absent/bypassed throttle enabled the credential loop that won

...and the response excerpt passed `hooks.py post-probe` with
`--response` carrying the verbatim delta.

## The field-notes discipline

`../../field-notes.md` records every real observation of this class — a
confirmed oracle, a measured throttle, a bypassed limit — marked
`proposed` until reviewed, `confirmed` when checked. A confirmed
chain-solve promotes the class from `catalogue` to `verified` in
`skills/registry.json`.

## The honesty rule

Never present a catalogue shape as "worked here". The corpus is standard
knowledge; `../../field-notes.md` is where local experience accumulates.
