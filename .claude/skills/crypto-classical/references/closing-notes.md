# Closing notes — crypto-classical, one paragraph

A classical cipher on a letter-only `ct`, no key. `cipher_id.py --text` gives
the statistics — IC ~0.066 → monoalphabetic (caesar/subst), ~0.038 →
polyalphabetic (vigenere), letters preserved → transposition (railfence/
columnar). `classical_solve.py {caesar,vigenere,subst,atbash,railfence} --text`
solves; `enc_detect.py` handles the encoding boundary. Language out +
`enc(pt)=ct` is the verify. **Catalogue** — `../field-notes.md` for real solves.
