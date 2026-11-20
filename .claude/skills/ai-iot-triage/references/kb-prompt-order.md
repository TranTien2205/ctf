# Prompt-handling cost order

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Direct ask (cheapest) -> reframe/translate -> encode ->
persona -> indirect via read-back -> tool-drive. Each
rung costs more; stop at the first that works.

## Pivot

Module read -> the router or sibling module the observation names.
