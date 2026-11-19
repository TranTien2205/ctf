# The read primitive — the mov-load gadget


`mov rX, [rY]; ret` reads [rY] into rX — but the value stays in a
register — useless alone; pair it with a store or a print.

## The note

A "read" in ROP terms is really a leak — the value must reach an
output (a write() call, a puts() call) to be observed.
