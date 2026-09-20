---
argument-hint: "[what changed, one line]"
---

Run the update gate before accepting any change to this system. Change: $ARGUMENTS

```bash
bash test/run_all.sh
```

Required steps must all pass: the regression suite, `selfcheck.py`, the routing
evaluator, the scope-boundary guard and the capability snapshot. The optional
foundation suite reports SKIPPED when `jsonschema` and `tornado` are absent, and
that is not a failure.

If the last line is not `PASS`, do not commit. Report which step failed and its
exact output.

On PASS, and only then:

```bash
python3 tools/skill_audit.py | grep -E '^\[(warn|review)\]'   # expect no output
bash scripts/save_version.sh "$ARGUMENTS"
```

Never lower `test/baseline.json` to make the gate pass. It is a capability floor,
and `capability_report.py --write` refuses to lower it for the same reason.
