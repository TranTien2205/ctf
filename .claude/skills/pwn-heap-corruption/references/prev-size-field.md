# prev_size — the backward pointer


prev_size is only live when P is clear (the previous chunk is free) —
then it gives the predecessor's size for the backward merge.

## Exploitation

- Set prev_size to a small value → the merge lands a short distance
  back (into controllable memory — einherjar).
- Set it large → the merge reaches deep into older heap state.

## Falsifier

The forged prev_size points at a region failing the fake-chunk checks
— the unlink aborts.
