# nvram / config partitions

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Device configuration blobs at the flash edges - wifi
credentials and admin passwords persist here; strings on
the partition finds them.

## Pivot

Module read -> the router or sibling module the observation names.
