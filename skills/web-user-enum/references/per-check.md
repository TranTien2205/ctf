# Per-check — each verification check's pass criteria

| Check | Pass (oracle confirmed) | Fail (channel closed) |
|---|---|---|
| noise baseline | `bad1` != `bad2` only in per-request fields | `bad1` == `bad2` fully (noise-free — fine) |
| body diff | a masked byte/word/code difference, repeats | masked `good`==`bad` |
| status | `good` code != `bad` code, repeats | identical codes |
| redirect | `Location` differs (`?e=1`/`?e=2`), repeats | identical `Location` |
| timing | median delta >3x jitter, N>=8, re-run | sub-jitter delta, N>=8 |
| envelope | a cookie/header/JSON-field difference | identical envelope |
| send side | the email/OTP fires only for real | both arms queue/send |
| direct exists | `{"available":false}` / `200` vs `404` | `{"available":true}`/uniform |
| register-taken | `"taken"`/`409` on known, free on bad | both free or both rejected |
| lockout | `423` only on real name | both lock or neither |
| throttle | absent / threshold / bypassed | measured and bounded |

## The check-order rule

Baseline first (noise), then the cheap checks (body/status/envelope),
then the paid checks (timing/lockout/throttle). A check that passes is
a confirmed oracle on that channel; a check that fails is a measured
closure.

## The check-to-evidence map

Each passing check carries its verbatim excerpt — the two response
bodies, the two `Location`s, the median+jitter numbers, the `Set-Cookie`
diff, the `{"available"}` JSON, the `423` line, the burst codes. The
excerpt is the evidence; the check is the protocol.
