---
argument-hint: "[observation text, or --source <path>]"
---

Classify this evidence into a bug class and check whether the shape was already
solved here. Evidence: $ARGUMENTS

```bash
python3 tools/classify.py $ARGUMENTS
python3 tools/chain_match.py $ARGUMENTS        # add --record <id> once a ledger exists
python3 tools/skill_select.py $ARGUMENTS
```

Read the output as candidates, never as findings. For each candidate report:

- the class, and whether its evidence level is `verified` (a chain card in this
  tree proves it was solved here) or `catalogue` (published knowledge, nothing
  here has solved it — never present it as local experience)
- the `first_probe` to run
- the `falsifier` that would close the class
- for a chain match, the card's `first_confirming_probe`, `known_traps` and
  `blast_radius`

If `classify.py` returns no candidate, say so plainly. It does not guess, and an
empty result for a non-web challenge is expected: the bug-class taxonomy covers
web only. Use the router `skill_select.py` names instead.
