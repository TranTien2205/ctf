# Theory — why each move works

## Why %p leaks
printf reads varargs by position — %p prints the Nth arg's value, which
for stack args is stack memory.

## Why %s derefs
%s reads the Nth arg AS A POINTER — plant a pointer, it prints *ptr.

## Why %n writes
%n writes 'bytes printed so far' to *arg — plant a pointer, control the
count via %c/width, write an arbitrary value.

## Why %hhn for addresses
A 64-bit address is 8 bytes; %hhn writes count&0xff — set each byte with
a controlled count, one %hhn per byte.

## Why the arg-offset matters
Every specifier is index-addressed — without N, the primitive is blind.
