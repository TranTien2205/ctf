# The sections — where things live


    readelf -S ./chal

- .text — the gadgets' home.
- .plt/.plt.got — the call stubs.
- .got/.got.plt — the resolution table (write target).
- .data/.bss — writable — the plant region.
- .rodata — strings.

## The addresses

Each section's address is fixed under non-PIE — the chain's targets.
