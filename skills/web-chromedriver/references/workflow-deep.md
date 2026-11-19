# Workflow deep — the run, step by step with decision points

## Phase 1: classify (minutes 0–5)

```
supplied source? --yes--> grep driver/bot -> which use?
bot flow?        --yes--> debugging aid
POST /session?   --yes--> attack surface
neither?         --no-->  class dead, record
```

**Decision point**: attack surface is tested first (cheaper read) —
one `POST /session` answers it.

## Phase 2a: attack surface (minutes 5–45)

```
sessionId? --yes--> file read? JS? loopback? cookies?
         \--no--> capability negotiation -> legacy protocol -> dead
```

- `file:///etc/passwd` + `source` -> the file-read check
- `execute return 1+1` -> the JS check
- `localhost/admin` + `source` -> the loopback check
- `GET /cookies` -> the jar check

**Decision point**: map the flag's surface (file/route/cookie/DOM/
render), then read through the matching live primitive.

## Phase 2b: debugging aid (minutes 5–50)

```
bot source? --yes--> copy URL/cookie/wait/flags verbatim
         \--no--> observe + record assumptions
-> local driver, same flags/version -> same cookie/URL/wait
-> verify page matches live -> reproduction confirmed
```

**Decision point**: the reproduction must match on the behaviour
axes — a divergence invalidates every later test.

## Phase 3: payload development (debugging aid)

```
four hooks on -> canary -> read the channels -> iterate -> confirm
-> channel check (tunnel reachable from inside) -> full payload fires
```

- canary: `console.log` / a marker fetch -> proves execution
- staged markers: `S1/S2/S3` -> locates the dead stage
- the four channels: console/error/DOM/network

**Decision point**: a payload confirmed locally is ready for the live
fire — only then spend a bot visit.

## Phase 4: fire and confirm

```
debugging aid: fire live once -> listener carries flag-shape -> pre-flag
attack surface: the source/execute/cookies/screenshot carries it -> pre-flag
```

**Decision point**: a candidate is not a flag until `pre-flag` gates it.

## Phase 5: close

```
DELETE every session -> kill local driver processes
-> record working payload + channel in notes
-> record dead ends in kill map with re-open conditions
```

## The escalation rungs (stalled)

| Stall | Rung |
|---|---|
| reproduction won't match | re-derive properties; bot version |
| payload won't fire locally | the context -> `../web-xss/` |
| channel dead | alternate channel -> `evasion.md` |
| read blocked | `execute`/`localhost`/CDP alternate |
| "bot" isn't a browser | `../web-ssrf/` |
| mechanism layer spent | `tools/decide.py` -> escalate |

The workflow's property: each phase has a decision point, and a
stall routes to a rung rather than a sixth variant.
