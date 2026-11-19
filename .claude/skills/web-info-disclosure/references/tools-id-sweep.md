# tools/web/id_sweep.py — existence oracle over ids

Enumerates ids through a request template — for disclosure, useful when sequential ids expose other objects' data (which is also the web-idor boundary).

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url contains {id} or {ids} | the sweep template | sequential or list |
| --range LOW-HIGH[:STEP] | numeric sweep | bounded |
| --rate/--retries | politeness + resilience | sized to target |
| --no-follow keeps the 302 oracle | redirect evidence | when 302 is the signal |

## Steps

1. Identify the id-bearing endpoint and its valid range.
2. python3 tools/web/id_sweep.py --url 'https://t/obj/{id}' --range 1-200 --rate 10.
3. Each 200-with-content is an exposed object — the disclosure.
4. --no-follow when a 302 is the oracle (auth-gated content often redirects).

## Falsifier

Falsifier — ids return uniform 404/catch-all: no enumerable surface.

## Traps

- Sequential-id disclosure is web-idor's class when ownership matters — the tool is shared, the class differs.
- --stop-on-flag for flag-shaped responses.
- Respect --rate: shared infra, unbounded sweeps kill the instance.

## Commands

```bash
python3 tools/web/id_sweep.py --url 'https://t/doc/{id}' --range 1-500 --rate 5
python3 tools/web/id_sweep.py --url 'https://t/doc/{id}' --no-follow
```

## Cross-references

`bounded-sweep.md` · `../web-idor/`
