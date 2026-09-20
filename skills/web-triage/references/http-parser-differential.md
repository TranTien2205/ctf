# HTTP parser differential / proxy desync (MCCRAB3 pattern)

When: a custom proxy/WAF/gateway (Rust/Go/nginx-lua/HAProxy) sits in front of the
backend and blocks a path/header/method that the backend itself would serve.

## First moves (decisive tests before variants)

1. Fingerprint both parsers: send minimal requests, compare proxy errors vs
   backend errors (status + body shape + timing).
2. One-echo-backend test: point a copy of the proxy at a raw echo server and
   compare forwarded bytes vs sent bytes. Answers "does it re-serialize or forward
   raw?" in one shot — do NOT brute 20 payload variants first.
3. Build an OFFLINE replica (real proxy binary + real backend) — removes LB noise
   and instance time limits; fuzz there, replay winners live once.

## Budget rule

Header-evasion is ONE hypothesis class. ≤5 probes / 15 min; if no new signal,
jump layers: parser -> connection state machine -> auth gate -> response side.
(See `../../LOOP_DISCIPLINE.md` §3.)

## What closed fast in practice (do not re-walk)

- Duplicate headers / obs-fold / trailer smuggling: both sides parse identically.
- Tab/space before colon, control bytes in names: proxies usually fail-closed.
- CL+TE or TE+TE desync: modern stacks both prefer TE.
- Pipelining limits, Expect: 100-continue, HTTP/1.0 framing: same both sides.
- Header names >127: often skipped by the proxy's rule registry but still
  forwarded — good for FORWARDING probes (proved 500s), useless for names the
  backend must normalize to a specific env key.

## Where the bug actually hides (unreversed = still open)

- The proxy's connection/exchange state machine (hold-then-release semantics,
  message pairing), its auth/pubkey gate, and any config drift between shipped
  template and deployed config. Reverse the DECISIVE function with a decompiler
  (`pdc`/`pdg`/ghidra) before burning more live requests.

## Reproduction notes (TFC CTF MCCRAB3, 2026-09, UNSOLVED)

- Deny = drop-before-backend (proved via game-state oracle), not response filter.
- Matched request held ~30s then connection closed; follow-up benign messages on
  the same connection were still forwarded.
- Lab replica reproduced every live behavior exactly (nohdr 500, matched EMPTY,
  >127-name 500, split-value 500).
