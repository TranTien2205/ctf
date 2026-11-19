# Field manual (deep) — the complete operator guide

## The mission

The front-end is shipped source — read it. The bundle names every
endpoint, param, route, flag, and sometimes a secret or the flag; the
`.map` recovers the original commented source. The goal is the *real
attack surface*, enumerated from the client's own code.

## The operator sequence

```
S1  inventory     every script + the manifest (the bundle set)
S2  map           probe every map route per bundle
S3  mine          bundle_miner / targeted grep
S4  triage        rank the leads
S5  verify        each lead live
S6  route         each verified lead to its class
S7  record        each lead + each dead end
```

## The one-command path

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
```

S1-S3 in one tool. `-H "Cookie: $C"` for auth; `--show-secrets` for the
candidates; `--context`/`--lookahead` for the evidence.

## The per-stage decision table

| Stage | Decision | Path |
|---|---|---|
| S2 | map found + sourcesContent | read recovered source for sinks/keys |
| S2 | map found, no content | file names only — structure leads |
| S2 | no map | string mine every bundle |
| S5 | endpoint live | route to its class |
| S5 | endpoint 404/catch-all | dead — record |
| S5 | secret verifies | web-auth-session |
| S5 | secret dead/publishable | dead — record |
| S5 | flag server-enforced | dead — record |
| S5 | flag client-only | a find — route to logic |
| S5 | flag-shape | pre-flag gate |

## The tool-vs-hand rule

`bundle_miner` for the inventory (it crawls, guesses maps, reconstructs,
inventories); hand-grep for a token it missed or a `--file`/`--map`
already on disk. Do not re-derive the endpoint inventory by hand.

## The budget rule

The map pass is bounded recon — one entry fetch, one `bundle_miner`,
targeted greps, one verify pass. The exploit is the routed class, not
more mining. Stop when every lead is verified-or-dead.

## The record rule

Every lead: source file + verbatim string + live result. Every dead
end: the same + the falsifier that fired. A lead without provenance is
not traceable; a dead end without the falsifier is not recorded.

## The honesty rule

The map is recon, not the exploit. A bundle string is a claim; the
live check is the finding. Catalogue class — no local verified solve.
