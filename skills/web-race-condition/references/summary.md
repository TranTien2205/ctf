# Summary — web-race-condition in one file

The skill distilled: the model, the workflow, the proof, and the index into
the depth corpus. Start here; open a named file for the detail.

---

## The model

A race is a **check-then-act gap**: the app reads a predicate (`balance>=x`,
`!used`, `count<max`, `email==`) and acts on it in a *separated* operation.
Two in-flight requests each read the pre-state and both pass the check. The
proof is a **serial-impossible outcome** — a state no serial ordering of the
requests can produce.

## The workflow (one page)

```text
1. classify    → classify.py names the class; chain_match.py hands back the card's probe
2. inventory   → every writable endpoint that has a check (not a blind insert)
3. window      → find the read→write pair + the work between (email/render/fetch)
4. falsifier   → grep for atomic UPDATE / FOR UPDATE / constraint / SERIALIZABLE
5. baseline    → race_probe --baseline-count 5 --count 0 --no-baseline  (the serial set)
6. raced run   → race_probe --concurrency N --count N --write-ack
7. read        → max_in_flight (≥2=overlap) + status split + the STATE
8. attribute   → name the pair that crossed
9. verify      → the effect (2 grants, -balance, 2 votes) → the gate it opens
10. record     → hooks.py post-probe with the verbatim excerpt in --response
```

## The three delivery mechanics

| Mechanic | For | Tooling |
|---|---|---|
| burst | wide window | `race_probe --concurrency N` |
| single-packet | tight window | `race_probe`'s barrier |
| interleave/stall | narrow window, two different requests | `--url-b` or a raw-socket last-byte stall |

## The check-then-act alphabet (quick index)

| Letter | Resource | Module |
|---|---|---|
| A | registration uniqueness | `per-check-balance.md` §4 |
| B | balance/withdraw | `per-check-balance.md` §1 |
| C | coupon/redeem/single-use | `per-check-balance.md` §2 |
| D | vote/like limit | `per-check-balance.md` §3 |
| E | email-change token cross | `per-check-token.md` §1 |
| F | file/object creation | `per-check-balance.md` §6 |
| G | gift/claim-once | `per-check-balance.md` §2 |
| H | inventory/seat | `per-check-balance.md` §6 |
| J | join/member cap | `check-then-act-alphabet.md` |
| L | limit/OTP counter | `per-check-balance.md` §5 |
| O | OTP consume | `per-check-balance.md` §5 |
| Q | queue/job claim | `check-then-act-alphabet.md` |
| S | session issue | `per-check-token.md` §4 |
| T | ticket/seat | `per-check-balance.md` §6 |
| X | cross-request swap | `check-then-act-alphabet.md` |

## The evidence standard

- **confirms** = baseline + real overlap (`max_in_flight` ≥ 2) + a
  serial-impossible state + an attributed pair + the verified effect.
- **falsifier** = real overlap + the defence held + no cross — record it.
- **inconclusive** = `max_in_flight` = 1 — never a result.
- a timeout is never a result; a constraint-500 is a falsifier, not a win.

## The falsifiers

| Defence | It closes |
|---|---|
| atomic `UPDATE ... WHERE` + rowcount | yes — falsifier |
| `FOR UPDATE` / `select_for_update` / `PESSIMISTIC` | yes |
| `UNIQUE`/`CHECK`/PK constraint | yes |
| SERIALIZABLE + retry | yes |
| `version` column | same-row only |
| `findOneAndUpdate`/`ConditionExpression`/`WATCH`/Lua/`IF` | yes |
| advisory/distributed lock scoped read→commit | yes |
| `SKIP LOCKED` / idempotent worker | yes |
| a transaction alone (READ COMMITTED) | **no — still open** |
| a `sleep`/busy-check | **no — narrow only** |

## The verified cards

| Card | Primitive → sink |
|---|---|
| `htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce` | profile race → token-cross → stored XSS → file-write → template RCE |
| `htb-ssos-oauth-registration-race-cookie-swap-json-csrf` | register race → own the bot's account → cookie-swap → flag in your mailbox |

## The blast-radius rules

- `--write-ack` for any write-shaped run.
- Race an object you own — never a shared/demo resource.
- A one-shot target (SSOS) must be confirmed fresh — consumed is
  unrecoverable.

## The index

| Need | Module |
|---|---|
| the window model | `read-modify-write.md`, `theory.md`, `theory-deep.md` |
| delivery | `delivery-mechanics.md` |
| the alphabet | `check-then-act-alphabet.md` |
| per-check playbooks | `per-check-balance.md`, `per-check-token.md` |
| detection | `detection.md`, `detection-deep.md`, `detection-index.md`, `timing-oracle.md` |
| source hunting | `whitebox-hunt.md` |
| per-axis maps | `per-route.md`, `per-boundary.md`, `per-vector.md`, `per-surface.md`, `per-mechanism.md`, `per-framework.md`, `per-falsifier.md` |
| isolation | `database-isolation.md` |
| exploitation | `exploitation.md`, `exploitation-shapes.md`, `multi-step-chains.md` |
| cases | `case-studies.md`, `real-world-cases.md`, `verified-chains.md` |
| evidence | `evidence-rules.md`, `evidence-rules-deep.md` |
| falsifiers/negatives | `falsifiers.md`, `negative-results.md`, `negative-results-deep.md` |
| edge cases | `edge-cases.md`, `edge-cases-deep.md` |
| mistakes | `common-mistakes.md`, `common-mistakes-deep.md` |
| troubleshooting | `troubleshoot.md`, `troubleshoot-deep.md` |
| evasion | `evasion.md` |
| workflow | `workflow.md`, `workflow-deep.md`, `field-manual.md` |
| class boundary | `class-boundary.md` |
| reference | `payload-variants.md`, `extended-corpus.md`, `glossary.md` |
| the base probe | `interleaved-writes.md` |
