# Learning Loop — how a skill gets better

A skill library does not improve by growing. It improves when each verified solve
lands in the one skill that will be opened next time the same shape appears, and
when nothing lands there unreviewed.

That is this loop. Four steps, one of which is a human.

```
solve + verified flag
   -> chain card            knowledge/chains/<id>.json
   -> classify              tools/classify_solve.py --chain <id>
   -> field note            skills/<class>/field-notes.md   [proposed]
   -> review                tools/classify_solve.py --confirm <class> <anchor>
   -> field note            skills/<class>/field-notes.md   [confirmed]
```

## 1. The flag is verified, so write the chain card

Nothing enters the loop before the flag is read from a live response or a
supplied artifact. Write the card into `knowledge/chains/` following
`knowledge/chain-schema.json` — preconditions, literal signals, the chain, the
first confirming probe, the blast radius, the traps that cost time.

The traps are the most valuable field. They are what you will have forgotten.

Write it by hand. `tools/chains_from_solved.py` exists and generated the ten
cards that are here now, but it reads the prose in `solved/` and is only as good
as that prose; it is a bulk backfill tool for notes written before the card
format existed, not a step in this loop. Validate whichever way the card was
produced:

```bash
python3 tools/validate_card.py knowledge/chains/<id>.json
```

## 2. Classify the solve

```bash
python3 tools/classify_solve.py --chain <chain-card-id>
```

The tool classifies from the card's own signals and its solved note, then writes
a `proposed` entry into the matching class's `field-notes.md`. Every line it
writes is copied from the card — it does not summarise or infer.

**When the evidence does not decide**, the tool refuses and lists the tied
classes. That is deliberate: a solve filed under the wrong skill is worse than
one not filed at all, because the next challenge of that shape will open the
wrong door. Decide from the card and re-run with `--into <class>`.

The rule of thumb: the field note belongs to the class whose **first probe opens
the chain**, not the class of the final payload. A chain that starts with a
traversal and ends in blind SQL injection is filed under file read; that is the
door you had to find.

## 3. Review, then confirm

```bash
python3 tools/classify_solve.py --review
python3 tools/classify_solve.py --confirm <class> <anchor>
```

Review means checking the entry against the card: is the class right, is the
probe stated as it actually ran, is the trap real. Nothing is confirmed by
default and nothing expires into confirmed on its own.

Delete an entry that did not hold up and say why in the commit message. An
unreviewed pile is the failure mode — `test/capability_report.py` reports the
proposed-to-confirmed ratio so the pile is visible.

## 4. Raise the class when it has earned it

`knowledge/bug-classes.json` marks every class `verified` or `catalogue`:

| Level | Meaning |
|---|---|
| `verified` | a chain card in this repository proves the class was solved here |
| `catalogue` | a real, standard class that nothing here has solved yet |

A catalogue class whose first verified solve arrives is proposed for promotion by
`classify_solve.py`, but never promoted automatically. Edit
`build/make_bug_classes.py`, add the chain id to `verified_by`, set
`evidence_level` to `verified`, regenerate, and run the gate:

```bash
python3 build/make_bug_classes.py
python3 build/make_registry.py
bash test/run_all.sh
```

The distinction is not bookkeeping. A catalogue skill says plainly that its
content is standard knowledge rather than local experience, and an agent reading
it should weigh it accordingly. Promoting one without a chain card would put a
claim of experience behind text nobody earned.

## When nothing matches

`tools/classify.py` appends every unclassified input to
`knowledge/classify-misses.log`. That log is the backlog: each line is a shape
the taxonomy cannot name yet.

Close a gap by adding a class to `build/make_bug_classes.py` with its signals,
first probe and falsifier, regenerating, and writing its skill. A shrinking miss
log with a growing verified count is what improvement actually looks like.

## What the gate enforces

- every class in the taxonomy has a skill directory that exists
- every skill directory has a `field-notes.md`
- every field-note entry is `proposed` or `confirmed` and nothing else
- a `verified` class names at least one chain card that exists
- a `catalogue` class names none
- the classifier still routes every shape in `test/cases/classify.json` correctly
- the benign fixture still matches no class at all

That last one matters most. The cheapest way to make a classifier look good is to
widen its signals until everything matches something. The benign fixture is there
so that move fails the gate.
