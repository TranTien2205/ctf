# tools/web/http_probe.py — the sanctioned request+response — operational checklist

The one component that holds request and response together and emits the post-probe command with --response already filled — use it for disclosure probes so evidence is paste-free.

## Checklist

- [ ] python3 tools/web/http_probe.py --url <u> --challenge <ch> --class web-info-disclosure --hypothesis-id <id>.
- [ ] Read the emitted response excerpt — the same text post-probe records.
- [ ] Use --emit to run the hooks loop when the probe produces class evidence.
- [ ] For disclosure 'hits', the response IS the evidence — verbatim.

## Abort conditions

- --emit writes state — only when the probe is real (not a rehearsal).
- --class must match the hypothesis bug_class or the hook refuses.

## Falsifier

Falsifier — the response is the catch-all body: no disclosure, record the negative.

## Cross-references

`evidence.md` · `bounded-sweep.md`
