# __builtins__ under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** __builtins__ — eval/exec/__import__.

The chain survives if the attribute name is reachable without the blocked token.
