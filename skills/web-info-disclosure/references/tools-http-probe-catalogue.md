# tools/web/http_probe.py — the sanctioned request+response — case catalogue

The one component that holds request and response together and emits the post-probe command with --response already filled — use it for disclosure probes so evidence is paste-free.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | --url required, --challenge required | hooks integration | evidence-ready |
| 2 | --emit runs pre-probe+post-probe | verified loop | post-probe quoted |
| 3 | --header/--body/--method | request shaping | as needed |
| 4 | --body-chars bounds the excerpt | response size | for big bodies |

## Falsifier

Falsifier — the response is the catch-all body: no disclosure, record the negative.

## Coverage notes

- --emit writes state — only when the probe is real (not a rehearsal).
- --class must match the hypothesis bug_class or the hook refuses.

## Cross-references

`evidence.md` · `bounded-sweep.md`
