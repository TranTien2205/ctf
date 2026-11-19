# Evidence (deep) — the verbatim record, in full

## The evidence envelope

Every confirmed oracle record carries:

```json
{
  "form": "/api/login",
  "channel": "json-error-code",
  "good": {"user":"admin","excerpt":"{\"error\":\"bad_password\"}","status":401},
  "bad1": {"user":"zzz-NOSUCH","excerpt":"{\"error\":\"user_not_found\"}","status":404},
  "bad2": {"user":"qqq-FAKE","excerpt":"{\"error\":\"user_not_found\"}","status":404},
  "verdict": "json-error-code oracle on /api/login",
  "confirmed_accounts": ["admin","service"]
}
```

## The verbatim excerpts — per channel

### body
```
good:  <div class="err-BADPASS">Invalid password</div>
bad1:  <div class="err-NOUSER">No such user</div>
bad2:  <div class="err-NOUSER">No such user</div>
```

### status + redirect
```
good:  302  Location: /login?error=pass
bad1:  302  Location: /login?error=user
bad2:  302  Location: /login?error=user
```

### timing
```
good_med=247ms  bad_med=8ms  jitter=4ms  delta=239ms  N=12  (re-run: 242/7)
```

### side-artifact
```
good:  Set-Cookie: auth_attempt=1; Path=/
bad1:  (none)
bad2:  (none)
```

### send side-effect
```
good:  {"emails_queued":1}
bad1:  {"emails_queued":0}
```

## The noise-mask record

The noise-masked fields are recorded too — `bad1` vs `bad2` showed only
`csrf`/`timestamp`/`request_id` varying, which was masked before the
good/bad diff. The masked-diff excerpt proves the signal survived.

## The re-run record

A single measured delta is a lead; a delta that re-runs on a SECOND bad
name and a re-ordered second pass is a finding. The record carries both
runs.

## The hook call — verbatim

```bash
python3 tools/hooks.py post-probe <chal> --hypothesis-id <h> \
  --class web-user-enum --verdict confirms --evidence-kind class \
  --evidence 'bad: {"error":"user_not_found"} vs good: {"error":"bad_password"}' \
  --response '<the full JSON response>'
```

The `--evidence` excerpt must be a substring of `--response` — the gate
checks. Never paraphrase; quote the bytes.
