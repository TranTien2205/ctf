# argv/env strings as write targets


argv/env strings live on the stack — their addresses are leakable;
writing INTO an argv string (if it's the format) or past it targets
stack data.

## Steps

1. argv/env pointers appear in the %p dump as stack-top addresses.
2. A string slot in argv is writable stack memory.
3. Patching an argv string affects later uses of it.

## Falsifier

Nothing useful sits at the argv/env region.
