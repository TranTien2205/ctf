# Tool-call grammar

Depth module for `mcp-agent-security`. The model's own text
is never evidence of a flag.

The model emits a structured call (name + JSON args) -
the injection's target is making that call carry
attacker arguments. The grammar itself is the
injection's destination shape.

## Pivot

Module read -> the base reference files or the class boundary it names.
