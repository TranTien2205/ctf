# Per-endpoint-class — each mined endpoint type and its class

## The object-reference endpoint

| Shape | Route |
|---|---|
| `/api/user/{id}`, `/api/post/{id}`, `?id=`, `?uid=`, `?pk=` | `web-idor` |

A named object param is an IDOR probe — the map named the param.

## The query/filter endpoint

| Shape | Route |
|---|---|
| `?q=`, `?search=`, `?filter=`, `?sort=`, `?order=`, `?where=` | `web-sqli`/`web-nosqli` |
| a JSON `filter`/`where` body | `web-nosqli`/`web-sqli` |

## The fetch/proxy endpoint

| Shape | Route |
|---|---|
| `?url=`, `?uri=`, `?target=`, `?callback=`, `?webhook=`, `/proxy`, `/fetch`, `/preview`, `/screenshot`, `/render-url` | `web-ssrf` |

## The file endpoint

| Shape | Route |
|---|---|
| `/file/`, `?file=`, `?path=`, `?name=`, `?doc=`, `/download`, `/read`, `/view`, `/static/` traversal | `file-read-primitives` |

## The render/template endpoint

| Shape | Route |
|---|---|
| `?template=`, `?render=`, `?message=`, `?name=` rendering into a template | `web-ssti`/`web-xss` |

## The auth endpoint

| Shape | Route |
|---|---|
| `/login`, `/auth`, `/token`, `/session`, `/reset`, `/oauth`, `/sso` | `web-auth-session`/`web-oauth-sso` |
| `/verify`, `/otp`, `/mfa` | `web-auth-session` |

## The admin/internal endpoint

| Shape | Route |
|---|---|
| `/admin`, `/internal`, `/debug`, `/management`, `/actuator`, `/metrics`, `/console` | `web-logic-flaw`/`web-idor`/`web-info-disclosure` |

## The action/economic endpoint

| Shape | Route |
|---|---|
| `/transfer`, `/pay`, `/purchase`, `/redeem`, `/apply`, `/bet`, `/spin` | `web-logic-flaw`/`web-race-condition` |
| `/export`, `/dump`, `/backup`, `/import` | `web-logic-flaw`/`file-read-primitives` |

## The upload endpoint

| Shape | Route |
|---|---|
| `/upload`, `/import`, `/avatar`, `/attach` | `web-file-upload` |

## The GraphQL endpoint

| Shape | Route |
|---|---|
| `/graphql`, `/gql`, `/api/graphql`, `/query` | `web-graphql` |

## The redirect endpoint

| Shape | Route |
|---|---|
| `?redirect=`, `?next=`, `?return=`, `?return_to=`, `?goto=` | `web-open-redirect` |

## The realtime endpoint

| Shape | Route |
|---|---|
| `ws://`, `wss://`, `/socket.io`, `/ws`, `/realtime` | `web-websocket` |

## The classification rule

Each endpoint routes to the class its *verb + param shape* implies.
When it implies several, the cheapest-class first probe wins — an
`?id=` that is also a query body gets `web-idor`'s existence oracle
before `web-sqli`'s injection oracle.
