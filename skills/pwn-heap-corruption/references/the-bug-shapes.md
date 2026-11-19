# The five heap bug shapes — taxonomy


1. UAF — a pointer survives free(); the most common.
2. Double-free — free() called twice on one chunk.
3. Heap overflow — a write crosses the chunk boundary into metadata.
4. OOB index — an object-array index escapes the array.
5. Uninitialized use — a "new" object read before its fields are set
   (stale bin data shows through).

Each shape maps to a different first technique — the taxonomy entry is
the primitive, not the symptom.
