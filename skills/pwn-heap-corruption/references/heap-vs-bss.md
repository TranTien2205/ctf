# Heap vs BSS — where the pointers live


The pointer ARRAY is usually in .bss (fixed address, non-PIE) — the
objects are on the heap (ASLR'd): the table is reachable even when the
heap isn't.

## Exploitation

- A fixed .bss slot is a deterministic write target — aim there
  without a leak (non-PIE).
- The array's entries point INTO the heap — reading them is a heap
  leak the program gives for free (a show-the-pointer op).

## Falsifier

PIE on and no base leak: even .bss moves — the table isn't fixed
either.
