# Emulation — running the check in isolation


angr/unicorn are absent here — emulate by extraction: lift the check
function's logic to Python directly (the replicate route), or run the
real binary with controlled input under r2 -d.

## The boundary

Heavy VM-style obfuscation may need a real emulator — document the
limit.
