# Heap case studies — the shapes in the wild


## The menu service

add/delete/show/edit over a slot array — the canonical shape; every
op maps to an allocator op.

## The note system

Notes with content buffers — the classic UAF/overflow shape; the
content pointer is the confusion target.

## The C++ objects

Objects with vptr + string members — the vptr-confusion ending.

## The threaded server

Per-connection allocs — the arena/per-thread complications.

Each shape maps the same primitives onto different ops.
