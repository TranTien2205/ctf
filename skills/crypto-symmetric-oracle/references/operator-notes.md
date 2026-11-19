# Operator notes — field-tested habits

## Before the first request

- Read the whole handout once for the word 'flag': where does it live (a
  cookie, a decrypt endpoint, a file)? The attack targets THAT location.
- List every endpoint that takes attacker bytes. Each is a candidate oracle.

## During the loop

- Log every request count. A padding-oracle loop at 12,000 requests with no
  progress is stuck at a boundary, not 'almost there'.
- Save every recovered byte — a loop restart from scratch wastes the budget.
- When a guess produces two 'valid' answers, it's the pad-boundary ambiguity:
  disambiguate immediately, don't pick one.

## Rate and politeness

- Shared CTF infra: a 40k-request loop at full speed can kill the instance
  for everyone. Throttle to the accepted rate.
- A service that starts returning 429/connection-reset has been rate-limited;
  the loop must back off, not retry harder.

## Verification habit

- Every recovered byte region gets re-verified: submit the recovered value
  where it should produce a known answer.
- Flag candidates get submitted through pre-flag — never recorded from the
  tool's stdout alone.

## Restart discipline

- A mid-loop failure (connection drop) resumes from the saved byte position,
  not from byte 0.
- A mechanism-level failure (falsifier fires) does NOT resume — the mechanism
  was wrong; re-identify.
