# __builtins__ under a word blacklist

**Filter:** a word blacklist — names blocked as strings.

**Chain:** __builtins__ — eval/exec/__import__.

The chain survives if the attribute name is reachable without the blocked token.
