# The stub call — how a PLT call works


call plt[x]: the stub jmp's through got[x] to the resolved function —
the call reaches the real function; the chain sees the function's
behavior.
