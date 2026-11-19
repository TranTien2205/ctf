# Lead triage — ranking the mined output

## The triage order

`bundle_miner` and the greps produce a mixed lead list. Rank by
exploit value:

```
1. a live secret/credential          -> web-auth-session  (immediate reach)
2. a hidden endpoint with a param    -> its class          (idor/sqli/ssrf/...)
3. a feature flag / admin route      -> web-logic-flaw     (a gate to test)
4. an internal host/URL              -> web-ssrf           (a reach target)
5. a recovered-source sink           -> the sink's class   (the vuln itself)
6. a flag-shaped string              -> pre-flag           (maybe the flag)
7. a route that is client-only       -> dead               (a recorded negative)
8. a publishable config / public ep  -> dead               (a recorded negative)
```

## The value signals

| Signal | Raises |
|---|---|
| the lead is *hidden* — no UI link reaches it | high |
| the lead carries a *param* — `?id=`, `/:id` | high (injection/IDOR) |
| the lead is a *verb* endpoint — `/admin/export`, `/internal/dump` | high |
| the lead is a *credential* | highest |
| the lead is behind a *flag/gate* | high |
| the lead is a *publishable* `pk_`/`NEXT_PUBLIC_` | low |
| the lead is a *client-only* route | low (dead) |
| the lead is `node_modules`/vendor | low |

## The per-lead record

Each lead gets: `string, source_file, class_route, verify_result`. The
triage is a sorting of the lead list, not a claim — the verify pass
decides which leads are real.

## The "one hidden endpoint" outcome

The most common valuable result: ONE endpoint the UI hides —
`/api/admin`, `/internal/export`, `/debug`. The whole map pass is
justified by a single hidden endpoint that verifies. Route it to its
class and work it there.

## The "no lead survives" outcome

A mined bundle whose leads all fail verify is a clean depth-4 negative —
record it and move. The triage still produced a result: the surface is
measured as public-only.

## The dedup rule

The same endpoint found in `main` and a chunk is one lead — dedupe on
the endpoint string, keep the first source file. A param template
(`/:id`) and its instances dedupe to the template.
