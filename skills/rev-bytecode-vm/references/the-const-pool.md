# The constant pool — indexed constants

Some VMs index constants by operand — `push_const N` loads
const_pool[N]. The pool is a separate array from the program.

## The recovery

- Find the const pool array (a byte/word array the handler indexes).
- `push_const 3` → const_pool[3] — resolve each reference.

## The flag angle

The expected bytes often sit IN the const pool — `push_const` of
each index yields the comparison targets.
