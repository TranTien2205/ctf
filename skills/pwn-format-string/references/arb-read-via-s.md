# Arbitrary read via %s — dereference a planted pointer

%s dereferences a pointer argument — plant a pointer where a %N$s arg reads it and %s prints the memory it points to. An arbitrary read in one specifier.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a pointer you control lands as a %N$s arg | %s derefs it | arbitrary read |
| a target address to read | plant it as the arg | %s prints *ptr |
| need to read flag/.rodata/secret | the read primitive | %s at the ptr |

## Steps

1. Plant the target address as an argument (in your input or via a controllable slot).
2. Send %N$s at that argument's index — it derefs and prints the target.
3. Read the bytes from the output — arbitrary read of the target's memory.
4. Read until \x00 — a null in the target truncates.

## Falsifier

Falsifier — you can't plant a pointer where a %N$s arg reads it: no controlled dereference; only the leak-via-%p path remains.

## Traps

- %s reads until a null byte — a \x00 in the target truncates the read.
- The pointer must be at a %N$s-readable argument position.
- A GOT entry or a flag-path address is the usual target.

## Cross-references

`arb-write-via-n.md` · `arg-offset-finder.md`
