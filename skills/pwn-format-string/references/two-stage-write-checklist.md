# Two-stage write — a write that enables a bigger write — checklist

A first %n can write a pointer or a bound that makes a SECOND input's write/overflow reach further — the write that enables the next primitive.

## Checklist

- [ ] Identify what a first write could enable: a planted pointer, an enlarged bound, a redirected arg.
- [ ] Stage 1: %n write of the enabling value.
- [ ] Stage 2: a later input/overflow that uses it — reaches further.
- [ ] The two writes compose into the final primitive.

## Abort conditions

- The enabling write plants a pointer the second read derefs.
- A bound-field write enlarges a bounded second buffer's reach.

## Falsifier

Falsifier — nothing the first write could change makes the second input reach further: no composition.
