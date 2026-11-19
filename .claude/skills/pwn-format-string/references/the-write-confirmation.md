# Confirming the write — the read-back


A %n write is proven by reading the target back: the GOT entry's new
value, the ret-addr's new address — the changed bytes are the evidence.

## The proof

- The target's value changed → the write landed.
- A second %s read shows it → the verification.
- A redirect that fires is also confirmation.

## Steps

1. After the write, read the target back — %s or a re-trigger.
2. The changed bytes confirm the write landed.
3. A redirect that fires is also confirmation.

## Falsifier

The target's value doesn't change when %n fires: the pointer isn't at
the arg position; re-find N.
