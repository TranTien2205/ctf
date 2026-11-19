# Per-param — each named parameter and its exploit path

## The param semantic table

A param name is a signal — it names what the server does with the
value. The map surfaces the param; its semantics route to the class.

| Param | Semantics | Route |
|---|---|---|
| `id`,`uid`,`user_id`,`pk`,`post_id`,`order_id`,`doc_id` | an object ref | `web-idor` |
| `file`,`path`,`filename`,`name`,`doc`,`page`,`include`,`template`,`view` | a file/resource | `file-read-primitives` |
| `url`,`uri`,`link`,`callback`,`webhook`,`target`,`dest`,`host`,`domain`,`fetch` | a server fetch | `web-ssrf` |
| `q`,`query`,`search`,`keyword`,`filter`,`sort`,`order`,`where`,`field` | a query | `web-sqli`/`web-nosqli` |
| `redirect`,`return`,`next`,`return_to`,`goto`,`continue`,`url`,`dest` | a redirect | `web-open-redirect` |
| `token`,`key`,`secret`,`password`,`otp`,`code`,`pin`,`auth` | auth material | `web-auth-session` |
| `role`,`admin`,`is_admin`,`isAdmin`,`permission`,`level`,`type`,`group` | a privilege | `web-mass-assignment`/`web-logic-flaw` |
| `amount`,`price`,`balance`,`quantity`,`discount`,`total`,`cost`,`rate` | an economic field | `web-logic-flaw`/`web-race-condition` |
| `__proto__`,`constructor`,`prototype`,`proto` | pollution | `web-prototype-pollution` |
| `message`,`comment`,`text`,`title`,`bio`,`signature` | stored content | `web-xss`/`web-ssti` |
| `template`,`render`,`engine`,`format` | a render | `web-ssti` |
| `cmd`,`command`,`exec`,`ping`,`host`,`ip` | a command | `web-command-injection` |
| `xml`,`data`,`payload` (XML body) | an XML parse | `web-xxe`/`web-deserialization` |
| `action`,`method`,`callback`,`handler`,`op` | a dispatch | `web-logic-flaw` |
| `json`,`filter`,`query` (object value) | an object query | `web-nosqli`/`web-mass-assignment` |
| `debug`,`verbose`,`test`,`dev`,`trace` | a debug flag | `web-logic-flaw`/`web-info-disclosure` |

## The hidden param

A param the client sends but the UI does not expose — a debug flag, an
admin param, a `role` the form omits — is a `web-mass-assignment`/
`web-logic-flaw` lead: the server reads it, the UI just does not offer
it.

## The param-shape signal

The *value* the client sends hints at the sink:

- a JSON object → `web-mass-assignment`/`web-prototype-pollution`
- a path/`../` value → `file-read-primitives`
- a URL value → `web-ssrf`
- a template/`{{`/`${` value → `web-ssti`
- a numeric id → `web-idor`
- a serialized blob → `web-deserialization`

## The param-source read

Grep the param's usage — `data.id`, `body.file`, `params.q` — to find
the endpoint it feeds and the shape the server expects. The param's
context is the request contract.

## The param → endpoint chain

The param is only useful with its endpoint — the map names both. A
`file` param on `/read` is a `file-read` lead; a `url` param on
`/proxy` is an `web-ssrf` lead. Pair each param with its endpoint.
