# The second channel — stderr, logs, deferred output


When stdout isn't your channel, the format output may go to stderr, a
log file, or a follow-up response — the leak's channel decides if you
can harvest it.

## Steps

1. stdout=socket: reflected. stderr/log: not on socket.
2. A deferred channel: the next response carries the output.
3. Check every channel before concluding blind.

## Falsifier

No channel returns the output: the read is unharvestable; only a blind
write remains.
