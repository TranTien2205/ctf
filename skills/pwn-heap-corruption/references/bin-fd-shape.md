# The fd's shape — what a bin link looks like


A free chunk's fd value identifies its bin: tcache/fastbin fd = a heap
pointer (or mangled one); unsorted/small fd = &main_arena.bins[..]; a
null fd = the bin's tail.

## Reading a dump

- 0x55/0x56-shaped fd → tcache/fastbin (heap).
- 0x7f..-shaped fd → arena-resident (unsorted/small/large).
- mangled fd (2.32+) → weird values — de-mangle with pos>>12.

## Falsifier

You can't tell which bin the chunk sits in from the fd — dmh shows it
directly.
