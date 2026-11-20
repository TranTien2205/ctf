# JTAG/SWD note

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Debug interfaces on the board - mostly out of scope for
jeopardy (no hardware), but a JTAG-log artifact is read
like a UART dump.

## Pivot

Module read -> the router or sibling module the observation names.
