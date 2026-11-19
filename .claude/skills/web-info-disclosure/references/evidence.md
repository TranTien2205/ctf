# Evidence — disclosure proofs

A disclosure finding's evidence is the artifact itself, verbatim. post-probe records the excerpt; pre-flag only on response bytes.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| The artifact content itself | proof | post-probe class evidence |
| The recovered repo/source | impact when it leads somewhere | chain to sink |
| Catch-all baseline diff | the discriminator | record in notes |

## Steps

1. post-probe --verdict confirms with the artifact excerpt as --evidence and the response as --response.
2. pre-flag only when flag bytes are read from a live response.
3. Record the catch-all baseline in field notes for future probes.
4. Redact real credentials in notes — don't commit secrets.

## Falsifier

--

## Traps

- A catch-all 200 is NOT a finding — the content must differ from baseline.
- Tool output alone isn't evidence; the response bytes are.

## Commands

```bash
python3 tools/hooks.py post-probe <ch> --verdict confirms --hypothesis-id <id> --class web-info-disclosure --evidence-kind class --evidence 'ref: refs/heads/main' --response '<the bytes>'
```

## Cross-references

`catchall-falsifier.md`
