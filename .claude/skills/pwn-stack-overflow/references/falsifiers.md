# Falsifiers — the observations that close each route

| Route | Falsifier |
|---|---|
| The class itself | the read is bounded below the saved-state distance |
| ret2shellcode | NX on — nothing on the stack executes |
| ret2win | no function in the binary does what's needed |
| ret2plt | no useful import |
| ret2libc | no leak primitive → libc base hidden |
| canary bypass | no leak and no fork-brute channel |
| GOT overwrite | full RELRO — GOT read-only |
| offset measurement | faulting register never holds pattern bytes |
| ret2csu | statically linked/stripped, no __libc_csu_init |
| SROP | no syscall;ret, or stack can't hold the frame |
| bit-flip chain | a needed byte in an address is a banned char |
| pie defeat | no leak, no partial-write trick |
| fork-brute | server execs per connection — new canary each |

## Class falsifier

The write is bounded by a length the input cannot influence AND that bound
is below the saved-state distance: no stack-corruption is possible. Note
that a STATIC binary can carry __stack_chk_fail even when built
-fno-stack-protector — confirm the canary from the %fs:0x28 load in the
disassembly, not the import.

## Using them

Check the cheapest falsifier before the chain: one probe usually answers
whether the route is open.
