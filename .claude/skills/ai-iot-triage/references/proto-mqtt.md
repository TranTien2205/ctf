# MQTT capture detail

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Wildcard subscribe (#) catches every topic - the flag often sits
in a topic the client never subscribes to. Read retained messages
first; they persist without live traffic.

## Pivot

Module read -> the router or sibling module the observation names.
