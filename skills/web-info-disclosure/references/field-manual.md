# Field manual — one page per move

## The five-minute pass

1. `curl -sI $BASE/` — read every header.
2. `curl -s $BASE/zz-no-such-9x` — the catch-all baseline, saved.
3. The bounded path list — read bodies, diff against baseline.
4. `robots.txt` + `sitemap.xml` — collect Disallow + URLs.
5. Framework fingerprint → the matching debug-path list.

## The tools

| Job | Tool |
|---|---|
| Walk a served .git | `python3 tools/web/git_dumper.py --base <u>/.git/ --out repo` |
| Recover + mine bundles | `python3 tools/web/bundle_miner.py --url <page> --out mined/` |
| Probe with evidence shape | `python3 tools/web/http_probe.py --url <u> --challenge <c> --class web-info-disclosure` |
| Walk a file-read primitive | `python3 tools/web/read_loop.py --url '<u>/{path}' --profile secrets` |
| Enumerate sequential ids | `python3 tools/web/id_sweep.py --url '<u>/{id}' --range <a-b>` |
| Pinned-dep recall | `python3 tools/gadget_lookup.py --lockfile <lockfile>` |

## The evidence rule

The artifact itself, verbatim in `--evidence`, its source response in
`--response`. A catch-all 200 is not evidence. A found secret is used in the
chain, redacted in notes, never committed.

## The exits

- Every channel falsifier fires → record the negative list, done.
- A find chains to impact → continue in the owning class.
- Flag in a response → `pre-flag --value` on the bytes.
