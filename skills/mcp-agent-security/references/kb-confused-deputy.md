# Confused deputy, agent edition

The agent holds permissions the caller lacks - an injection
that drives the agent's tools routes the attacker's intent
through the agent's privilege. The deputy is confused when
it cannot tell the instruction source apart.

## Shape

Attacker content -> agent context -> agent's privileged
tool call. The boundary the audit checks is whether the
agent can distinguish instruction sources.

## Pivot

Module read -> the base reference files or the class boundary it names.
