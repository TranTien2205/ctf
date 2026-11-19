# fd/bk offsets in the user area — x64 map


Freed chunk user area (x64):
+0x00 e->next / fd
+0x08 e->key (tcache) / bk (small/large)
+0x10 fd_nextsize (large only)
+0x18 bk_nextsize (large only)

## x86 offsets

+0x00 fd; +0x04 key/bk; +0x08/+0x0c the nextsize pair.

## Use

Every "write user+8" recipe is the key field; "user+0" is the fd —
know the offset you're writing.
