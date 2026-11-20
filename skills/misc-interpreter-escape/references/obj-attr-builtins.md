# __builtins__ under attribute access blocked

**Filter:** attribute access blocked — . rejected.

**Chain:** __builtins__ — eval/exec/__import__.

The chain survives if the attribute name is reachable without the blocked token.
