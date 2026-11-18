# Denied conditions — when this class is actually closed

The falsifiers that close `web-graphql` — each is a `post-probe
--verdict refutes` with the verbatim observation. Record these so the next
agent doesn't re-walk them.

---

## 1. The class-level falsifiers

| Observation | Closes |
|---|---|
| `{__typename}` → `Cannot query field "__typename"` | not GraphQL — class fully closed |
| `{__typename}` → 404 HTML | route isn't graphql — class fully closed |
| `{__typename}` → `Unexpected token` / generic parse error | not a graphql parser |
| `{__schema{types{name}}}` → `Cannot query field "__schema"` + `__type(name:"Query")` → same + `_service{sdl}` → same + `did you mean` never appears + bundle has no query docs + WS refuses both subprotocols | no schema recovery channel — class effectively closed for *discovery*, but **not** the class itself — the JS bundle may still hold a query doc |

The last row is the critical nuance: "introspection off" is not the falsifier.
"Introspection off AND suggestions stripped AND `_service` absent AND no
bundle queries AND WS dead" is.

## 2. The per-mechanism falsifiers

### 2.1 IDOR surface

```text
Hypothesis: user(id:) reads cross-tenant
Falsifier: every foreign-id probe returns Forbidden/null,
           nested paths (post.author, comment.author, order.user) same,
           node() returns Forbidden or doesn't exist,
           _entities returns Forbidden or doesn't exist
```

Record:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}}' \
  --verdict refutes --evidence-kind class --class web-graphql \
  --hypothesis-id h9 --evidence '"message":"Forbidden"' --response '<verbatim>'
```

### 2.2 Injection surface

```text
Hypothesis: search(q:) reaches SQL
Falsifier: quote probe returns no driver text AND no behavior change
           across 3 DBMS shapes; errors always generic
```

### 2.3 Mass-assignment surface

```text
Hypothesis: register input accepts extra keys
Falsifier: every extra key rejected with "Field X is not defined"
```

### 2.4 Privesc surface

```text
Hypothesis: role mutation callable without authz
Falsifier: every *Role/grant/promote mutation returns Forbidden
```

### 2.5 Node-interface surface

```text
Hypothesis: node(id:) resolves arbitrary types
Falsifier: node(id) returns Forbidden, or node doesn't exist on Query,
           or every typename prefix errors Unknown type
```

### 2.6 Federation surface

```text
Hypothesis: _service/_entities leaks schema or entities
Falsifier: both fields return Cannot query field, or both return Forbidden
```

### 2.7 CSRF/transport surface

```text
Hypothesis: endpoint accepts non-JSON carriers
Falsifier: form-urlencoded → 400, GET → 405/400, text/plain → 415/400
```

### 2.8 Subscription surface

```text
Hypothesis: WS channel live
Falsifier: handshake refuses both graphql-transport-ws and graphql-ws
           subprotocols, or connection_init never gets connection_ack
```

### 2.9 Batching surface

```text
Hypothesis: array batching accepted
Falsifier: [{...}] returns "Must be a single object" / "Batching is not supported"
```

### 2.10 Type-confusion surface

```text
Hypothesis: scalar arg accepts object via variables
Falsifier: every typed-confusion probe returns Expected type X, found Y
```

## 3. The chain falsifier — when to stop

The class is *effectively* closed when:

```text
All of:
  - introspection channels exhausted (incl. _service, __type, suggestions)
  - the JS bundle holds no query documents
  - no sensitive field resolves (unauth, low-priv, all paths)
  - no mutation resolves (unauth, low-priv)
  - transport carriers are POST+JSON only
  - WS refuses both subprotocols
  - batching rejected
  - all type-confusion probes rejected
  - every admin-shaped name errors the same way
```

At that point the ledger records the class `refutes` and the challenge
pivots — the surface was never GraphQL-shaped, or every surface is correctly
authz'd, or the flag lives behind a different bug class entirely
(`web-idor`, `web-sqli`, `web-ssti` on the non-GraphQL routes).

## 4. The "looks-closed-but-isn't" traps

| Looks closed | Actually |
|---|---|
| `Cannot query field "__schema"` | try `__type(name:"X")` — different field |
| `Introspection is disabled` | try `_service{sdl}` — not introspection |
| `Mutation not supported via GET` | try POST — transport, not authz |
| `Field "x" not defined` on input | try another field — strict input ≠ strict resolver |
| `Forbidden` on `admin{...}` | try `debug{...}`, `internal{...}`, `backdoor{...}` — different names |
| `Not found` on `user(id:5)` | try `user(id:"5")`, `user(id:"05")`, `node(id:"VXNlcjo1")` — type tricks |
| `401` on unauth | get ANY session — even a fresh-registered user unlocks the surface |
| `PersistedQueryNotAllowed` | register a hash — `persisted-queries.md` |
| `Rate limit` | batch/alias inside one request — `batching-attacks.md` |
| `403` on POST+JSON | try form-urlencoded — middleware order bug |

## 5. What "closed" actually means for the ledger

```bash
python3 tools/state.py $CHAL --bug-class web-graphql
python3 tools/state.py $CHAL --hypothesis \
  "closed: all surface probes refuted — flag lives in another class"
python3 tools/decide.py $CHAL   # next class to try
```

A class closed after all channels refuted is *progress* — the ledger says
"not graphql" and `decide.py` names the next shape. The cost of the wrong
class was bounded — that is the design.
