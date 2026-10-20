# Field notes — reverse engineering

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

**This file is empty on purpose.** The taxonomy classes that route here are all
`catalogue`: the measured count of chain cards in this category is zero. An empty
field-notes file is the honest state, not a gap to fill with published knowledge.

---
