# __globals__ under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** __globals__ — the func namespace.

The chain survives if the attribute name is reachable without the blocked token.
