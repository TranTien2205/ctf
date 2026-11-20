# Hardware dumps

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

UART logs, SPI flash dumps, RF captures - binwalk carves
the firmware, and radio captures route to
`../../ctf-misc/rf-sdr.md`. The artifact's format decides
the owner.

## Pivot

Module read -> the router or skill the boundary names, or the sibling
module the artifact points to.
