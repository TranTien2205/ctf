# Audit: schema truthfulness

The tool description is prompt-space - check whether the
description's claims match the implementation's behavior.
A schema that lies is a confused-deputy factory.

## Check

Read each tool's description, then the code path it calls;
the description's claims (read-only, sandboxed, scoped)
must be true in code.

## Finding shape

A 'read-only' tool whose code writes, or a 'sandboxed' tool
whose code isn't, is a reject with the verbatim mismatch
quoted.

## Pivot

Module read -> the base reference files or the class boundary it names.
