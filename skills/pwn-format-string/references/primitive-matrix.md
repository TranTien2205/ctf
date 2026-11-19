# The format-specifier matrix — what each one buys

The specifier is the whole primitive: %p/%x read, %s dereferences, %n/%hn/%hhn write. Choosing the right one IS the exploit.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| %p/%x in a leaked output | read primitive | the leak |
| %s at a planted pointer | arbitrary read | the deref |
| %n/%hn/%hhn | arbitrary write | the write |
| a literal %s or %p | interprets nothing | closed |

## Steps

1. Identify which specifiers the input passes through printf-like calls.
2. %p/%x → read the stack/registers; %s → dereference a pointer you plant; %n/%hn/%hhn → write.
3. The width variants decide the write's granularity: n=qword, hn=2 bytes, hhn=1 byte.
4. The primitive available decides the chain.

## Falsifier

Falsifier — the format argument is a literal and your input is an argument to it (printf("%s", buf)): nothing is interpreted; the class is closed.

## Traps

- %n writes the count of bytes printed SO FAR — the %c/field-width controls it.
- x64: the first 6 args are in registers; the stack-args start at %7$p-ish.
- %s dereferences a POINTER — you plant it; %p just prints the value.

## Cross-references

`arg-offset-finder.md` · `arb-read-via-s.md`
