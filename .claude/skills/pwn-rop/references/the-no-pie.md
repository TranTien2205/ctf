# No PIE — the constant-address case


pie: false in the triage: every binary address is fixed — the pops,
the PLT stubs, /bin/sh-in-rodata if present — the chain is all
constants, no leak needed for binary addresses.

## The remaining leak

libc still needs one (ASLR is the OS's, not the binary's) — unless
the ending is a binary function or a syscall chain.
