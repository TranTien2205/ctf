# The register map

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Register addresses vs the device's documented map - a read
outside the documented range, or a write to an odd address,
marks the interesting transaction.

## Pivot

Module read -> the router or sibling module the observation names.
