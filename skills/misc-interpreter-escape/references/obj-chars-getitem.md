# __getitem__ under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** __getitem__ — dict access.

The chain survives if the attribute name is reachable without the blocked token.
