# Arbitrary read via %s — dereference a planted pointer — checklist

%s dereferences a pointer argument — plant a pointer where a %N$s arg reads it and %s prints the memory it points to. An arbitrary read in one specifier.

## Checklist

- [ ] Plant the target address as an argument (in your input or via a controllable slot).
- [ ] Send %N$s at that argument's index — it derefs and prints the target.
- [ ] Read the bytes from the output — arbitrary read of the target's memory.
- [ ] Read until \x00 — a null in the target truncates.

## Abort conditions

- %s reads until a null byte — a \x00 in the target truncates the read.
- The pointer must be at a %N$s-readable argument position.
- A GOT entry or a flag-path address is the usual target.

## Falsifier

Falsifier — you can't plant a pointer where a %N$s arg reads it: no controlled dereference; only the leak-via-%p path remains.
