---
name: web-ssrf
description: >
  Server-side request forgery. Use when the server fetches a URL the request
  controls, or when a bot or renderer visits an address you supply. Verified here
  by 2 chain cards.
tags: [web, ssrf, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---

# Server-side request forgery

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-red-island-ssrf-gopher-redis-lua-rce.json`
- `knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json`

Run `python3 tools/chain_match.py` before this skill: a matching chain
gives you the exact confirming probe that already worked.

## First probe

One address you control, then the same request against an internal-only address,
comparing status **and timing**. The pair matters: a single request tells you the
value was accepted, not that it was fetched.

**Falsifier** — the observation that closes this class: the fetch target is fixed
in source and the request never influences it.

## Find the read channel first

The difference between a slow SSRF and a fast one is whether you can see the
response. In order of value:

| Channel | How to spot it |
|---|---|
| Body echo | fetched content appears in the response |
| Error echo | content appears inside an error message even on a non-200 — read error bodies, always |
| Status oracle | open and closed ports differ by status or by timing |
| Out-of-band only | nothing comes back; you are limited to what the fetch itself achieves |

`../../solved/red-island.md` records the error-echo case: the app returned the fetched
file inside the `message` field of a 401. Had the error body gone unread, the
whole chain would have looked blind.

## What the fetch can reach

Start from what the source says exists, not from a list of guesses. Loopback
services, the container's own other ports, a metadata endpoint if the challenge is
cloud-shaped, and the application itself — which is how a loopback-only route
becomes reachable.

The schemes the client supports decide the rest. An HTTP client that accepts a
line-protocol scheme can speak to anything that reads lines: a cache, a queue, a
database. Build the payload byte-exactly — a length prefix that is off by one
produces silence, not an error.

## When the value is not encoded

If control characters survive into the outbound request, this stops being SSRF and
becomes `../web-request-smuggling/`. Test that early: it is a much stronger
primitive, and the tell is the same interpolation you already found.

## Traps

- Read error bodies. The leak is there more often than in a 200.
- A redirect can move the fetch to a scheme or host the validator would have
  rejected; follow what the server followed, not what you sent.
- A blocked address list is usually bypassable by representation; a resolver that
  checks after resolution is not. Read which one the source does.
- On a shared instance, a fetch that writes — a queue push, a cache fill, an eval
  — changes state for everyone. Prefer a read first.

## Routing

Shares signals with: `../file-read-primitives/`, `../web-request-smuggling/`.
Check those before committing to this one.

Depth, one named file at a time:

- `references/protocol-smuggling.md`
- `references/cloud-metadata.md`
- `../ctf-web/server-side-advanced.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Operational probe

Two requests, compared: one address you control, then the same request against an
internal-only address. Status *and* timing carry the signal.

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-ssrf \
  --url "$BASE/fetch" --method POST --body 'url=http://127.0.0.1:1/' \
  --evidence-regex 'ECONNREFUSED|Connection refused|:1\b' \
  --evidence-kind class --on-match confirms --on-miss inconclusive
```

A refused loopback port is a better first probe than a callback host: it needs no
egress, and the error text names the address the server actually dialled.

**Falsifier:** the fetch target is fixed in source and the request never
influences it. Reaching your own host proves egress, not SSRF — the class signal
is that *the server* chose an address you supplied.

Pipe the result straight into the write gate: `http_probe.py` already emits the
shape `tools/hooks.py post-probe` wants, so the excerpt is verbatim and a
transport failure is recorded as `transport`, which can never confirm.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. Entries marked `proposed` are awaiting review; entries marked `confirmed`
have been checked. See `../../LEARNING_LOOP.md`.
