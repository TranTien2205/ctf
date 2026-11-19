# Per-route — what each mined route is worth

## The route table

SPA route definitions (`path:`/`component:`) name every page the app
knows. A route the UI hides — `/admin`, `/internal`, `/debug`,
`/secret` — is a lead even if it is client-side, because some map to
server endpoints.

## Client route vs server endpoint

| Route | Test |
|---|---|
| `/admin` (react-router) | is there a `/api/admin` it calls? probe it |
| `/api/admin` (an endpoint string) | `curl` it — a real response is a target |
| `/dashboard/:id` | the `:id` param is an IDOR probe |
| a lazy route in the manifest | a page chunk + its endpoints |

## The route-endpoint gap

A named client route does not always hit a server endpoint — many are
pure client views. Probe each named route against the API prefix; the
ones that respond are real. The 404s are client-only — record them as
dead.

## The param-rich route

A route `/user/:id`, `/file/:name`, `/order/:orderId` names a parameter
the client fills — the param's name + the endpoint it feeds is an
IDOR/file-read target. The route tells you the param exists and what
to call it.

## The hidden-route priority

| Route | Priority |
|---|---|
| `/admin`, `/internal`, `/debug`, `/api/admin` | high |
| `/export`, `/backup`, `/config`, `/settings` | high |
| `/:id`, `/user/:id`, `/file/:name` | IDOR probe |
| `/login`, `/public`, `/index` | low — public by design |
