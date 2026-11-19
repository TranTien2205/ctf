# The xor build — the obfuscated constant


`mov eax, 0xXX; xor eax, 0xYY`-style builds decode a constant — the
decoded value is what to extract; compute it in Python.
