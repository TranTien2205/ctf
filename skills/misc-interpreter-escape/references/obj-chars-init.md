# __init__ under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** __init__ — the init func.

The chain survives if the attribute name is reachable without the blocked token.
