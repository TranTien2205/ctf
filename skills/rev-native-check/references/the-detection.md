# Detecting the class — when this skill applies


The signature: a native binary reading input and printing a verdict —
a license check, a password gate, a flag validator.

## The boundary

- A script/bytecode input → rev-bytecode-vm.
- A managed binary (.NET/Java) → rev-managed-code.
- The input overflows/does something → a pwn class.
- No verdict at all → maybe a different class entirely.
