# Evidence rules — what proves a business-logic flaw and what never does

A business-logic confirmation is a **state change the workflow forbids**,
read back verbatim from a live response. Everything short of that is a
candidate.

## The confirmation standard

A class verdict of `confirms` needs ALL of:

1. **The request that caused it** — method, path, and the exact field or
   step that was added, skipped, replayed, or pushed past a boundary.
2. **A verbatim response excerpt** showing the forbidden state:
   - `role: admin` in a read-back after sending `role=admin` at register.
   - `status: confirmed` on an order whose payment step was skipped.
   - `balance: 200` after replaying a one-time redeem.
   - `total: -50` after sending `quantity=-1`.
   - `status: processed` for an ID the documented limit excludes.
3. **A baseline** — the same request without the manipulation, showing the
   state does NOT change. Without a baseline, `balance: 200` proves nothing.
4. The excerpt is a substring of the recorded `--response` — `hooks.py
   post-probe` checks this mechanically.

```bash
python3 tools/hooks.py post-probe <challenge> \
  --request "POST /register {username:probe,password:x,role:admin}" \
  --verdict confirms --class web-logic-flaw \
  --hypothesis-id <id> \
  --evidence-kind class \
  --evidence '"role": "admin"' \
  --response "$(cat resp_register.json)"
```

## Evidence grades

| Grade | What it is | Example | Weight |
|---|---|---|---|
| **impact** | the exploit's end state, verbatim | `{"flag": ...}` after the chain | confirms impact |
| **class** | a forbidden state transition, verbatim | `role: admin`, `total: -50` | confirms class |
| **surface** | a shape consistent with the class | registration succeeds, form renders | candidate only |
| **negative** | the falsifier fired | `role: user` after sending `admin` | rules the shape out — RECORD IT |

## What never confirms

- **A `200 OK` alone.** Registering succeeds for ordinary users too.
- **A validation error message.** `"role is not allowed"` says the field
  exists in a schema — it does not say the field reaches the model.
- **A reflected field.** `{"role": "admin"}` echoed in the *response to the
  write* is only half the test — read the object back through a separate
  GET before calling it stored.
- **A UI difference.** A rendered admin panel in HTML the server still
  gates server-side is surface evidence.
- **A timeout or connection reset.** Never a confirm — for anything.
- **A chain-card match.** `chain_match` names a candidate shape. The
  Pachinko card's shape — checked value transformed before use — must be
  re-proven on THIS target.
- **A second request that differs in two ways.** Sending
  `quantity=-1&coupon=X` and crediting the `-1` when the coupon caused it
  is a misattribution — one probe, one changed variable.

## The baseline discipline

Every logic-flaw verdict needs two rows:

| Request | Response excerpt |
|---|---|
| `POST /register {...}` (no `role`) | `"role": "user"` |
| `POST /register {..., "role":"admin"}` | `"role": "admin"` |

Same for replays — the serial baseline first. A second `POST /redeem` that
returns `409 code already redeemed` is the baseline; the `200` that adds
the credit twice is the anomaly worth recording.

## Recording the verdict

```bash
# class evidence — the forbidden state transition
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" \
  --verdict confirms --class web-logic-flaw \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"admin"' --response "$(cat r.json)"

# a falsifier firing is a verdict too — record it, don't bury it
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" \
  --verdict falsified --class web-logic-flaw \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"user"' --response "$(cat r.json)"
```
