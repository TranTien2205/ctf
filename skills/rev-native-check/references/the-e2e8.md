# End to end — the patch route


A digest check with no preimage path:

1. Patch the jz to jnz at the deciding compare.
2. Run — the yes-branch executes.
3. If the flag prints independent of the input: done.
4. If the flag needs the input: the patch wasn't enough — the
   preimage brute or the falsifier.
