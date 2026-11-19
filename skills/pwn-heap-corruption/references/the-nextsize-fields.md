# fd_nextsize/bk_nextsize — the largebin extras


Large-bin chunks carry extra links: fd_nextsize/bk_nextsize order the
size-sorted list — corrupting them is the large-bin write primitive.

## Layout (free large chunk)

    | prev_size | size | fd | bk | fd_nextsize | bk_nextsize |

## The write

Insert walks by size; `victim->bk_nextsize->fd_nextsize = victim`
writes the chunk address where bk_nextsize points — aim it at
target - 0x20 (x64).

## Falsifier

The insert path never walks the corrupted node (size ordering keeps
it off the path): the write never lands.
