# tools/web/http_probe.py — the sanctioned request+response

The one component that holds request and response together and emits the post-probe command with --response already filled — use it for disclosure probes so evidence is paste-free.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url required, --challenge required | hooks integration | evidence-ready |
| --emit runs pre-probe+post-probe | verified loop | post-probe quoted |
| --header/--body/--method | request shaping | as needed |
| --body-chars bounds the excerpt | response size | for big bodies |

## Steps

1. python3 tools/web/http_probe.py --url <u> --challenge <ch> --class web-info-disclosure --hypothesis-id <id>.
2. Read the emitted response excerpt — the same text post-probe records.
3. Use --emit to run the hooks loop when the probe produces class evidence.
4. For disclosure 'hits', the response IS the evidence — verbatim.

## Falsifier

Falsifier — the response is the catch-all body: no disclosure, record the negative.

## Traps

- --emit writes state — only when the probe is real (not a rehearsal).
- --class must match the hypothesis bug_class or the hook refuses.

## Commands

```bash
python3 tools/web/http_probe.py --url '$BASE/.git/HEAD' --challenge ch --class web-info-disclosure --hypothesis-id h1 --emit
```

## Cross-references

`evidence.md` · `bounded-sweep.md`
