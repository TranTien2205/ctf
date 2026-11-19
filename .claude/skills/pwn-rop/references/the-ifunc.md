# IFUNC — the indirect function


GNU IFUNC symbols resolve through a resolver function at load —
memcpy/strchr often are; the GOT entry holds the chosen
implementation.

## The note

The resolver runs at load; the GOT holds the REAL impl — a leak of
it gives the impl's address.
