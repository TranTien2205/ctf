# Field manual — the operator sequence

## The five-step pass

```
1. INVENTORY  — every <script src> + the manifest's route list
2. MAP        — probe every .map sibling + the sourceMappingURL tail
3. MINE       — bundle_miner --url --out; or grep the bundles
4. VERIFY     — each endpoint live, each secret authenticates
5. ROUTE      — each verified lead to its class; dead leads recorded
```

## The one command

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
```

It does steps 1-3: crawls the scripts, guesses the maps, reconstructs
`sourcesContent`, inventories endpoints + routes + flags + secrets.

## The decision after

- recovered source → read it for sinks, keys, the flag
- endpoint strings → probe each live
- secret candidates → `--show-secrets`, verify each
- a flag shape → `pre-flag`
- nothing → record the negative, next recon layer

## The tool-vs-hand decision

`bundle_miner` first; hand-grep for a token it missed, or when feeding
a specific `--file`/`--map`. Do not re-derive the endpoint inventory by
hand when the tool emits it.

## The budget rule

The map pass is bounded recon — one entry fetch, one `bundle_miner`,
targeted greps. The exploit is the routed class, not more mining. Stop
when every lead is verified-or-dead.

## The record rule

Every lead: source file + verbatim string + live result. A lead without
its source file is not traceable. Dead leads are negatives.
