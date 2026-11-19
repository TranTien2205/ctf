# Summary — business-logic flaw, in one screen

## The class

The implemented state machine permits an edge the imagined workflow
doesn't: an extra field bound, a step skipped, an action replayed, a
boundary value accepted, a checked value transformed before use.

## The mechanism alphabet (13)

| Mechanism | One-line probe |
|---|---|
| mass assignment | `register` + `role=admin` → read-back |
| workflow skip | call the terminal step bare |
| state replay | the one-time action twice, serially |
| numeric boundary | `-1`, `0`, `NaN`, `1e309`, wraps |
| scaling-after-check | `id` past limit → different-layer rejection |
| unit confusion | the value in the other unit |
| role assignment | privileged field at create |
| idempotency | exact replay, same key |
| time assumption | past expiry / future notBefore |
| sequence | stale ID replay |
| ownership | foreign objectId in an operation |
| singleton | a second privileged object |
| trust-in-earlier-step | mutate an upstream-minted value |

## The falsifiers (fire early)

- `role: user` on read-back → allowlist → mass assignment dead.
- `302/400` to earlier step → state machine real → skip dead.
- `409` on second POST → dedup → replay dead (→ race for parallel).
- `400`/clamp → boundary dead at that field.
- identical rejection for out-of-limit vs malformed → no transform gap.

## The evidence

Baseline pair + manipulated request + verbatim forbidden state
(`role:admin`, `confirmed+unpaid`, `balance:+50-again`, `total:-50`) —
through `post-probe` with `--response` attached. The echo is not the
store; the read-back decides.

## The verified anchor

Pachinko Revisited (`knowledge/chains/pico-pachinko-revisited-...`):
`id` checked raw, address used as `off + id*S mod 2^w` — a checked index
wrapping into instruction memory. The transferable question: **is the
value the checker bounds the same value the sink uses?**

## The routing

- `role` at register confirming → `web-mass-assignment`.
- foreign objectId access → `web-idor`.
- serial replay `409`, parallel window → `web-race-condition`.
- proxy-vs-app value disagreement → `web-parser-differential`.

## The budget

5 probes / 15 min per mechanism; 25 / 45 per challenge. A falsifier
closes a whole mechanism — the cheapest budget-spend there is.
`decide.py` names the next rung when the alphabet is spent.
