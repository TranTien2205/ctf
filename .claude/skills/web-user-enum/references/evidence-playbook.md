# Evidence playbook — the prove-it runbook

## The verbatim-oracle record

```json
{
  "form": "/api/login",
  "channel": "json-error",
  "arms": {
    "good":  {"user":"admin","code":401,"body":"{\"error\":\"bad_password\"}"},
    "bad1":  {"user":"zzz-x","code":404,"body":"{\"error\":\"user_not_found\"}"},
    "bad2":  {"user":"qqq-y","code":404,"body":"{\"error\":\"user_not_found\"}"}
  },
  "verdict": "json-error oracle: 404/user_not_found vs 401/bad_password"
}
```

## The per-channel verbatim

- **body**: the two error blocks, verbatim (`"No such user"` / `"Wrong
  password"`), noise-masked
- **status+redirect**: `HTTP/1.1 302` + `Location: /login?error=user` vs
  `?error=pass`, byte-identical across `bad1`/`bad2`
- **timing**: `good_med=247ms bad_med=8ms jitter=4ms delta=239ms N=12`,
  plus the re-run `242/7`
- **side**: `Set-Cookie: auth_attempt=1` present on `good`, absent on
  `bad1`/`bad2`
- **send**: `{"emails_queued":1}` vs `{"emails_queued":0}`
- **lock**: `HTTP/1.1 423` + `"account locked"` on `good` at attempt 6,
  `200 "invalid"` on `bad` at attempt 20

## The hook call

```bash
python3 tools/hooks.py post-probe <chal> --hypothesis-id <h> \
  --class web-user-enum --verdict confirms --evidence-kind class \
  --evidence 'bad: {"error":"user_not_found"} good: {"error":"bad_password"}' \
  --response '<the verbatim response>'
```

## The throttle verbatim

- absent: `burst=15: codes=200 200 200 ... 200, no 429/423/delay`
- threshold: `attempts: 1..7=200, 8=429 "rate limited"`
- bypass: `X-Forwarded-For: 9.9.9.9 -> 200 (post-429 reset)`

## The provenance

Each record carries `form, channel, the three arms' excerpts, N, verdict`.
A lead without the verbatim pair is not traceable; a finding without a
re-run is not a finding.
