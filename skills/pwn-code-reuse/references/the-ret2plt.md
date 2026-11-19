# ret2plt — the no-libc-leak call


Calling a PLT stub directly uses the BINARY's stub — no libc leak
needed for the imported functions.

## The limit

Only imported functions are PLT-callable — system usually isn't
imported; puts/printf/write are — the leak still needs libc for the
ending.
