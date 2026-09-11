# CTF Toolkit

This is an independent toolkit for CTF jeopardy and attack-defense challenges.
It does not import or read the red-team machine toolkit under
`~/security-toolkit`.

## Fast entry point

```bash
python3 ~/ctf/ctf.py ./challenge-src       # whitebox
python3 ~/ctf/ctf.py "JWT login admin bot"  # blackbox
python3 ~/ctf/ctf.py --web "Challenge Event" # public writeups
```

For a new session, load [PROMPT.md](PROMPT.md) and use
[SKILL_GUIDE.md](SKILL_GUIDE.md). Run the offline update gate from
`test/README.md` before accepting changes.

The observation router returns one primary category and a local skill path
(a thin router where available). Source scanning returns heuristic findings,
not a category verdict or proof of exploitability. Do not open all
skills: open the selected router, run its cheapest probe, and only then load a
depth reference.

## Layout

- `ctf.py`: independent fast router
- `skills/`: CTF-only skill library
- `challenges/`: local challenge inputs and artifacts
- `solved/`: verified solutions and notes
- `cache/`: disposable web/search cache
- `tools/`: CTF helper tools only
- `test/`: offline regression checks for routing, source contracts, state, and skill paths

Flags are hypotheses until verified from the challenge target or supplied
artifact. This toolkit is for authorized CTF/lab use.

## Foundation Tools

- `tools/plan.py`: offline `first-probe-plan` suggestions, ranked by keyword evidence, at most three. Uses canonical first-probe registry keys where available; fallback probes remain generic.
- `tools/query_index.py`: literal-token FTS search, not a raw FTS expression interface. Missing/broken indexes report errors without creating a database; router retrieval degrades to an empty list.
- `tools/state.py`: safe challenge IDs, atomic state replacement, explicit hypothesis selection. Existing fields are retained and legacy hypotheses acquire IDs on a successful update. Invalid JSON/structure is never reset automatically. This is a single-writer tool; simultaneous updates can lose changes.
- `tools/validate_card.py`: requires `jsonschema` (tested with 4.19.2), validates the local Draft 2020-12 schema with URI formats and evidence/secret checks. Missing dependency fails closed. Validation does not verify source truth or strengthen constraints absent from the schema.
- `tools/promote_card.py`: requires critic acceptance and validation; destinations must resolve inside this toolkit. Publishes atomically without overwriting existing names. Critic acceptance is supplied input, not independent proof.
- `tools/web_probe.py`: retains HTTP error status, headers, final URL, and the same bounded body-derived observations as successful responses. It does not retain raw response bodies; transport failures remain errors.

State example (use the hypothesis ID returned by the first command):

```bash
python3 tools/state.py example --hypothesis "input reaches template"
python3 tools/state.py example --hypothesis-id <id> --probe "baseline" --result "no difference"
python3 tools/state.py example --hypothesis-id <id> --close "falsified"
```

IDs are 1-100 ASCII characters, starting alphanumeric, followed by letters,
digits, dots, underscores or hyphens; uppercase folds to lowercase as before.
Names are no longer silently sanitized or truncated. For previously sanitized
names, use the existing directory ID explicitly. No existing state is migrated
until explicitly updated.

## Command Logging

```bash
python3 tools/run.py --timeout 5 --cwd /home/kali/ctf example -- python3 -c 'print("baseline")'
```

Options go before the challenge ID. This records explicit argv, cwd, timestamps,
exit code, timeout status, and binary stdout/stderr artifacts under
`challenges/<id>/runs/<run-id>/`. A timeout kills the launched process group.
Execution uses no shell interpolation. It is not a sandbox: commands can access
files/network or spawn detached processes. Output files have no size quota,
and external interruption can leave a `running` record. It does not select
commands, automatically link hypotheses, discover extra artifacts, or verify flags.
Only run commands you have inspected and authorized.

## Offline Checks

```bash
python3 -m unittest discover -s tests -v
python3 selfcheck.py
python3 tools/evaluate.py
```

Tests use temporary fixtures inside this toolkit and mocked HTTP responses.
Only controlled Python snippets are executed, never challenge artifacts.
The golden evaluator is a small routing smoke test, not a solving benchmark.
There is no autonomous solving agent or automatic flag submission here. The
operator must execute probes and verify the flag from a real response or
artifact.
