# The arg sets — pop vs mov vs xor


Three ways to set a register:

- pop rX — the value is a chain qword.
- mov rX, rY — copies a register.
- xor rX, rX — zeroes it.

## The choice

pop for arbitrary values; xor for zero; mov for register-to-register
moves — pick by what's settable.
