# System Audit — 2026-09-11

Audit of `~/ctf` as found, the changes made in response, and what is still open.
Every claim below is tied to a file that was read or a command that was run.

## Strengths as found

- **Both modes already worked.** `ctf.py` has a white-box source scanner
  (`source_route`) and a black-box observation router (`observation_route`),
  offline and fast. The source scanner finds flag literals and sink candidates in
  one pass.
- **A scope boundary was declared and held.** `DESIGN.md` states that this tree
  does not import `~/security-toolkit`, and `ctf.py` imports nothing from it.
- **An evidence discipline already existed.** `EVIDENCE_POLICY.md`, the card
  schema, `tools/validate_card.py` and `tools/promote_card.py` form a real
  anti-fabrication chain: a card needs schema validation and critic acceptance
  before promotion, and `promote_card.py` refuses destinations outside the tree.
- **The ledger was sound.** `tools/state.py` writes atomically, gives every
  hypothesis an id, refuses unsafe challenge ids and symlinked paths, and never
  resets invalid JSON silently.
- **Command logging was honest.** `tools/run.py` records explicit argv, cwd,
  timing, exit code and timeout status with no shell interpolation, and the
  README says plainly that it is not a sandbox.
- **A genuine corpus of verified work.** Eight chains in `solved/`, each with the
  mechanism, the traps hit, and how the flag was verified.
- **Offline tests existed** and did not touch the network or execute artifacts.

## Weaknesses as found

1. **Four routing tables, no single source of truth.** `SKILL_GUIDE.md`, the
   table in `ctf-playbook/SKILL.md`, the table in `web-triage/SKILL.md` and the
   `SKILLS` dict in `ctf.py` each encoded the routing rule independently, free to
   drift. Nothing checked them against each other.
2. **Five skills were unreachable from the router.** `ctf.py` never routed to
   `ctf-playbook`, `file-read-primitives`, `pwn-rop`, `ctf-malware` or
   `ctf-writeup`.
3. **Measured dilution.** 29 skills, 190 depth files, about 622,000 estimated
   tokens; `skills/ctf-web/` alone is about 110,000. Nothing told an agent when
   *not* to open one, so the cheapest wrong move — opening a depth corpus before
   the first probe — was also the easiest.
4. **`CLAUDE.md` was corrupted and contradicted the rest of the system.** It
   contained a Russian word and a Chinese word spliced mid-sentence, and it
   instructed the agent to work autonomously until the flag, while `PROMPT.md`
   and `DESIGN.md` described an operator-guided system with no autonomous loop.
5. **Two languages of instruction.** 26 of 29 `SKILL.md` files contained
   Vietnamese while `PROMPT.md` and `SKILL_GUIDE.md` were English.
6. **Documentation named tools that do not exist.** `ctf-playbook/SKILL.md` and
   `web-triage/SKILL.md` both told the agent to run `solver/recognize.py`; there
   is no `solver/` directory. `ai-iot-triage` routed to `mcp-agent-security/`,
   which does not exist. This is the exact failure the "do not invent" rule is
   meant to prevent, inside the system's own instructions.
7. **Scope leakage into the skills.** `osint-triage/SKILL.md` was an external
   engagement playbook — employee lists, breach databases, "test found
   credentials against VPN/Webmail" — and `file-read-primitives/SKILL.md` cited
   statistics about a red-team box collection and a file-harvesting tool that
   does not exist here.
8. **Chain reuse was not implemented.** `knowledge/cards/` held exactly one card,
   `writeup-claimed` and not verified, while the eight verified chains in
   `solved/` were free prose: not indexed, not matchable, invisible to
   `ctf.py related_cards`.
9. **The regression suite was four tests**, all pinned to one challenge, and
   checked nothing about the routing table, the prompt contract, the cards or the
   language.
10. **No version control.** `~/ctf` was not a git repository; `VERSIONING.md`
    described the steps but nothing executed them, so there was no state to roll
    back to.
11. **The gate could not tell a broken system from a missing package.** Two of
    the seventeen foundation tests fail when `jsonschema` and `tornado` are
    absent, with messages (`[] is not true`, `'timeout' != 'verified'`) that read
    like defects.
12. **19 MB of vendored binary** in `tools/ghidra-dist/ghidra.zip`, which
    `.gitignore` did not exclude.

