# First hour variant — the 0→60 plan, compact

## 0–10 min — read + gates

- Params/sigs extracted; `r` deduped; `z` convention picked.
- `smoothness --n ord`; `Δ`; `#E`; `required_signatures`; validation probe.

## 10–25 min — solve

`payload-dictionary*` command for the chosen attack. `--sigs` file ready.

## 25–35 min — verify + flag

`x·G == Q`/`pow(g,x,p) == h` → decrypt/forge → `flag{`.

## 35–50 min — record

`post-probe` verbatim → `../field-notes.md` → `classify_solve`/`attempts`.

## 50–60 min — stuck path

`troubleshoot*` → `falsifiers*` → `decide.py` rungs.

## The budget

5/15 per mechanism · 25/45 total — the controller enforces.
