# tools/web/id_sweep.py — existence oracle over ids — operational checklist

Enumerates ids through a request template — for disclosure, useful when sequential ids expose other objects' data (which is also the web-idor boundary).

## Checklist

- [ ] Identify the id-bearing endpoint and its valid range.
- [ ] python3 tools/web/id_sweep.py --url 'https://t/obj/{id}' --range 1-200 --rate 10.
- [ ] Each 200-with-content is an exposed object — the disclosure.
- [ ] --no-follow when a 302 is the oracle (auth-gated content often redirects).

## Abort conditions

- Sequential-id disclosure is web-idor's class when ownership matters — the tool is shared, the class differs.
- --stop-on-flag for flag-shaped responses.
- Respect --rate: shared infra, unbounded sweeps kill the instance.

## Falsifier

Falsifier — ids return uniform 404/catch-all: no enumerable surface.

## Cross-references

`bounded-sweep.md` · `../web-idor/`
