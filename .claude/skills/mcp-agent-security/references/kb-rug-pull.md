# Rug pull / redefinition

A server that changes its tool set after install - the
tools/list response is a snapshot, not a contract. The
audit pins the server and re-checks on update.

## Check

Hash the manifest and the code at install; re-verify on
any update before the tool surface is trusted again.

## Pivot

Module read -> the base reference files or the class boundary it names.
