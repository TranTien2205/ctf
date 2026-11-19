# Lead grammar — every string shape and what it claims

## The endpoint grammar

| Shape | Claims | Verify |
|---|---|---|
| `"/api/x"` | a server API path | `curl $BASE/api/x` — real or catch-all |
| `"/v2/x"` `"/internal/x"` | a versioned/internal API | same |
| `fetch("x")` `axios.get("x")` | the call site | the literal arg + the baseURL |
| `path:"/x"` `Route("/x")` | a client route | prefix `/api/` → server path or client-only |
| `"/graphql"` | a GraphQL endpoint | `web-graphql` |
| `ws://` `wss://` `/socket.io` | a realtime channel | `web-websocket` |

## The secret grammar

| Shape | Claims | Verify |
|---|---|---|
| `eyJ…\.…\.…` | a JWT | decode + test `Authorization` |
| `AKIA…` `AIza…` `ghp_…` `xoxb…` | a provider key | authenticate against the provider |
| `sk_live_…` `pk_live_…` | a Stripe key | `sk_` is secret, `pk_` is publishable |
| `-----BEGIN … PRIVATE KEY` | a private key | the strongest candidate |
| `(api_key|secret|token|password)\s*[:=]` | a credential | authenticate |
| `postgres://` `mongodb://` `redis://` | a connection string | reach + auth |
| `process.env.X` `import.meta.env.X` `VITE_X` | an env ref | the inlined value |

## The flag/config grammar

| Shape | Claims | Verify |
|---|---|---|
| `feature.X` `flags.X` `config.X` | a client gate | probe the gated endpoint |
| `isAdmin` `is_admin` `role` `permission` | a client privilege flag | a `role`/param the server may bind |
| `meta.requiresAuth` `PrivateRoute` `canActivate` | a client route guard | probe the gated route's endpoint |
| `localStorage.getItem('admin')` | a client storage gate | set the flag or the param the client sends |

## The structural grammar

| Shape | Claims | Verify |
|---|---|---|
| `sources:["src/x.ts"]` | the original file path | probe the hosted `/src/` path |
| `?x=` `?url=` `?file=` `?id=` `?redirect=` | an injection point | its class's first probe |
| `?debug=` `?internal=` `?admin=` | a debug param | a `?debug=1` probe |
| `eval(` `innerHTML` `.exec(` `deserialize(` | a sink | its class's depth skill |
| a comment `TODO`/`secret`/`flag{` | a dev note/flag | the string is a candidate |

## The verdict grammar

Every lead is one of `live`, `dead`, `unverifiable`, `candidate`. A
`live` lead is routed; a `dead` lead is a recorded negative; an
`unverifiable` lead is routed with the note; a `candidate` flag-shape
goes through `pre-flag`.
