# Two pointer args — read and write in one call


A single fmtstr can plant TWO pointers: %N$s reads through the first,
%M$n writes through the second — read and write in one call.

## Steps

1. Plant ptr A at arg N, ptr B at arg M.
2. %N$s derefs A (read), %M$n writes to *B.
3. Order matters: the count for %n includes everything printed before
   it.

## Falsifier

Only one pointer position is plantable: pick read or write.
