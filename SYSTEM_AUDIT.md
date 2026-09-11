# CTF System Audit

## Current strengths

- Supports both black-box observation routing and white-box source scanning.
- Uses a bounded first-probe planner instead of loading every reference.
- Stores compact related cards in SQLite and keeps raw/normalized writeup
  provenance separate from the router.
- Validates cards, rejects unsafe destinations, writes state atomically, and
  records command output with timeouts.
- Has a useful solved-chain corpus, including the verified Weather App chain.
- Has offline foundation tests and now has a dedicated regression suite under
  `test/`.

## Current weaknesses

- Routing remains heuristic: keyword scores are not exploitability proof and
  generic terms can outrank a more specific signal.
- The planner was previously missing explicit routes for some categories and
  depended on skill paths that did not exist. The missing web-SSRF and binary
  triage paths are now restored and checked.
- Hypothesis state previously had no priority or explicit deprioritization;
  an operator could close a useful branch instead of parking it. Priority 0
  now preserves an open branch.
- The benchmark is a narrow local Tornado fixture and is not a representative
  black-box, white-box, or exploit-chain benchmark.
- The system is operator-guided. It does not autonomously execute a full
  attack loop, verify every claim, or submit flags.
- Knowledge-card validation checks schema and supplied evidence spans, but it
  cannot independently prove that a writeup is truthful.
- `gh` and GitHub credentials are unavailable in this environment, so remote
  private-repository creation cannot be completed automatically yet.

## Recommended architecture

Keep the system layered: one router, one selected depth skill, compact
evidence-backed cards, and a state file that preserves competing hypotheses.
Import external bundles selectively. `Claude-BugHunter` is valuable for web
patterns, evidence hygiene, and methodology, but its declared scope is
external bug hunting and it excludes much of CTF pwn/reverse/forensics. A full
copy would increase skill dilution and licensing/maintenance burden.

## External sources

- `elementalsouls/Claude-BugHunter`: reviewed 2026-09-11 from its public README.
  It advertises 83 skills, 15 commands, and 681 disclosed-report patterns;
  treat those numbers as repository claims, not local coverage.
- `ctfs/writeups`, CTFtime, PortSwigger, and selected technical blogs are
  already supported by the crawl prompts. Pin revisions, preserve URLs and
  hashes, and reject unsupported metadata.

## Update gate

Before accepting a system update, run:

```bash
python3 ~/ctf/test/regression.py
python3 -m unittest discover -s ~/ctf/tests -v
python3 ~/ctf/selfcheck.py
```

Then inspect `git diff` and create a version tag. Never store live target
tokens, credentials, or private flags in a public repository.
