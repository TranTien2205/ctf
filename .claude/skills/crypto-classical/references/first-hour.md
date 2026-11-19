# First hour — the reads, the output, the budget

## The reads

- `cipher_id.py --text 'CT'` — IC/chi²/Kasiski/frequency/verdict.
- The charset — cipher vs encoding.
- A cipher name in the text → the decoder.
- The format positions `flag{`/`CTF{`.
- `classical_solve <family> --text` — the family + flags.
- The plaintext read — language or `flag{...}`.

## The output

A family, a `k`/`L`/`σ`/depth/key — and the plaintext.

## The falsifier-first rule

Read the bound before solving — no `k`/`L`/language → the family closes.

## The budget

`decide.py` — 5 probes/15 min per class, 25/45 per challenge. The statistics
are one read; the solve is one probe.

## The record

`post-probe` on a confirm/falsify; `../field-notes.md` after.
