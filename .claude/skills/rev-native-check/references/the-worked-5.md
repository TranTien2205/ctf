# Worked example — the digest dead-end


1. The compare is sha256(input) == stored_digest — can't invert.
2. Patch the jz → accept anything — but the flag needs the real
   input (the digest seeds a decryption).
3. Find the input's source: a hint, a small space to brute, a
   supplied list — or report the falsifier.