## Changes made

| Weakness | Change |
|---|---|
| 1, 2, 3 | `skills/registry.json` and `skills/INDEX.md` are now the single routing table; `tools/skill_select.py` returns one entry skill, one router and at most one depth candidate, with each locked skill's reason. Large corpora sit behind an explicit `manual_gate`. Every skill on disk is registered, and the gate fails if that stops being true. |
| 4 | `CLAUDE.md` rewritten in English: the corrupted characters are gone, and the autonomy rule now states exactly when to stop rather than contradicting `PROMPT.md`. |
| 5 | Control plane and all eight routers rewritten in English; a gate check fails on Vietnamese or any unrelated script re-entering them. Depth references keep their original language deliberately — translating 190 technique files risks changing their technical content. |
| 6 | Phantom references removed; a gate check scans every skill document for them, and a second check asserts that every `tools/*.py` named in the control plane exists. |
| 7 | `osint-triage` rewritten for challenge artifacts with an explicit out-of-scope note on its inherited references; `file-read-primitives` rewritten without the invented tool and the red-team statistics. |
| 8 | All eight `solved/` notes converted into structured chain cards under `knowledge/chains/`, with preconditions, literal match signals, the chain, a first confirming probe, a blast-radius note and traps. `tools/chain_match.py` matches them against an observation or a source tree and returns candidates with a suggested priority. Flags are redacted; a gate check fails on any flag-shaped string in a card. |
| 9 | `test/regression.py` is now 31 checks in seven groups, driven by `test/cases/*.json`; `test/run_all.sh` is the gate; `test/baseline.json` is a capability floor the suite refuses to fall below. |
| 10 | `scripts/repo_init.sh` and `scripts/save_version.sh`: gate, commit, tag, push to a private repository. Every tag is a state that passed. |
| 11 | The gate separates required checks from dependency-gated ones and prints SKIPPED with the install command. |
| 12 | `.gitignore` excludes the vendored binary, media, per-challenge state and secret patterns; the white-box fixture is force-added deliberately. |
| — | A direction change now parks a hypothesis instead of closing it: `state.py --deprioritize` keeps it open at priority 0, `--revive` returns it at 40, `--show` prints the ledger by priority. `HYPOTHESIS_PROTOCOL.md` documents the scale and both gate checks cover it. |
| — | `ctf.py` signal and source rules extended with real stack, datastore and auth tokens, so shapes like "Express mongoose /update" classify instead of falling through. |
| — | `tools/import_external.py` and `external/sources.lock.json`: pin a commit, stage named files with a digest manifest, review by hand, then write a card. Staging from an unpinned source is refused. |

## Still open, honestly

- **Routing stays heuristic.** Keyword scores are not proof of exploitability. The
  golden cases in `test/cases/routing.json` pin the shapes already met; a new
  shape can still route wrongly, and the fix is to add a case, not to widen a
  pattern until the old cases break.
- **Preconditions are plain language.** `tools/chain_match.py` matches literal
  signals, not semantics. It ranks candidates; a human confirms the
  preconditions. That is deliberate — a tool that claimed to verify them would be
  the fabrication risk this system is built against.
- **Eight chain cards is a small corpus.** Coverage grows one verified solve at a
  time. `skills/ctf-writeup/SKILL.md` plus `knowledge/chain-schema.json` is the
  path; the discipline is to write the card at the moment the flag is verified.
- **The white-box regression uses one challenge.** A second and third white-box
  fixture from a different stack would make group C meaningfully stronger.
- **The benchmark is still narrow.** `tools/benchmark.py` runs one local Tornado
  fixture. It is not a black-box, white-box or exploit-chain benchmark, and the
  README does not claim it is.
- **No autonomous solving and no flag submission.** The operator runs the probes
  and verifies the flag. Nothing here changes that.
- **Depth references are still bilingual and still large.** Consolidating the
  overlapping families (`server-side-advanced` parts 1 to 4,
  `games-and-vms` 1 to 4, `patterns-ctf` 1 to 3) would cut real noise, but it
  deletes knowledge that cannot be recovered and was deliberately deferred.

## Update gate

```bash
bash test/run_all.sh
bash scripts/save_version.sh "what changed"
```

Never weaken a test case to make a change pass. If a case is genuinely obsolete,
record why in the commit message.
