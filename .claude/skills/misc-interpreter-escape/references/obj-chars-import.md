# __import__ under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** __import__ — the import func.

The chain survives if the attribute name is reachable without the blocked token.
