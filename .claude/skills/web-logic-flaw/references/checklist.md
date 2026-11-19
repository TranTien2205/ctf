# Checklist — the business-logic audit, ordered by cost

## Recon (free)

- [ ] endpoints enumerated (bundle_miner or crawl)
- [ ] field map from GET responses written down
- [ ] happy-path baseline saved verbatim
- [ ] classify + chain_match run and recorded

## The 60-second probes

- [ ] `GET /flag`, `GET /admin`, `GET /export` bare — terminal endpoints
      checking nothing
- [ ] `POST /register {..., "role":"admin"}` + read-back
- [ ] terminal workflow step called with no earlier steps
- [ ] one-time action replayed once, serially

## The field sweep

- [ ] `role`, `isAdmin`, `verified`, `balance`, `permissions`, `plan`
      per write endpoint
- [ ] `PATCH`/`PUT` binder probed separately from `POST`
- [ ] nested `{"user":{"role":"admin"}}` and `{"role":["admin"]}` paths
- [ ] boundary alphabet per numeric field: `-1`, `0`, `NaN`, `1e309`,
      `2147483648`, `0x10`

## The workflow sweep

- [ ] each non-first step called bare
- [ ] steps reordered: last→first, middle→end
- [ ] `step`/`state` values forged in cookie, param, body
- [ ] out-of-range step: `0`, `-1`, `N+1`

## The replay sweep

- [ ] serial replay ×2, ×3
- [ ] same key + mutated body
- [ ] cross-user replay
- [ ] replay after compensating action (redeem→refund→redeem)

## The transform sweep

- [ ] `id` at documented limit, limit+1, word boundaries
- [ ] rejection shape diffed: out-of-limit vs malformed
- [ ] wrap targets computed: `off + id*S mod 2^w`

## The trust sweep

- [ ] every hidden field mutated between mint and submit
- [ ] carried `total`/`price`/`state` resubmitted modified
- [ ] boundary headers set directly (`Referer`, `Origin`, `X-Forwarded-*`)

## Evidence

- [ ] every probe has its baseline pair
- [ ] every verdict through `post-probe` with `--response`
- [ ] falsifiers recorded, negatives recorded
- [ ] flag through `pre-flag` against live response

## Closure

- [ ] solve filed via `classify_solve.py`, or
- [ ] escalation rung spent via `decide.py`, or
- [ ] kill map written to `knowledge/attempts/`
