# The heap header — heap_info on thread arenas


Non-main arenas start with heap_info (ar_ptr, prev, size, mprotect_size,
pagesize_) — a fake heap_info is the house-of-mind anchor.

## Layout (x64)

    heap_info: | ar_ptr | prev | size | mprotect_size | pagesize[6] |

## Use

Corrupting a chunk's N bit routes free() through heap_info_for() —
which computes the arena from the chunk address — aiming it at your
fake heap_info.

## Falsifier

No controllable region can host a plausible heap_info: mind is closed.
