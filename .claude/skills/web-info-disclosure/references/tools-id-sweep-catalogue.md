# tools/web/id_sweep.py — existence oracle over ids — case catalogue

Enumerates ids through a request template — for disclosure, useful when sequential ids expose other objects' data (which is also the web-idor boundary).

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | --url contains {id} or {ids} | the sweep template | sequential or list |
| 2 | --range LOW-HIGH[:STEP] | numeric sweep | bounded |
| 3 | --rate/--retries | politeness + resilience | sized to target |
| 4 | --no-follow keeps the 302 oracle | redirect evidence | when 302 is the signal |

## Falsifier

Falsifier — ids return uniform 404/catch-all: no enumerable surface.

## Coverage notes

- Sequential-id disclosure is web-idor's class when ownership matters — the tool is shared, the class differs.
- --stop-on-flag for flag-shaped responses.
- Respect --rate: shared infra, unbounded sweeps kill the instance.

## Cross-references

`bounded-sweep.md` · `../web-idor/`
