# os._wrap_close under a char blacklist

**Filter:** a char blacklist — bytes like () or ' blocked.

**Chain:** os._wrap_close — a common gadget.

The chain survives if the attribute name is reachable without the blocked token.
