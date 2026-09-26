# Hypothesis Protocol — change direction without losing the old one

A wrong-looking direction is usually an unfinished direction. This protocol
exists so that redirecting the agent costs one command and never destroys work.
`tools/state.py` is the ledger; `test/regression.py` checks that a parked branch
survives.

## Priority scale

| Range | Meaning | Who sets it |
|---|---|---|
| 90–100 | confirmed primitive; work it to the flag | evidence from a probe |
| 60–89 | strong evidence, or a chain card matched with high coverage | evidence or `chain_match` |
| 50 | default for a newly recorded hypothesis | `state.py --hypothesis` |
| 10–49 | plausible but unevidenced, or revived after being parked | operator |
| 0 | parked: still open, still visible, last in line | `--deprioritize` |
| closed | falsified by a specific observation, with the reason recorded | `--close` |

Parked is not closed. Priority 0 keeps `status: open`, keeps the hypothesis in
the ledger, and keeps its probe history. Only an observation that actually
falsifies a hypothesis justifies `--close`, and the reason must name that
observation.

## When the operator says "wrong direction, try something else"

Never delete the branch and never mark it falsified. Run:

```bash
python3 tools/state.py <challenge> --hypothesis-id <id> \
  --deprioritize "operator redirect: no falsifying evidence yet"
python3 tools/state.py <challenge> --hypothesis "<the new direction>" \
  --bug-class <taxonomy-class>
```

Then state in the reply, in one line: what was parked, why, and what the new
highest-priority action is. The parked branch remains eligible; it simply sorts
last.

## When to bring a parked branch back

Revive when new evidence bears on it — not on a hunch, and not because the new
direction is slow.

```bash
python3 tools/state.py <challenge> --hypothesis-id <id> \
  --revive "new evidence: <the observation that changed the picture>"
```

A revived branch returns at priority 40, below a fresh hypothesis, until a probe
raises it. `--priority N` overrides that when the evidence is strong.

Review the ledger before every direction change:

```bash
python3 tools/state.py <challenge> --show
```

## Budget per hypothesis class

Group probes by mechanism, not by payload variant. Twenty header tricks are one
class. The budget for a class is five probes or fifteen minutes, whichever comes
first. On exhaustion with no new signal: park the class at priority 0, record
what was tried, and move to the next mechanism layer. Do not try a sixth variant.

Escalation order when a class is exhausted:

1. Re-read the challenge text and the artifact. A missed field or an unanchored
   pattern is more common than an exotic bug.
2. Change mechanism layer: parser, state machine, auth/session, response side,
   framing, application logic. List the layers still untried before going deeper
   into the current one.
3. Reverse the deciding function. Do not leave the most suspicious code unread
   while brute-forcing around it.
4. Pull outside knowledge for one named missing fact: `tools/chain_match.py`,
   then `tools/search_facts.py` and `tools/writeup_search.py` if challenge name
   and event are known. Record URL/snippet plus the local verification outcome;
   search output is a lead, never a verdict.
5. Time-box out and come back. In a timed contest, one challenge is not worth
   more than its share.

## Never more than three at priority above zero

Three open, non-parked hypotheses at a time. Parked branches do not count
against the limit, which is exactly why parking is safe.

Every hypothesis at priority above zero must carry:

```text
class      the mechanism, not the payload
evidence   the observation that produced it, quoted or referenced
falsifier  the observation that would close it
next probe one reversible action and its expected distinguishing signal
```

A hypothesis without a falsifier is a guess. Write the falsifier before the
probe.

## Chain matches enter the ledger like everything else

`tools/chain_match.py` returns `suggested_priority`. Record it as a hypothesis
with that priority and the card id as evidence. If the confirming probe fails,
park it at 0 with the reason — a chain that does not fit this challenge may
still fit the next one, and the card stays untouched.
