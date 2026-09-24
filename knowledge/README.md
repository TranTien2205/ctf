
Pilot command:

```bash
python3 tools/github_pilot.py --limit 30
```

The pilot pins the repository to a commit, selects Markdown files under web
challenge paths, and delegates fetching to `tools/crawl.py`. It never clones
the complete repository or executes downloaded code.

`python3 tools/queue_extract.py` scores what was fetched and produces the
extraction queue: which pages carry evidence worth turning into a card, in what
order. Nothing in the queue becomes a card without a human reading it first.

## Two stores, and the line between them

| | `chains/` | `cards/` |
|---|---|---|
| where it came from | solved on this machine | someone else's writeup |
| schema | `chain-schema.json` | `schema.json` |
| read by `chain_match.py` | yes | **no** |
| may make a class `verified` | yes | **never** |
| `quality.verified_live` | n/a | must be `false` |

A writeup card is **hearsay**. It records a technique someone else reported, with
its provenance, so `classify.py` can recognise a shape and a human can go read
the original. It is never evidence that anything works here. The only route from
`cards/` to `chains/` is solving the challenge on this machine and writing the
chain card from that run.

### What to keep when filtering a writeup

Keep the parts that make a probe possible, drop the narration:

- `signals` — literals that actually appear in the target's source or responses,
  specific enough to identify the mechanism. The same rule as a chain card:
  `tools/validate_card.py` rejects a card that cannot be told apart without
  signals common to half the known handouts. `api`, `bot`, `config` are noise;
  `hash_data(req.http.` is a signal.
- `first_probe` — the cheapest request that distinguishes this from its
  neighbours, and what answer would rule it out.
- `pitfalls` — what the author says cost them time. This is the scarcest part of
  any writeup, because most are written after the fact with the dead ends
  removed.
- `source.url` and `source.author` — so a claim can be traced back.

Drop the walkthrough prose, the screenshots and the tool transcripts. A writeup
that yields nothing but prose yields no card.

### Why the separation is enforced and not just documented

`chain_match.py` ranks by how rare a signal is, so every extra card competes for
the top slot. Cards that were never verified here would dilute that ranking with
claims nobody checked, and the `verified` label in `bug-classes.json` would stop
meaning "this toolkit has done it". `test/regression.py` holds the boundary.

