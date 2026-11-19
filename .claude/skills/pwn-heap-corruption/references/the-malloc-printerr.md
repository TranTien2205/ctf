# malloc_printerr — the abort path


Every check failure calls __libc_message → malloc_printerr → abort —
the abort message prints to stderr via _IO_2_1_stderr_ (the FSOP side
effect).

## Exploitation note

- The abort itself uses stdio — a corrupted stderr FILE fires DURING
  the abort handling.
- Reading the abort text names the failed check — your diagnostic.

## Falsifier

None — the abort is evidence.
