# Anti-patterns — moves that look right

## Guessing the arg offset
Trial-and-error N instead of the systematic AAAA.%N$p sweep. Fix: one
sweep names N.

## Building the write before the offset
%n before knowing which arg index your pointer sits at. Fix: AAAA.%N$p
first.

## Assuming %n writes the target's address
%n writes the byte COUNT to *ptr — the pointer is the ARGUMENT, the count
is the value. Fix: plant the address, steer the count.

## Ignoring the cumulative count
Multiple %n in one call share the count — each write sees all printed
bytes. Fix: plan the cumulative count, or write byte-wise.

## Treating a leak as the exploit
A %p dump is a leak, not the flag — it feeds the write/smash.
