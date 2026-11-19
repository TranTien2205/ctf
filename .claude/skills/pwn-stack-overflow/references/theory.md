# Theory — why each move works, one paragraph each

## Why the saved RIP is the prize

On function return, `ret` pops the top of stack into RIP. If your overflow
wrote there, execution continues at your address — total control in one
write.

## Why the canary exists

A random word before the saved frame, checked before return. Your write
must either avoid it (overwrite only what comes after), keep it (leak and
re-write its value), or exploit the fact that a forking server reuses it.

## Why NX forces ROP

Non-executable stack: the CPU won't execute data. So the payload is made
of existing code fragments ending in 'ret' — a chain, not injected code.

## Why PIE needs a leak

Position-Independent Executable: the binary's base is randomized. Every
static address is base+offset — one leaked pointer gives the base, and
then every address is computable.

## Why GOT is writable under partial RELRO

Lazy binding: GOT entries fill on first call, so the table stays writable
in partial RELRO. Write into a slot and the next call goes to your target.

## Why a bad byte kills silently

The read function terminates on its delimiter: fgets on \n, scanf %s on
whitespace, strcpy on \x00. A banned byte in your address/payload truncates
the input — the chain never reaches the saved state.
