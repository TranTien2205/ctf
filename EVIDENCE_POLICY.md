# Evidence policy

Every claim carries two separate things: what is claimed, and what supports it.
A claim with no supporting record is not a finding, and the ledger refuses it.

## What counts

- **Probe evidence** — the exact request or argv, the timestamp, the status, the
  headers, the final URL, and a bounded span of the body or output.
- **Source evidence** — the exact file, line, route, input and sink.
- **Control evidence** — the request that establishes what the answer should have
  been: a value that certainly exists, a path that cannot, an identity that is
  not entitled, a token that is deliberately invalid.
- **Out-of-band evidence** — a callback at a collector we control, carrying a
  token only this probe could have minted.
- **Browser evidence** — a real browser reporting that a payload executed.

## What does not count

A scanner's label. A template id. A tool's confidence score. A version banner. A
timeout. A 500. A reflected payload. A writeup's claim. A chain-card match. Your
own reasoning about what probably happened.

A timeout is evidence about availability or processing time, and nothing else.

## The per-class requirement

`argus proof` prints the whole matrix; `argus proof <class>` prints one. The
shape of each requirement, and the mistake it exists to prevent:

| Class | Requirement | Prevents |
|---|---|---|
| `rce`, `deserialization`, `file-upload-rce` | a declared marker command, its nonce in the **output**, and an identity line; nothing destructive in the request | a timing difference reported as code execution; a *reflected* nonce reported as execution; a report that needs the host rebuilt to verify |
| `sqli` | DBMS fingerprint + a named table + at least one row, bounded | a 500 on a quote reported as injection; a proof that becomes a breach |
| `lfi`, `xxe` | a sentinel from a file whose shape is known, plus the control for a path that cannot exist | "the response got longer" reported as a file read |
| `ssti` | a result of four digits or more, computed and not echoed | `{{7*7}}` returning 49 by coincidence |
| `ssrf`, `log4shell` | a collector callback with the probe token, or a response only the internal network could give | a connection error reported as a blocked SSRF |
| `idor` | two identities, a cross-read naming actor and subject, the entitlement control, and outcomes that actually differ | a 200 on `id=2` reported as broken access control; a control that answers exactly as the probe did |
| `auth-bypass` | a forged token accepted, an invalid one rejected, privileged content returned | an endpoint that never needed a token reported as a bypass |
| `xss` | a browser that executed the payload and reported the nonce | reflection reported as execution |
| `csrf`, business logic | read, act, read again — and the actor must be one that should not have been able to | a state change nobody checked persisted |
| `race-condition` | two orderings of the same requests, the serial control, and a difference in outcome — which may be one of degree: the same statuses and more successes in parallel | a flaky endpoint reported as a race |
| `cache-poisoning` | a value only the poisoning request sent, returned to a requester that did not send it, with the clean control | an unkeyed header reported as a poisoned cache with no second requester |
| `open-redirect` | a 3xx `Location` pointing off origin, with the in-origin control | a status difference with an in-origin Location; and the reverse — a real redirector refused because both destinations answer the same 302 |
| `secret-exposure` | the credential observed in a response **and** shown live against its own issuer, stored redacted | a rotated key in an old bundle reported as a live credential |
| `dos` | — | refused: the proof would be the damage |

Three mechanisms sit behind that table, and each exists because a check that
reads plausibly can still grade wrongly:

- a **required** check must pass for `proven`, and one passing is what makes a
  grade `supported`;
- a **veto** check disqualifies: "the proof command stayed benign" passes
  trivially when no command ran, so as a *required* check it made any record at
  all under an `rce` hypothesis recordable as a critical candidate. As a veto it
  does the job it was written for;
- a **floor** check is the one that makes the evidence about this class at all.
  Without it a record set containing only the control graded `supported` —
  "every redirect destination stayed in origin" came back as partial progress
  toward an open redirect.

## Grades, and what each one licenses

- **`proven`** — every required check passes. It may be reported as a finding.
- **`supported`** — a real class-specific signal, with at least one required
  check missing. Recorded as a **candidate**, with the missing check named. It
  may not be reported as a vulnerability, and it is the most useful line in the
  report for whoever works next.
- **`unproven`** — nothing in the evidence meets the requirement. Not recorded.
- **`refused`** — the class may not be proven here at all.

## Bounded collection

A proof is the smallest observation that establishes the claim. Five rows, not
the table. One file, not the filesystem. One benign command, not a shell. The
tools enforce this where they can — sqlmap extraction is capped, evidence
records store at most five rows, a `rm -rf`-shaped payload cannot be graded — and
where they cannot, the hygiene checks in the matrix say so in the report.

Secrets are redacted on the write path, before anything reaches disk: the ledger
holds the kind and the position, never the value.

## Absences

Never state an unbounded absence. "No SQL injection" is a claim about every
parameter, every encoding and every code path.

State the absence with its boundary instead: which inputs were tested, with what,
and what was not reached. That sentence is longer, it is true, and it is the one
that survives the client finding an injection next month.

The report's coverage section is generated from the ledger for this reason: it
lists the classes with no hypothesis on any target and says, in as many words,
that their absence from the report is an absence of testing rather than an
absence of risk.

## Direction changes

A hypothesis is closed only by an observation that falsifies it, and the record
names that observation. An operator redirect, a tight schedule or a better idea
are reasons to **park** at priority 0, not to close. A parked branch is revivable
the moment new evidence bears on it, and the report lists what would revive it.

## Cross-verification

A confirmed finding is re-read by a model from a different family, shown the
evidence and the requirement but not the first model's reasoning. Disagreement
demotes the finding to a candidate and the report carries the disagreement. That
is the correct outcome, not a failure of the process.
