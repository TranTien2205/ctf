# Param surface — the request parameters the bundle names

## Why params matter

The bundle names the parameters the client sends — the keys the server
expects. A param name is an injection point; a param value's shape is a
hint at what the server does with it. Mining params maps the server's
input surface.

## The param extraction

```bash
# object keys sent in a request body
grep -oE '[{,]\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*:\s*[,}]' bundle.js | sort -u
# URLSearchParams / FormData fields
grep -oE '(append|set|get|delete)\s*\(\s*["'"'"'][a-zA-Z_$]+' bundle.js | sort -u
# a query-string param
grep -oE '[?&][a-zA-Z_$]+=' bundle.js | sort -u
# a template-literal param
grep -oE '\$\{[a-zA-Z_$][a-zA-Z0-9_$.]*\}' bundle.js | sort -u
# axios/fetch body params
grep -oE '(body|data|params|payload)\s*:\s*\{[^{}]{10,}' bundle.js | head -30
```

## The param-name semantics

| Param name | Hints at |
|---|---|
| `id`, `user_id`, `uid`, `pk`, `post_id` | an object reference → `web-idor` |
| `file`, `path`, `filename`, `name`, `doc` | a file read → `file-read-primitives` |
| `url`, `uri`, `link`, `callback`, `webhook`, `target` | a fetch → `web-ssrf` |
| `q`, `query`, `search`, `filter`, `sort`, `order` | a query → `web-sqli`/`web-nosqli` |
| `template`, `render`, `message`, `name` | a render → `web-ssti`/`web-xss` |
| `redirect`, `return`, `next`, `return_to`, `goto` | a redirect → `web-open-redirect` |
| `token`, `key`, `secret`, `password`, `otp`, `code` | auth material → `web-auth-session` |
| `role`, `admin`, `is_admin`, `isAdmin`, `permission` | a privilege → `web-mass-assignment`/`web-logic-flaw` |
| `amount`, `price`, `balance`, `quantity`, `discount` | an economic field → `web-logic-flaw` |
| `__proto__`, `constructor`, `prototype` | pollution → `web-prototype-pollution` |

## The param-shape read

The *value* the client sends hints at the sink:

- a JSON object → `web-mass-assignment`/`web-prototype-pollution`
- a path-looking value → `file-read-primitives`
- a URL value → `web-ssrf`
- a template-looking value → `web-ssti`
- a numeric id → `web-idor`

## The hidden param

A param the client sends but the UI does not expose — a debug flag, an
admin param, a `role` the form omits — is a `web-mass-assignment`/
`web-logic-flaw` lead: the server reads it, the UI just does not offer it.

## The param → class route

Each named param routes to the class its semantics imply. The param
surface is the injection-point map the class's own skill then works.
