# Planting the pointer — getting your address into a %N position


Every %s/%n needs a pointer at an argument position: the pointer is what
%s derefs or %n writes to. Planting it inside your own input is the usual
move.

## How

- Your input bytes land as an argument — a pointer written as raw bytes
  in the input becomes arg[N].
- AAAA.<addr-as-8-bytes>.%N$s — the addr is in your input, %N$s derefs it.
- The addr must be at the right argument position — the arg-offset-finder.

## Falsifier

The input bytes can't be placed at a %N-arg position, or the position
isn't a pointer slot: no dereference/write is possible.
