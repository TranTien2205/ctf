# Filesystem scope

Depth module for `mcp-agent-security`. Open `../SKILL.md` for the
two-half framing first (offensive vs defensive); this file is one
named piece of the corpus - never a finding by itself. A model's
own text is never evidence of a flag.

Read vs write, path allowlist vs unrestricted, sensitive-path reach (.ssh, .env, creds) - the fs boundary is the first check.

## Pivot

Module read -> the base reference files or the class boundary it names.
