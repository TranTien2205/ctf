# Triage - first pass over an unknown web target

The job of the first pass is not to exploit. It is to name the two or three
most promising hypotheses with the cheapest discriminating test for each.

## Order of operations

1. `fingerprint(url)` - stack from headers, cookie flags, missing security
   headers, robots.txt paths (robots disallow lists are free endpoint intel).
2. `crawl(url, depth=2)` - pages, forms, query params. Forms and parameters
   are the attack surface; static pages are not.
3. `js_recon(url)` - endpoints the front-end actually calls, plus secret
   candidates. For SPAs this beats every wordlist.

## What to record as surface

- Every parameter (query, form field, JSON key, path segment, header the app reads)
- Every object identifier (numeric id, uuid, slug, filename, token)
- Every state-changing endpoint (POST/PUT/DELETE) and its auth requirement
- The auth model: cookie, bearer, JWT, basic; how it is issued and checked
- Anything reflected: search terms, error messages, profile fields

## Prioritization heuristic

Test in this rough order unless evidence says otherwise:

1. Auth surface - login, register, reset, OAuth callbacks (logic bugs pay most)
2. Parameters that look like they reach a query or file - `id`, `q`, `file`,
   `path`, `url`, `next`, `template`, `sort`, `filter`
3. Reflected values - XSS first, SSTI if a template engine is suspected
4. Object ids with a second identity - IDOR
5. Anything the server fetches - SSRF
6. Endpoints that parse structured input - XML/XXE, GraphQL, deserialization

## Discipline

- One hypothesis -> one probe -> read -> update. Never batch blind.
- A status-200 response is not signal. A *difference* between two responses is.
- Park dead ends in note() with the evidence that killed them, so a later
  turn does not re-walk them.
- Budget: if the surface is large, test the top 5 inputs properly rather
  than 20 inputs shallowly.
