# The format-specifier matrix — what each one buys — checklist

The specifier is the whole primitive: %p/%x read, %s dereferences, %n/%hn/%hhn write. Choosing the right one IS the exploit.

## Checklist

- [ ] Identify which specifiers the input passes through printf-like calls.
- [ ] %p/%x → read the stack/registers; %s → dereference a pointer you plant; %n/%hn/%hhn → write.
- [ ] The width variants decide the write's granularity: n=qword, hn=2 bytes, hhn=1 byte.
- [ ] The primitive available decides the chain.

## Abort conditions

- %n writes the count of bytes printed SO FAR — the %c/field-width controls it.
- x64: the first 6 args are in registers; the stack-args start at %7$p-ish.
- %s dereferences a POINTER — you plant it; %p just prints the value.

## Falsifier

Falsifier — the format argument is a literal and your input is an argument to it (printf("%s", buf)): nothing is interpreted; the class is closed.
