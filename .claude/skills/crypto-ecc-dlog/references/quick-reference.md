# Quick reference — the one-screen card

```
GROUP:   p a b G n          (order = n, not p)
SIGS:    --sigs file.json   [{"r","s","z"} | [r,s,z]]

ATTACK                         COMMAND
r dup                        ecdsa-nonce-reuse --sigs f --order n
k bounded                    hnp-ecdsa --sigs f --order n --nonce-bits B
(t,u) pairs                  hnp --t f --u f --modulus n --bound B
ord smooth                   pohlig-hellman --g --h --p --order n
x bounded                    bsgs --g --h --p --order n
order ?                      smoothness --n n
#E == p                      tools/crypto/smart_attack.py
Δ == 0                       tools/crypto/singular_ec.py
unvalidated P                tools/crypto/ec.py (+ bsgs/pohlig, CRT)

COUNT:   hnp.required_signatures(order_bits, nonce_bits)
VERIFY:  x·G == Q  |  pow(g, x, p) == h
FLAG:    flag{...} | CTF{...}
RECORD:  post-probe + ../field-notes.md
```
