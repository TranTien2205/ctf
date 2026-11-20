# Audit: auto-execution set

Which tools run without confirmation - the unconfirmed set is
the reachable set for any injection that lands. Confirmation in
docs is not confirmation in code.

## Check

The server manifest or config for per-tool confirmation gates;
the client's own gating list; the destructive-action boundary
(delete, send, pay, write) specifically.

## Finding shape

A destructive tool with no code-level gate is a reject; a
read-only unconfirmed tool is a normal risk.

## Pivot

Module read -> the base reference files or the class boundary it names.
