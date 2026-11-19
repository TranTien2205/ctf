# Reading the delete op — clear or dangling


The delete op's implementation decides UAF: does it clear the stored
pointer after free? If not, the slot's pointer dangles — the class's
canonical entry.

## Check

- delete(i): free(ptr[i]); ptr[i]=NULL → clean, no UAF from this path.
- delete(i): free(ptr[i]); → ptr[i] dangles → UAF open.
- delete(i) missing bounds → OOB free of an arbitrary pointer.

## Falsifier

Every free path nulls and every access validates liveness: no dangling
reach — the class is closed at this interface.
