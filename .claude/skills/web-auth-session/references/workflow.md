# Workflow — bounded end-to-end method

Every probe feeds `http_probe.py`/`session_dissect.py`/`jwt_forge.py` and
every verdict goes through `tools/hooks.py`. The loop terminates on
evidence, a falsifier, or the controller's budget — never on a hunch.

---

## Phase 0 — ledger first

```bash
python3 tools/state.py <name> --category web --target "$BASE" \
  --challenge-name "<name>" --event "<event>"
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --source <dir> --record <name>
```

If a chain card is a **strong** match, run its `first_confirming_probe`
verbatim — do not re-derive it.

## Phase 1 — inventory (≤3 requests)

1. `GET /` — capture `Set-Cookie`, `Server`, `X-Powered-By`, the login link.
2. The login POST — capture the response body + `Set-Cookie` verbatim.
3. `session_dissect --token` on whatever the login returned.

Decision after phase 1: is the token **opaque** (session class),
**JWT** (jwt-deep), **signed blob** (itsdangerous/Fernet — deser-adjacent),
or **missing** (Basic/header auth)?

## Phase 2 — mechanism-specific probe

| Mechanism | First discriminating probe |
|---|---|
| JWT | `jwt_forge --claims '{"role":"admin"}' --alg ''` → replay |
| Opaque | two-account diff → fixation test (`session-fixation.md` §1) |
| Signed blob | `session_dissect --try-keys` → re-sign |
| Basic | `admin:admin` etc., then check `/api/me` for claims |
| OAuth | `redirect_uri=https://you.tld` on `/authorize` |
| Reset flow | `Host: attacker.tld` on `/forgot` |
| MFA | `code` absent → `""` → `null` → `"000000"` ladder |

One probe, one verdict, `hooks.py post-probe`, then `decide.py`.

## Phase 3 — escalate along the card

- JWT verify bug works → **forge** `{"role":"admin","sub":"admin"}`.
- Session fixation works → plant the id, trigger the victim.
- Reset-token leak works → read victim's token, POST the reset.
- OAuth `redirect_uri` works → chain to token theft.
- Mass-assign works → read back `/api/me` for the role field.

The win is *crossing an authorization boundary* — a token that verifies
wrong, a session bound to another user, a role you didn't earn. "I got a
token" is never the finding.

## Phase 4 — the flag is elsewhere

The auth break is the *key*, not the flag. The flag lives behind:

- `GET /admin`, `/admin/flag`, `/admin/config`, `/admin/users`
- A field on the admin object: `user{flag}`, `admin{note}`
- An internal endpoint the admin's token unlocks
- A file the admin can read (`/flag`, `/admin/files`)

After boundary-crossing, sweep the admin surface **with the captured
token** — same ledger, new hypothesis.

## Phase 5 — record the chain

```bash
python3 tools/hooks.py pre-flag --value "flag{...}" --source "..." --evidence "..."
python3 tools/classify_solve.py --chain <id>
```

## Bounded-budget notes

- Class budget: 5 probes / 15 min — `decide.py` enforces.
- When a probe falsifies a class (verify-pinned JWT, strict SameSite,
  bound reset token, hashed+rotated session), **record the falsifier**
  and route to the confusable class (`web-idor`, `web-logic-flaw`,
  `web-csrf`, `web-mass-assignment`) instead of retrying.
- Escalation order when budget is spent: `chain_match` → `reclassify` →
  `writeup_search` → `novel_plan` → `fanout_sweep` → `solver_handoff`.
