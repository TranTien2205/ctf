# Bin sort order — largebin's size lines


Large bins hold chunks sorted by size descending; insert finds the
first chunk smaller than the new one — the sorted walk is the write
primitive's machinery.

## Reading it

`dmh`/`dmhb` in r2 -d shows bin membership and order.

## Exploitation

- bk_nextsize corruption aims the sorted-link write.
- A fake chunk with a chosen size slot inserts at a chosen position.

## Falsifier

The size ordering never walks your corrupted node: the insert doesn't
deliver the write.
