# Lazy binding — the un-resolved GOT


Without BIND_NOW, GOT entries hold resolver addresses until first
called — reading them leaks the PLT resolver, not libc.

## The consequence

- puts(got[x]) before x was called prints a resolver stub address —
  a binary address, not libc.
- Call the function once first, or read an already-called import's
  GOT entry.

## Falsifier

No import has been called and none can be invoked: the GOT reads are
all resolver stubs — the leak must come from elsewhere.
