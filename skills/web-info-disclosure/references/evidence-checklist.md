# Evidence — disclosure proofs — operational checklist

A disclosure finding's evidence is the artifact itself, verbatim. post-probe records the excerpt; pre-flag only on response bytes.

## Checklist

- [ ] post-probe --verdict confirms with the artifact excerpt as --evidence and the response as --response.
- [ ] pre-flag only when flag bytes are read from a live response.
- [ ] Record the catch-all baseline in field notes for future probes.
- [ ] Redact real credentials in notes — don't commit secrets.

## Abort conditions

- A catch-all 200 is NOT a finding — the content must differ from baseline.
- Tool output alone isn't evidence; the response bytes are.

## Falsifier

--

## Cross-references

`catchall-falsifier.md`
