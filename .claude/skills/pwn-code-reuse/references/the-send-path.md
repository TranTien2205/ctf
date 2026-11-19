# Sending the payload — the channel


The chain travels over the input channel: stdin, a socket, argv —
the bytes must survive the transport (nulls, newlines as terminators).

## The transport issues

- \x00 in an address truncates a gets()-style read — a zero in an
  address usually can't be avoided (the terminator) — the offset
  must place it last.
- \x0a/\x0d may end a line-based read.
