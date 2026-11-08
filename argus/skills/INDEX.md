# Argus knowledge modules

Load one at a time with `load_skill("<name>")` - only when the signal points
at that bug class. Each module carries: when it applies, first probes, what
actually confirms the bug, and bypasses for common filters.

## Signal -> skill

| Observed | Skill |
|---|---|
| Value reaches a SQL query; error / boolean / timing delta | `sqli` |
| JSON object-shaped filter honoured (`$ne`, `$gt`) | `nosqli` |
| Value reflected into HTML/attr/JS context | `xss` |
| Value rendered by a template engine | `ssti` |
| Server fetches a controlled URL; webhook/pdf/bot | `ssrf` |
| Request data reaches a shell call | `command-injection` |
| File read built from a request value | `file-read` |
| Upload with weak ext/type/content checks | `file-upload` |
| XML parser, external entities | `xxe` |
| Object id in path/body, no ownership check | `idor` |
| Token/cookie signed, key in token or leaked | `auth-session` |
| Login/reset reveals which accounts exist | `auth-enum` |
| Deep merge over request JSON; `__proto__` | `prototype-pollution` |
| Check-then-act on balance/coupon/one-time | `race-condition` |
| ACAO reflects origin; credentials allowed | `cors` |
| Cross-origin state change, no token check | `csrf` |
| Param naming the next destination | `open-redirect` |
| Proxy/gateway parses differently than backend | `request-smuggling` |
| Single endpoint taking a query document | `graphql` |
| Extra fields accepted; skippable step | `logic-flaw` |
| 403s, verbose errors, debug routes, .git | `info-disclosure` |
| Cookie/param deserializes (pickle, Java, PHP) | `deserialization` |
| Cache in front; unkeyed inputs reflected | `cache-poisoning` |
| ws:// channel, Socket.IO | `websocket` |
| Value lands in a response header unencoded | `crlf` |
| First pass over an unknown target | `triage` |
