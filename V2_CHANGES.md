# ctf-v2 — what differs from ~/ctf

Built 2026-09-17. Update gate on this tree: **PASS** — 62 regression checks, 26 self-check, routing 5/5 and 13/13 golden cases, 0 review / 0 warn across 46 skills.

## Increment 2026-09-17 (session 3): one language, resolvable references, a gate that bites

A review pass, not a feature pass. Everything below was a defect found by reading
the tree, and each one now has a regression check so it cannot come back.

**One language.** The tree is English end to end. `AGENTS.md` (103 lines) and
`solved/weather_app.md` (18 lines) were translated; the stray CJK characters in
`skills/web-file-upload/references/content-bypass.md` and
`skills/ctf-misc/encodings.md` were removed, along with a Vietnamese word left in
the `tools/skill_audit.py` docstring. The language detectors in
`test/regression.py` used to be written with literal Vietnamese characters, so the
file tripped its own check; they are now built from integer codepoints and the
file is pure ASCII.

The check itself was scoped to eleven control-plane files. It now runs over all
364 authored files. It distinguishes two things that were previously conflated:
codepoints only Vietnamese uses (never allowed, no exceptions) and accented Latin
vowels shared with Spanish, Portuguese and French (allowed outside the control
plane, because a Spanish search string in an OSINT skill is data, not
instruction). Cyrillic, CJK, Kana and Hangul must be declared in
`test/gate-exemptions.json` with a reason; exactly one file declares them, the
homoglyph table in `skills/ctf-osint/social-media.md`, where the codepoints are
the technique being taught.

**Resolvable references.** 155 files named by a SKILL.md did not exist in this
tree: the depth corpus for crypto, pwn, reverse, forensics, misc, osint, ai-ml and
malware was never carried over. They are restored, and a new check walks every
markdown file under `skills/` and fails on any named `.md` that is not on disk. It
found four more real breaks: a phantom `references/anti-analysis.md` in
`rev-triage` (the file lives in `ctf-reverse/`), three SQL dialect references
written without their directory in `web-sqli`, a `field-notes.md` promised by
`mcp-agent-security` that did not exist, and a reference in
`mcp-agent-security/references/prompt-injection-testing.md` still pointing at an
`evidence-and-reporting` skill that belongs to the other toolkit and was never
ported. Generic mentions (the phrase "a SKILL.md") are exempted by name, with a
reason.

**A gate that bites.** `test/run_all.sh` called `test/capability_report.py`
without checking its exit status, and that script imported the suite as
`test.regression`, which only resolves while an empty `test/__init__.py` shadows
the standard library's own `test` package. Delete one empty file and the gate
reported PASS while the capability snapshot crashed. The script now loads the
suite by path, the gate checks the exit status, and two new tests keep both ends
honest: one runs the report and parses its JSON, one asserts that every step
`run_all.sh` labels REQUIRED sets the failure flag.

**A tree that runs anywhere.** 99 commands began with a hardcoded home-relative
tree root that pointed at the old tree while this one sat elsewhere. All of them
are now relative to the root, so the tree works wherever it is checked out, and a
new check enforces it. `AGENTS.md` is the single exemption: it is the bootstrap
file and the one place that says where the tree lives, so moving the tree means
editing exactly one file.

**The last bloated router.** `skills/ctf-misc/SKILL.md` was 455 lines of mixed
routing and depth, duplicating its own reference files. It is now a 100-line
router with two first probes, a falsifier and a 15-row signal table; its 34 depth
sections moved verbatim into six named files: `toolbox.md`,
`encoding-and-cipher.md`, `data-hiding.md`, `solvers.md`, `jails-and-shells.md`
and `platform-and-network.md`. The two sections about escalating privilege on a
Linux host you already hold carry an explicit scope note: they apply to a jeopardy
challenge that hands you a shell, and machine or Active Directory privilege
escalation remains out of scope for this tree. `web-ssti` and
`file-read-primitives` gained the First probe and Falsifier sections the format
requires, quoting `knowledge/bug-classes.json` rather than inventing new content.
The skill audit is now 0 review / 0 warn across all 46 skills.

Six new regression checks, 56 to 62. Every one was verified to fail on the defect
it describes before being accepted.

## Increment 2026-09-17 (session 2): orchestrator + hooks + skill audit

Added after the first v2 delivery, without touching any metric baseline:

- `AGENTS.md` — the session bootstrap file, auto-loaded by every new agent
  session (CTF-only; the red-team boundary is stated without naming
  red-team techniques).
- `tools/decide.py` — the external decision controller. Reads the
  per-challenge state and returns one action: `start_recon`,
  `new_hypothesis`, `run_probe`, `switch_class`, `reopen_confirm`,
  `verify_flag`, `record_solve`, `search_writeup`, `stop_report`. It never
  writes state. It enforces the protocol the agent previously only promised
  to follow: 5 probes / 15 minutes per class force a layer switch, a
  confirmation without a confirming probe is reopened, a flag without live
  evidence is a candidate, a matching chain card's probe runs before any
  novel hypothesis.
- `tools/hooks.py` — the verification gates and the only write path for
  probe verdicts, confirmations and flags. `post-probe --verdict confirms`
  must quote the response excerpt; a timeout is refused as a confirmation.
  `pre-probe` rejects duplicate requests (syntax churn) and write-shaped
  probes without `--write-ack`. `pre-confirm` and `pre-flag` gate the
  confirm/flag lifecycle.
