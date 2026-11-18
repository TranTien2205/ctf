# Evidence rules — what proves what

The repository's proof standard applies to every claim here. This file maps
each GraphQL observation to the verdict it supports — and what it does NOT
support.

---

## 1. The evidence taxonomy

| Observation | Supports | Does NOT support |
|---|---|---|
| `{"data":{"__typename":"Query"}}` | endpoint is GraphQL | any bug |
| `__schema` returns types | introspection open; capability | a finding |
| `Did you mean "users"?` | field `users` exists | `users` resolves without authz |
| `Cannot query field "x"` | field x does not exist (on this type) | anything else |
| `argument "id" of type "ID!" is required` | field exists + arg shape | the field resolves |
| `Cannot return null for non-nullable` | resolver ran, returned null | authz applied |
| `errors:[{message:"Forbidden",path:[f]}]` | per-resolver authz present | field is safe |
| `{"data":{"user":{...}}}` | field resolves | the data is *another tenant's* — ownership check needed |
| `{"data":{"user":{"email":"other@x"}}}` + own-id control | cross-tenant read — impact | — |
| `errors:[{message:"sqlite3.OperationalError..."}]` | SQL reachable — sqli class | the sqli is exploitable |
| `{"data":{"login":{token}}}` returned under `mutation` | mutation ran | the token works |
| `200` on `x-hasura-role:admin` | role accepted | admin data returned — still need the read |

## 2. The verdict ladder

```text
refutes      →  the probe produced the falsifier (e.g., not GraphQL at all)
inconclusive →  probe ran, signal ambiguous (timeout, weird parse, masked error)
candidate    →  capability exists (schema open, suggestion oracle live,
                injection-point reaches a parser) — no harm yet
confirms(class)   →  the *class* of bug confirmed — schema/transport evidence
confirms(impact)  →  the *harm* confirmed — leaked private data, crossed
                     boundary, privilege change
```

The `confirms` ladder is what `post-probe` enforces: `--evidence-kind class`
for capabilities, `--evidence-kind impact` for harm. A schema response is
`class`. A `user{email}` that belongs to a *different* tenant is `impact`.

## 3. The verbatim-evidence contract

`--evidence` must be a substring of `--response` — the gate checks. So:

- Quote the *exact* bytes — `"email":"victim@x.tld"` not `email leaked`.
- Include enough context to show it's a foreign object — `"user":{"id":5,
  "email":"victim@x.tld"}` — the `id:5` shows it isn't yours.
- For mutations, quote the returned state — `"role":"admin"` from a
  `setAdmin` response, and the `Before`/`After` if both shown.
- For error oracles, quote the message — `"message":"Cannot query field
  \"secret\" on type \"Query\". Did you mean \"secrets\"?"`

## 4. What does NOT count as evidence

| Non-evidence | Why |
|---|---|
| A tool's own log saying "field exists" | tool output is not a response |
| An LLM-written summary of a response | re-typed is not verbatim |
| A screenshot's alt-text | not the bytes |
| A writeup's claim it worked | provenance ≠ proof |
| A response you constructed | not the server's bytes |
| A schema naming `flag` field | capability ≠ resolution |
| An error `Did you mean "flag"` | field name exists — but resolving it is the test |
| `200` status | transport success ≠ harm |
| `errors:[]` empty | nothing failed ≠ data returned |

## 5. The negative-evidence ledger

`refutes` needs evidence too — the falsifier observed verbatim:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {users{email}}' \
  --verdict refutes --evidence-kind class --class web-graphql \
  --hypothesis-id h1 \
  --evidence '"message":"Forbidden","path":["users","email"]' \
  --response '<verbatim>'
```

Record the negative so the next agent doesn't re-probe. The falsifier list
per class:

| Hypothesis | Falsifier |
|---|---|
| introspection open | `Cannot query field "__schema"` or `data.__schema:null` |
| suggestion oracle live | every typo'd name returns identical generic error |
| `_service` resolves | `Cannot query field "_service"` |
| `node()` exists | `Cannot query field "node"` |
| object-level authz absent | every foreign-id probe returns `Forbidden`/null |
| injection reaches SQL | `'` produces no driver text AND no behaviour change |
| batching accepted | `Must be a single object` on `[{...}]` |
| form-CT accepted | `400 Unsupported content type` on `query={...}` |
| mutation over GET | `405` or `Can only perform a mutation operation from a POST request` |
| WS channel live | handshake refuses both subprotocols |
| Hasura role-spoof | `x-hasura-role:admin` → 401/403 |

## 6. The impact-standard

`confirms --evidence-kind impact` for GraphQL specifically requires:

- **Read-impact**: a field returning data the caller should not have —
  another tenant's email, a token, a flag, a private document. Control:
  repeat with your own id (returns your data) and a nonexistent id (null) —
  three classes proves the boundary.
- **Write-impact**: a mutation that changed state you shouldn't control —
  self-`role:"admin"` after, or another object's field mutated.
- **Authz-bypass-impact**: an admin field resolved with a non-admin token.
- **Injection-impact**: a query argument reaching SQL/NoSQL/shell — driver
  text in `errors` is the class-confirm; the flag/extracted value is the
  impact.

A `users{id}` returning public usernames is **not** impact — public data is
public. `users{email}` returning real emails is.

## 7. The flag standard

The flag is `flag{...}`-shaped text from a live response or supplied
artifact, passed through `pre-flag`. GraphQL shapes it comes in:

```json
{"data":{"flag":{"value":"flag{...}"}}}
{"data":{"flag":"flag{...}"}}
{"data":{"internal":{"secret":"flag{...}"}}}
{"data":{"debug":{"env":[{"name":"FLAG","value":"flag{...}"}]}}}
{"data":{"getFlag":{"result":"flag{...}"}}}
{"errors":[{"message":"flag{...}","path":["flag"]}]}    # via forced-error
{"data":{"node":{"value":"flag{...}"}}}                 # via node()
{"data":{"_entities":[{"value":"flag{...}"}]}}          # via _entities
```

Any shape counts — the rule is the *value is in a live response*. A flag
extracted char-by-char through blind oracle counts once the assembled value
is submitted to `pre-flag` with the response excerpt showing the oracle hits.

## 8. Hook shapes

```bash
# capability confirmed — class evidence
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {__schema{types{name}}}' \
  --verdict confirms --evidence-kind class --class web-graphql \
  --hypothesis-id h1 --evidence '"types":[...]' --response '<verbatim>'

# harm confirmed — impact evidence
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h2 --evidence '"email":"victim@x.tld"' --response '<verbatim>'

# falsifier observed
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {users{email}}' \
  --verdict refutes --evidence-kind class --class web-graphql \
  --hypothesis-id h3 --evidence '"message":"Forbidden"' --response '<verbatim>'

# flag
python3 tools/hooks.py pre-flag $CHAL \
  --value 'flag{abc123}' --source response --evidence '"value":"flag{abc123}"'
```
