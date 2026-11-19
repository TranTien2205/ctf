# Dead ends — the routes that don't work


- Writing .text: read-only — code can't be patched by a write.
- A GOT overwrite under full RELRO: the GOT is read-only.
- A call to a non-imported libc function without a leak: unaddressable.
- A gadget that doesn't exist: can't be conjured — substitute.
