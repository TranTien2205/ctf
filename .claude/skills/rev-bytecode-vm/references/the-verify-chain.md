# The verification chain — candidate → flag

1. co_consts / the program holds a flag-shaped constant — a
   CANDIDATE.
2. Verify it's the accepted input: run the interpreter on it.
3. Accepted → candidate → flag via hooks.py pre-flag.

Never skip step 2 — a constant is a guess until the program accepts
it.
