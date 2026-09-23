---
name: web-request-smuggling
description: >
  Action-oriented depth skill for Request smuggling / CRLF injection. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-ssrf, web-parser-differential.
  Verified here by 1 chain card(s).
tags: [web, request-smuggling, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: verified
---
# Request smuggling / CRLF injection

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

one folded control character inside the interpolated value; compare the upstream error with an ordinary hostname

**Falsifier** — the observation that closes this class: the value is percent-encoded or validated, so no control character survives into the outbound request

**Blast radius** — read before any write on a shared instance: a smuggled request executes against the backend as a trusted client; it can change state for everyone
## Recognise

Two parsers disagree about where one request ends and the next begins. In CTF web
that most often appears as **CRLF injection into a server-side fetch**: a request
value is interpolated into a URL or a header without encoding, and the control
characters survive into the outbound request.

## Confirm

One folded control character inside the interpolated value. Compare the upstream
error against an ordinary hostname. If the parser accepts the folded form, the
value is not encoded and a second request can be appended.

## Operational probe

Compare two requests and preserve the raw status lines:

```text
baseline: ordinary hostname -> one ordinary upstream response
variant:  one observed folded control character -> parser error or a second
          attributable status line
```

Use only routes observed in source or responses. A class confirmation requires
the control character to survive into the outbound request, shown by a parser
differential or a second response. A 302, generic 400, timeout, or reset is not
confirmation.

After confirmation, calculate body length in bytes and add a trailing fragment.
Send the first state-changing request only against an object created by the
solver, with cleanup recorded before execution.

## Building the smuggled request

Once a control character survives, the outbound stream is yours to shape:

1. Terminate the original request line and its headers.
2. Append a complete second request, with a content length that counts the body
   bytes **exactly**.
3. Append a trailing fragment so the smuggled request is terminated and the
   connection does not hang waiting for more.

The backend is now issuing the request, which is what defeats a loopback-only
route: the caller's address is the backend's own.

## Traps

- An off-by-one content length silently drops the body or hangs the connection.
  Count the bytes, do not estimate them.
- Without the trailing fragment the smuggled request is never completed.
- A smuggled request executes as a trusted client. On a shared instance it
  changes state for everyone — know what it will do before sending it.
- Do not use a sixth CRLF spelling after the class budget is exhausted. Change
  the parser boundary or move to another mechanism layer.

## Routing

Shares signals with: `../web-ssrf/`, `../web-parser-differential/`. Check those before committing to this one.

Depth, one named file at a time:

- `../ctf-web/client-side.md`
- `../web-triage/references/http-parser-differential.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
