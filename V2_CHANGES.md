# ctf-v2 — what differs from ~/ctf

Built 2026-09-17. Update gate on this tree: **PASS** — 46 regression checks, 26 self-check, routing 5/5 and 13/13 golden cases.

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

