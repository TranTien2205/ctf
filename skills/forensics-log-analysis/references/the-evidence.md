# Evidence — line + count + context

- The verbatim log line.
- The count/baseline that makes it anomalous.
- The surrounding window for context.
A bare grep hit without the distribution is a lead.

## Levels

- Surface: a line matching a grep — a lead.
- Impact: the verbatim line + the count making it anomalous + the
  window — the finding.
- A flag token inside a line still goes through pre-flag.
