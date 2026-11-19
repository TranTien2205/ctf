# End to end — the digest+patch


md5(input)==stored, no preimage:

1. Patch the jz at the check → the yes-branch runs.
2. The flag's decrypt needs the real input — but the patch let the
   SUCCESS-PATH run; if the flag's computed FROM the input, the
   patch alone doesn't produce it — the input must be real.
3. The input's source: a bruteable charset × the digest — an
   offline brute.
