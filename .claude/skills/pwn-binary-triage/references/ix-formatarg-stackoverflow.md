# Input cell: format-arg / stack-overflow

Routing module for `pwn-binary-triage`. This file names the protections, the IP-control proof, and the depth file the route selects; it never writes the exploit.

Whether `format-arg` input can produce `stack-overflow`.

## Read

The input surface's reach against the family's requirement -
a stdin read to a stack buffer says stack-overflow; a format
arg reaching printf says format-string. The cell names the
code shape that would make the pairing real.

## Falsifier

The source or disassembly observation showing the input does
NOT reach the family's sink - recorded as a proved negative.
