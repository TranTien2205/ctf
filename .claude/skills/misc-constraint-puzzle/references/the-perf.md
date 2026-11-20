# Speed — where rounds actually cost

Profile before optimizing: usually the parse or the solve, rarely
the socket. recv buffering and a compiled regex are the usual wins;
threads rarely help.

## Profile first

Parse/solve cost, not the socket — buffer + compiled regex.
