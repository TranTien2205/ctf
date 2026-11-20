# Telnet negotiation — IAC bytes

Some services open with telnet IAC negotiation (0xFF ...) — strip the
IAC sequences before parsing text; they appear as garbage bytes at
the banner's head.

## Strip IAC

0xFF sequences before text parsing.

## Strip IAC

0xFF sequences before text parsing.
