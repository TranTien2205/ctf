# LOOP_DISCIPLINE — how to not get stuck

Shared by every router. The priority scale, parking and revival commands live in
`../HYPOTHESIS_PROTOCOL.md`; this file is the reasoning discipline behind them.

## 1. The unit of work is a mechanism class, not a probe

Group probes by mechanism, never by payload variant. "Bypass the rule with a
header trick" is one class whether you try three variants or twenty: duplicate
headers, tabs, high bytes, split values are all the same idea. When the class
budget is spent, change layer — do not try the next variant.

Default budget per class: **five probes or fifteen minutes**. Reaching either
without a new signal ends the class.

## 2. Decisive test first

Before trying N variants, ask: is there one test that kills or confirms the whole
class?

- Does the proxy forward the original bytes? One echo-backend test answers it;
  twenty payloads do not.
- Is the comparison equality or containment? Read the deciding function; do not
  brute-force around it.

Variants are for when a decisive test is genuinely impossible.

## 3. Escalation ladder

Climb in order. Do not return to a closed layer without new evidence.

1. **Re-read the challenge text and the artifact.** A missed hint, field or route
   is the most common cause. Is the pattern anchored? Is the check equality or
   containment?
2. **Change mechanism layer.** Parser, state machine, auth and session, response
   side, framing, application logic. List the layers still untried before going
   deeper into the current one.
3. **Reverse the deciding function.** For binary work, decompile the function
   that actually decides. Never leave the most suspicious code unread while
   brute-forcing around it.
4. **Pull outside knowledge.** `../tools/chain_match.py` first, then
   `../tools/writeup_search.py` once the name and event are known. Whether a
   writeup is allowed depends on the contest rules; record that you used one.
5. **Park it and come back.** In a timed contest, one challenge is not worth more
   than its share.

## 4. Recognising flailing

Stop immediately on any of these: repeated self-correction inside one turn; more
than two new hypotheses in a turn with none tested; restating an idea that was
already falsified; payload complexity rising while information gained does not.

Replace it with a written ledger entry through `../tools/state.py`
(`--hypothesis`, `--probe`, `--result`, `--deprioritize`, `--close`). The ledger
leads the decision; it is not a log written afterwards.

## 5. Evidence, not belief

- "Reversing is done" is true only when the deciding function has been read, not
  most of it.
- Suspect a misread offset or opcode? Verify with a decompiler or a local
  replica. Do not reason from a guess.
- A flag is a hypothesis until it is read from the target or the artifact.
- A timeout says something about availability, nothing about a bug.

## 6. Build an offline replica when one is possible

If the challenge ships a binary or a service and you control the input, rebuild
it locally. Fuzz there without a clock and without instance noise, then fire only
confirmed payloads at the live target. This also protects shared instances from
destructive experiments.
