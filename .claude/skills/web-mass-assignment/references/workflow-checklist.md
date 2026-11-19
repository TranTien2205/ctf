# Workflow checklist — the engagement step-by-step

## Phase 0 — setup

- [ ] `state.py <name> --category web --target <url>` run
- [ ] `classify.py "<obs>"` run — class named or considered
- [ ] `chain_match.py --record <name>` run — any card match?
- [ ] `bundle_miner --url <bundle> --out /tmp/bundle` — endpoints + sources

## Phase 1 — inventories

- [ ] `GET /api/me` / object detail — full field list
- [ ] bundle grepped — `role|admin|balance|verified|price|plan|perm`
- [ ] wrong-typed probe — schema leaked via error
- [ ] docs/introspection — `/openapi.json`, `__schema`
- [ ] admin/sibling views — the full field set

## Phase 2 — binder fingerprint

- [ ] stack identified — headers, errors
- [ ] binder family — merge-all / kwargs / allowlist / strict
- [ ] content-types — JSON, form, multipart
- [ ] method permutations — POST, PATCH, PUT, override
- [ ] nested/array/prefixed support

## Phase 3 — first probe

- [ ] control request — documented body, captured
- [ ] canary — ONE extra field on the widest endpoint
- [ ] read-back — DIFFERENT endpoint
- [ ] falsifier depth annotated

## Phase 4 — decision exercise

- [ ] gated route hit — `/admin`, `/flag`, `/premium`, `/checkout`
- [ ] decision changed vs control session
- [ ] verbatim evidence captured

## Phase 5 — widen or stop

- [ ] falsifier depth → remaining cells queued
- [ ] `decide.py` consulted on exhaustion
- [ ] `post-probe` verdicts recorded per cell
- [ ] class/impact evidence kinds used correctly

## Phase 6 — close

- [ ] flag through `pre-flag` against live response
- [ ] `classify_solve.py --chain <id>` — promotes catalogue→verified
- [ ] `../field-notes.md` updated with the mechanism, falsifiers, carriers
- [ ] background processes cleaned
