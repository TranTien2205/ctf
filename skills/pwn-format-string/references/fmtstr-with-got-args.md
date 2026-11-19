# When a GOT entry is already an arg


Sometimes a printf argument IS already a pointer to something useful:
%N$s on it reads that memory for free — no planting needed.

## Steps

1. Scan %N$p: an arg that's already a pointer is a free deref target.
2. %N$s on it reads the pointee — if it's a GOT entry, that's a libc
   leak.
3. A saved-string-pointer arg reads the string.

## Falsifier

No existing arg holds a useful pointer: plant your own.
