# Heap evidence — what counts as a signal


## Stage signals

- leak: a printed value that is a heap/libc/stack address — verified
  by range (0x55/0x56, 0x7f, 0x7ff).
- overlap: marker written via object A read back via object B.
- write: the target slot's changed bytes (read-back or behavior).
- redirect: a call/return/free that fires your pointer.

## The proof standard

A flag read from the service counts only through the evidence hook:
`python3 tools/hooks.py pre-flag <chal> --value 'flag{...}' --source
response --evidence '<excerpt>'`.

## Falsifier discipline

An abort message is also evidence — it names the check that caught the
corruption. Record which check; that is the wall the technique must
clear.
