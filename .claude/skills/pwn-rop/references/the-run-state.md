# The run state — what the exploit knows


Between stages the script holds: the bases (binary/libc/heap/stack
leaked so far), the computed addresses, the stage's number — the
exploit is a state machine.
