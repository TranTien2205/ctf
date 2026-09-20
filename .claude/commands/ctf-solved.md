---
argument-hint: "[challenge-name] [flag]"
---

Close the learning loop after a verified flag: $ARGUMENTS

The flag counts only if it was read from a live response or a supplied artifact.
Run every step; the loop is what makes the bug-class skills better over time.

```bash
# 1. the flag enters state only through the gate
python3 tools/hooks.py pre-flag <challenge> --value '<flag>' \
        --source live-response --evidence '<verbatim excerpt>'

# 2. the controller must now return record_solve
python3 tools/decide.py <challenge>
```

3. Write `knowledge/chains/<id>.json` by hand, following
   `knowledge/chain-schema.json`. The `known_traps` field is the most valuable
   one — it is what you will have forgotten next time. No flag goes in the card.

```bash
python3 tools/validate_card.py knowledge/chains/<id>.json

# 4. file the solve into the right bug-class skill
python3 tools/classify_solve.py --chain <id>

# 5. review the proposed note, then confirm it
python3 tools/classify_solve.py --review
python3 tools/classify_solve.py --confirm <class> <anchor>

# 6. the gate must pass before this counts as done
bash test/run_all.sh
```

Filing rule: the note belongs to the class whose **first probe opened the
chain**, not the class of the final payload. If the evidence does not decide
between two classes, `classify_solve.py` refuses to file — that is correct, so
decide from the chain card yourself and re-run with `--into <class>`.
