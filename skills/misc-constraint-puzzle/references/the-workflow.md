# The workflow — capture, parse, loop

1. net_dialog once — the verbatim transcript.
2. Solver against the captured format: buffer-until-terminator,
   lenient parse, exact reply.
3. One round works -> run; log raw bytes per round.
4. Then optimize: timeout, buffering, batching.

## The order

Capture -> solver -> run -> optimize.

## The order

Capture -> solver -> run -> optimize.
