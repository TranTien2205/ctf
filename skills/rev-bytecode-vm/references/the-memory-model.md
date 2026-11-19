# The VM's memory — where data lives

A VM's state: registers + stack + a memory array — the flag-check
reads input into memory, transforms, compares.

## The ops

- load_mem [addr]: read a memory byte.
- store_mem [addr]: write.
- load_input: read a flag byte into a register/memory.

## The extraction

The expected bytes may live in the VM's memory image — dump the
initialized memory region the program reads.
