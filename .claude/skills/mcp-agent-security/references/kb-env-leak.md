# Env-var leakage path

Depth module for `mcp-agent-security`. The model's own text
is never evidence of a flag.

A server reading its env vars is normal; a tool returning
env content into context is the leak path. The audit maps
which env vars exist vs which tools' outputs could
carry them.

## Pivot

Module read -> the base reference files or the class boundary it names.
