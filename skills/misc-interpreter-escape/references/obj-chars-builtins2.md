# __builtins__ dict under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** __builtins__ dict — the namespace dict.

The chain survives if the attribute name is reachable without the blocked token.
