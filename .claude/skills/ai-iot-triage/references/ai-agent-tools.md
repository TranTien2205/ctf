# The agent/tool surface

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

An agent with tools is a different challenge than a bare model -
map every tool it can reach and what data crosses into it. The
mcp-agent-security skill owns the tool-surface depth; this
router hands off once the agent shape is confirmed.

## Pivot

Module read -> the router or skill the boundary names, or the sibling
module the artifact points to.
