# Audit: logging and observability

What the server logs about calls and results - an unlogged
tool surface cannot be audited after the fact.

## Check

Per-tool call logging, result logging, the log's own access
controls, and whether secrets are scrubbed from it.

## Finding shape

No call log on a state-changing tool is a finding; secrets
in the log is a different one.

## Pivot

Module read -> the base reference files or the class boundary it names.
