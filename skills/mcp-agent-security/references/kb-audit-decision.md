# The audit's decision shape

Depth module for `mcp-agent-security`. The model's own text
is never evidence of a flag.

Pass, rated risk, or reject - per tool and per server.
The output is a decision record: the inventory table,
the findings with verbatim mismatches, the reject
list. A 'looks fine' with no table is not an audit.

## Pivot

Module read -> the base reference files or the class boundary it names.
