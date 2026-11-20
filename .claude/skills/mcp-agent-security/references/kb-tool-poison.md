# Tool poisoning

A malicious server's tool descriptions carrying
instructions - the schema is prompt-space, so the
server's own description field is an injection surface
before any tool is even called.

## Audit

Read every tool description as adversarial content; a
description that contains instructions, not just docs,
is a finding.

## Pivot

Module read -> the base reference files or the class boundary it names.