- `tools/skill_audit.py` + `knowledge/skill-audit.json` — the trash-skill
  filter. Scores every skill on first probe, falsifier/stop-conditions,
  discipline/traps, field-notes content, evidence honesty, size and
  nearest-neighbour overlap. Verdicts: pass / warn / review.
- Fixed the three skills the audit flagged as weakest (missing first probe
  and discipline sections): `web-file-upload`, `web-deserialization`,
  `web-auth-session`. Audit result is now 0 review / 1 warn (`ctf-misc`
  bloated router, a real finding).
- `CLAUDE.md` table now points at AGENTS.md, decide.py, hooks.py and
  skill_audit.py.
- 10 new regression checks (`OrchestratorTests`) cover every gate: flag
  evidence, unsupported confirmations, budget switch, chain-card priority,
  empty-state classification, evidence-free confirms, duplicate and
  write-shaped probes, the confirm/flag lifecycle, AGENTS.md boundaries,
  and skill-audit consistency.

`tools/decide.py` and `tools/hooks.py` are the "external decision maker"
requested for exploit chains: step 1 finds a signal, the verdict goes through
the hook with evidence, and the controller decides whether the next step is
another probe, a class switch, a flag verification or a stop.

This is a parallel tree. It does not touch `~/ctf`, which is still the running system.

```bash
tar xzf ~/ctf/ctf-v2.tar.gz -C ~        # creates ~/ctf-v2
cd ~/ctf-v2 && bash test/run_all.sh      # verify on your own machine
```

## New (61 files)

- `LEARNING_LOOP.md`
- `build/make_bug_classes.py`
- `build/make_class_skills.py`
- `build/make_index.py`
- `build/make_registry.py`
- `challenges/Weather App/web_weather_app/challenge/static/css/main.css`
- `challenges/Weather App/web_weather_app/challenge/static/js/koulis.js`
- `challenges/Weather App/web_weather_app/challenge/static/js/main.js`
- `knowledge/bug-classes.json`
- `skills/file-read-primitives/field-notes.md`
- `skills/mcp-agent-security/SKILL.md`
- `skills/mcp-agent-security/references/prompt-injection-testing.md`
- `skills/mcp-agent-security/references/tool-permission-audit.md`
- `skills/security-skill-evaluation/SKILL.md`
- `skills/security-skill-evaluation/references/eval-task-templates.md`
- `skills/security-skill-evaluation/references/skill-quality-rubric.md`
- `skills/web-auth-session/field-notes.md`
- `skills/web-cache-poisoning/SKILL.md`
- `skills/web-cache-poisoning/field-notes.md`
- `skills/web-chromedriver/SKILL.md`
- `skills/web-chromedriver/references/webdriver-api.md`
- `skills/web-command-injection/SKILL.md`
- `skills/web-command-injection/field-notes.md`
- `skills/web-cors/SKILL.md`
- `skills/web-cors/field-notes.md`
- `skills/web-csrf/SKILL.md`
- `skills/web-csrf/field-notes.md`
- `skills/web-deserialization/field-notes.md`
- `skills/web-file-upload/field-notes.md`
- `skills/web-graphql/SKILL.md`
- `skills/web-graphql/field-notes.md`
- `skills/web-idor/field-notes.md`
- `skills/web-logic-flaw/SKILL.md`
- `skills/web-logic-flaw/field-notes.md`
- `skills/web-nosqli/SKILL.md`
- `skills/web-nosqli/field-notes.md`
- `skills/web-oauth-sso/SKILL.md`
- `skills/web-oauth-sso/field-notes.md`
- `skills/web-open-redirect/SKILL.md`
- `skills/web-open-redirect/field-notes.md`
- `skills/web-parser-differential/SKILL.md`
- `skills/web-parser-differential/field-notes.md`
- `skills/web-prototype-pollution/SKILL.md`
- `skills/web-prototype-pollution/field-notes.md`
- `skills/web-race-condition/SKILL.md`
- `skills/web-race-condition/field-notes.md`
- `skills/web-request-smuggling/SKILL.md`
- `skills/web-request-smuggling/field-notes.md`
- `skills/web-sqli/field-notes.md`
- `skills/web-ssrf/field-notes.md`
- `skills/web-ssti/field-notes.md`
- `skills/web-web3/SKILL.md`
- `skills/web-web3/field-notes.md`
- `skills/web-xss/field-notes.md`
- `skills/web-xxe/SKILL.md`
- `skills/web-xxe/field-notes.md`
- `test/cases/classify.json`
- `test/fixtures/benign-express/app.js`
- `test/fixtures/benign-express/db.js`
- `tools/classify.py`
- `tools/classify_solve.py`

## Changed (17 files)

- `CLAUDE.md`
- `PROMPT.md`
- `skills/INDEX.md`
- `skills/file-read-primitives/SKILL.md`
- `skills/registry.json`
- `skills/web-auth-session/SKILL.md`
- `skills/web-deserialization/SKILL.md`
- `skills/web-file-upload/SKILL.md`
- `skills/web-idor/SKILL.md`
- `skills/web-sqli/SKILL.md`
- `skills/web-ssrf/SKILL.md`
- `skills/web-ssti/SKILL.md`
- `skills/web-triage/SKILL.md`
- `skills/web-triage/references/signal-to-skill-map.md`
- `skills/web-xss/SKILL.md`
- `test/baseline.json`
- `test/regression.py`

## Unchanged, carried over (26 files)

Already identical in `~/ctf`; present here only so the tree is complete and the
gate can run against it.

