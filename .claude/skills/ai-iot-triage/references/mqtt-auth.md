# MQTT auth shapes

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Anonymous subscribe allowed vs username/password required -
the ACL question is itself a signal; default creds are the
first test.

## Pivot

Module read -> the router or sibling module the observation names.
