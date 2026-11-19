# Two-stage write — a write that enables a bigger write

A first %n can write a pointer or a bound that makes a SECOND input's write/overflow reach further — the write that enables the next primitive.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a bounded second input | first write extends it | the enabling write |
| a pointer written first | plants the arg for stage 2 | the setup |
| a bound/length field writable | enlarge the buffer for stage 2 | the write |

## Steps

1. Identify what a first write could enable: a planted pointer, an enlarged bound, a redirected arg.
2. Stage 1: %n write of the enabling value.
3. Stage 2: a later input/overflow that uses it — reaches further.
4. The two writes compose into the final primitive.

## Falsifier

Falsifier — nothing the first write could change makes the second input reach further: no composition.

## Traps

- The enabling write plants a pointer the second read derefs.
- A bound-field write enlarges a bounded second buffer's reach.

## Cross-references

`multi-target-write.md` · `second-stage.md`
