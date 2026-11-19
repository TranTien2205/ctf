# The send path — getting bytes down the wire


The payload's journey: the script's bytes → the socket → the service's
read buffer → the stack frame — each hop must preserve them.

## The per-hop checks

- The script packs correctly (the self-check).
- The socket sends all (sendall, not send).
- The service's read accepts them (the length and the terminators).
- The frame's layout matches the measured offset.
