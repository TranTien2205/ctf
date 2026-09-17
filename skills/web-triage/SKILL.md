---
name: web-triage
description: >
  Web recognition router. Use at the START of any web challenge, white-box or
  black-box. Maps one observed source or response signal to one bug class and the
  cheapest first probe, then names the depth skill. Routes; does not solve.
tags: [web, jeopardy, triage, recognition, ctf]
environment: [ctf]
---

# Web — Recognition Router

The task is not to enumerate. It is: find the sink, prove one bug, reach one
flag. The bug you need is the one that reaches the flag, not the most impressive
one on the page.

## Step 0 — before any payload

**White-box (source supplied)**

1. Read all of it. Find where a request value reaches a dangerous sink, and note
   file and line.
2. Record the stack: language, framework, datastore, parser, template engine,
   reverse proxy.
3. Locate the flag: environment variable, database row, file on disk, or a route
   only a privileged identity can reach.

**Black-box (target only)**

1. Fetch the entry page. Read the front-end JavaScript and list every endpoint it
   calls — each one is a real endpoint, and this beats directory brute force.
2. Note the stack from response headers, cookie names, error pages and HTML
   comments.
3. Test each observed endpoint: method, body shape, response shape, and what
   changes when a field is removed.
4. Only then consider hidden routes.

Run `python3 ~/ctf/tools/chain_match.py` before opening any depth skill.

## Signal to class to first probe

| Source or response signal | Class | First probe | Depth |
|---|---|---|---|
| A request value concatenated into a query; SQL error; boolean or timing delta | SQL injection | one syntax marker, then a true/false pair | `../web-sqli/` |
| An object-shaped filter accepted from a JSON body; comparison operators honoured | NoSQL injection | send the filter pinned to your own object id, with write fields omitted | `../web-sqli/references/nosql.md` |
| A request value rendered by a template engine | Template injection | one arithmetic marker | `../web-ssti/` |
| A shell or evaluation call taking request data | Command execution | one benign command separator | `../ctf-web/server-side-exec.md` |
| A deserializer called on a cookie, parameter or uploaded model | Deserialization | identify the format before any gadget | `../web-deserialization/` |
| An XML parser with external entities enabled | XXE | one entity referencing a known-readable file | `../ctf-web/server-side-2.md` |
| The server fetches a request-controlled URL; a bot or renderer visits one | SSRF | one controlled address, then compare with an internal one | `../web-ssrf/` |
| A file read built from a request value | File read to source disclosure | absolute path first, traversal second | `../file-read-primitives/` |
| A token whose algorithm or key comes from the token, or a leaked signing key | Auth and session | decode and inspect before modifying anything | `../web-auth-session/` |
| A deep merge or assignment over request JSON; `__proto__` accepted | Prototype or class pollution | pollute one harmless property, then read it back | `../ctf-web/node-and-prototype.md` |
| An upload whose extension, type or content check is weak | File upload | benign marker file first; find where it is served | `../web-file-upload/` |
| An object id in a path, body or token with no ownership check | IDOR | one adjacent id from a second identity | `../web-idor/` |
| Check-then-act on a balance, coupon, token or one-time action | Race condition | two interleaved requests, not a flood | `../ctf-web/server-side-deser.md` |
| A registration, verification or reset flow; mass assignment | Auth or logic bypass | one extra field, or skip one step | `../web-auth-session/` |
| A value reflected into HTML, an attribute, JavaScript or the DOM, with a viewer | XSS | one unique harmless marker; identify the context | `../web-xss/` |
| A custom proxy, gateway or WAF in front of the app | Parser differential | compare how proxy and backend parse the same bytes | `references/http-parser-differential.md` |

## Probe rules

- One class, cheapest probe first. Read the result and ask: is there a new
  signal?
- No new signal after the class budget: the class is probably wrong. Return to
  this table and change layer — do not try another variant. See
  `../LOOP_DISCIPLINE.md`.
- If the bug cannot reach the flag, it is not this challenge's bug.
- Before any write on a shared instance, understand the write semantics on an
  object you created.

## Pulling a specific variant

When the class is right but a particular filter bypass is needed, open one named
file under `../ctf-web/`, not the directory:

```bash
grep -ril "<keyword>" ~/ctf/skills/ctf-web/ | head
```

## Extended maps

- `references/signal-to-skill-map.md` — response, header and behavioural signals
- `references/triage-checklist.md` — the ordered first pass
- `references/http-parser-differential.md` — proxy versus backend parsing
- `references/laravel-session-cookie-sqli.md` — leaked key to session forgery to
  a query fragment
