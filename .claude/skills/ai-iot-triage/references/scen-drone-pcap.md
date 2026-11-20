# Scenario: drone/telemetry capture

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

A protocol capture of telemetry - identify the protocol
from ports/magic, then read the fields; flag as a field
value or an exfil channel.

## Pivot

Module read -> the router or sibling module the observation names.
