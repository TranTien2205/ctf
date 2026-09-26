---
argument-hint: "[challenge-name] [target-url-or-source-path]"
---

Start work on a CTF challenge in this tree. Arguments: $ARGUMENTS

Do this in order, and do not skip to a payload:

1. Verify the tree is intact:
   ```bash
   python3 selfcheck.py
   ```
   Fix any FAIL before going further.

2. Read `AGENTS.md` if it is not already in context. It is the contract: the
   proof standard, the control loop, and the rule against rebuilding what
   already exists.

3. Open the challenge in the ledger, using the name and target from the
   arguments:
   ```bash
   python3 tools/state.py <name> --category <cat> --target <url>
   ```

4. Branch on what the challenge supplies:
   - source code available -> `python3 tools/classify.py --source <dir>`
   - black box only        -> `python3 tools/classify.py "<observation>"`
   Then, either way:
   ```bash
   python3 tools/chain_match.py "<observation>" --record <id>   # or --source <dir>
   python3 tools/skill_select.py "<observation>"  # which skill to open
   ```

5. Open exactly one router and at most one depth skill, as `skill_select.py`
   names them. Never browse the skills directory.

Report the bug class, the first probe and the falsifier before running anything
against the target.
