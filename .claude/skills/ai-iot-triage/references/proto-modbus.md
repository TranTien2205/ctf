# Modbus detail

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Function codes and register addresses - the capture's reads/
writes map the device state. The flag sits in a register nobody
reads normally; compare the capture's register set to the spec.

## Pivot

Module read -> the router or sibling module the observation names.
