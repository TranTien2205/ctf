# Heap vs loader regions — address geography


The address ranges tell apart: heap (brk'd, near 0x55.. for PIE or a
separate segment), libc (mmap'd 0x7f..), stack (0x7ff..), ld.so (another
0x7f.. region).

## Reading a leaked value

- 0x55/0x56.. → PIE binary or main-arena-relative heap.
- 0x7f.. mid → libc/ld mappings.
- 0x7ff.. high → stack.
- Small ints → counts/sizes, not pointers.

The range guess is fast and always wrong sometimes — confirm by
round-tripping a known-write.
