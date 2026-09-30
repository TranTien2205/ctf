---
argument-hint: "[handout-dir] [challenge-name] [base-url]"
---

Close a layered white-box handout in parallel, not one layer at a time: $ARGUMENTS

```bash
python3 tools/subagent_fanout.py --brief <handout> --challenge <name> --target <base-url>
```

Read `already_measured_dead_elsewhere` on every brief **before** launching
anything. A layer a previous attempt already closed does not get a subagent; read
its `measurement` and its `reopen_if` and spend the budget on a layer nobody has
touched.

Then launch one `ctf-layer-prober` per remaining layer, in parallel, one brief
each. Each returns the JSON from `python3 tools/subagent_fanout.py --contract`.

Nothing a subagent says counts until it passes the validator:

```bash
python3 tools/subagent_fanout.py --validate report.json
python3 tools/subagent_fanout.py --merge reports/*.json --challenge <name>
```

`--merge` prints `hooks.py post-probe` commands for **you** to run — it never
writes `state.json`, and the probers cannot. Run them, then `tools/decide.py`
names the next action.

Two things this enforces that prose cannot:

- evidence must be a **verbatim substring** of the response excerpt in the same
  report; a summary is refused
- a write-shaped probe never comes from a subagent; it comes back to you, and you
  read the chain card's `blast_radius` before passing `--write-ack`

A layer whose falsifier **held** belongs in `knowledge/attempts/<challenge>.json`
with its measurement, or the next attempt walks it again.

If `chain_match.py` returned a candidate, do not sweep — run that card's
`first_confirming_probe` first. See `skills/parallel-layer-sweep/SKILL.md`.
