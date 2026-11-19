# argv/env strings as write targets — checklist

Companion to `fmtstr-argv-globals.md`.

## Checklist

- [ ] 1. argv/env pointers appear in the %p dump as stack-top addresses.
- [ ] 2. A string slot in argv is writable stack memory.
- [ ] 3. Patching an argv string affects later uses of it.
