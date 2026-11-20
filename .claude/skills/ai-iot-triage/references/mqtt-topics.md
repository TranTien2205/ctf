# MQTT topic shapes

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

home/..., sensor/..., flag/... - topic names themselves carry
information; the wildcard dump plus retained messages is the
full inventory.

## Pivot

Module read -> the router or sibling module the observation names.
