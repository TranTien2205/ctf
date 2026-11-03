---
name: report-writing
description: Write the engagement report so that every claim is traceable and every absence is bounded — three sections that never merge, impact without inflation, and coverage stated as a limit. Use when an engagement is ending, when a finding is being written up, or when asked what was found.
---

# Writing the report

`argus report <engagement> --write` renders the structure. This skill is about
the sentences that go in it.

## Three sections, and they never merge

1. **Confirmed.** The proof requirement was met. Print the checks, the evidence
   ids, and a reproduction that a client can run.
2. **Candidates.** A real signal with a named missing check. This section is the
   most useful one in the document, because it tells the next session exactly
   where to start.
3. **Not demonstrated.** Parked and falsified hypotheses, with the observation
   that closed each one.

Merging two and three is how a report turns a guess into a vulnerability.
Dropping three is how a reader concludes that everything not mentioned was
tested and clean.

## Impact: what the evidence supports, and not one clause more

| written | should be |
|---|---|
| "full database compromise" | "read access to the `users` table; write access not tested" |
| "complete server takeover" | "command execution as `www-data`; privilege escalation not tested" |
| "all user accounts affected" | "one other user's record was read; the pattern suggests all, which was not tested" |
| "could lead to RCE" | a candidate, or an `rce` hypothesis with its own proof |

The pattern is the same each time: name what you observed, then name what you did
not test. The second half is what makes the first half credible.

## Severity is a judgement, so show the inputs

State the three things that produced it: what an attacker gains, what they need
first (unauthenticated, any user, admin), and what the data or function is worth.
A critical that needs admin is not a critical, and a medium on a tenancy boundary
can be the worst finding in the report.

Where a second model's reading disagreed with the first, the report carries the
disagreement. `argus verify` records it, and a demoted finding is a better
outcome than a confident one that fails review.

## Absences, with their boundary

Never write an unbounded absence. "No SQL injection" is a claim about every
parameter, every encoding and every code path.

Write instead: *"The `id`, `q` and `page` parameters on `/item`, `/search` and
`/list` were tested for SQL injection with quote differentials, boolean pairs and
sqlmap at level 1 risk 1; none showed a signal. Parameters reachable only after
admin authentication were not tested, because no admin credential was supplied."*

That sentence is longer, it is true, and it is the one that survives the client
finding an injection next month.

## Reproduction a client can run

One command or one request per step, with the nonce or the identifier that makes
it verifiable. No tool-specific invocation the client does not have installed, if
`curl` will do. For code execution, the reproduction is the benign marker command
— never the exploit that would do damage.

## What not to include

- raw credentials or keys: refer to them by kind and position, redacted. The
  ledger already redacts on write.
- a full database dump: the five rows that prove the read are the evidence; the
  rest is a liability for both sides.
- a stored payload you left behind: remove it, and record the removal.
- a scanner's output pasted wholesale. If it did not become a hypothesis, it goes
  in coverage as "scanned, not triaged", with the count.
