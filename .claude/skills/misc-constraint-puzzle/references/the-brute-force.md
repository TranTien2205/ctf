# Brute-force rounds — bounded search

Nonce/hash rounds are a bounded loop: try x=0..N, check the
predicate, send x. The deadline bounds N; the loop is cheap in
Python for CTF-sized searches.
