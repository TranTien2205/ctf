# Evidence — what counts

- The plugin output row(s) quoting the finding.
- The dumped bytes containing the flag.
- The flag through hooks.py pre-flag.

A "suspicious-looking process name" alone is a lead.

## Levels

- Surface: a pslist row, a filescan path — names a suspect, not a finding.
- Impact: a dumped region containing the flag token, a credential,
  or typed command — this is the finding.
- The flag itself passes through `tools/hooks.py pre-flag`.
