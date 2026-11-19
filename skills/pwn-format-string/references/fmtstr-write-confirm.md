# Confirming the write — read-back verification


After a %n write, read the slot back — %N$s on the same address confirms
the bytes changed before you fire the redirect.

## Steps

1. Write: <ptr>.%Nc.%M$hhn plants the byte.
2. Read-back: %N$s on the slot prints its (changed) contents.
3. Compare to the intended value.
4. Only then fire the redirect (call the import / return / free).

## On a loop service

Call 2 writes, call 3 reads-back — verification without firing.

## Falsifier

The read-back shows the old value: the write missed — check the pointer
alignment, the arg index, the count arithmetic.
