# Heap corruption — the closing notes


The class is the allocator-as-confused-deputy: corrupt its state, it
writes for you. The whole skill is: name the version → name the
primitive → leak before write → satisfy the checks on the path you
take → verify each stage → land on a firing target.

The catalog of techniques is large; the discipline is small. The
version question and the check-satisfaction question answer almost
every "why didn't it work".

The field-notes grow per solve: each new technique or check-bypass a
real challenge teaches belongs in field-notes.md — proposed until
reviewed, confirmed after.
The corpus covers: version detection, chunk anatomy, every bin, UAF,
double-free, tcache/fastbin/unsorted techniques, the house-of family,
leaks at every level, grooming, FSOP, and the ending table.
