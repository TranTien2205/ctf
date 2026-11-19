# Evidence map — the evidence type → the file / the rule

## The evidence types

| Type | The check | The file |
|---|---|---|
| plaintext recovery | `pow(m,e,n)==c` | `verify.md`,`verification-protocol.md` |
| factor recovery | `p*q==n`, `1<p<n` | `verify.md`,`evidence-rules.md` |
| `d` recovery | `pow(c,d,n)==m` | `evidence-deep.md` |
| `phi` consistency | `n-phi+1==p+q` | `evidence-rules.md` |
| the attack bound | the applicability line | `falsifiers.md`,`per-bound.md` |
| a negative | the falsifier observed | `negative-results.md`,`negative-map.md` |

## The rule

`pow(m,e,n)==c` for a plaintext; `p*q==n` for a factor. Both deterministic —
run them. A value that fails is a candidate; an attack that "ran" is not proof.

## The files

- `evidence-rules.md` — the standard.
- `evidence-deep.md` — the proof chain.
- `evidence-catalogue.md` — per-attack checks.
- `verify.md` + `verification-protocol.md` — the procedure.
- `falsifiers.md` + `falsifier-map.md` — the closing observations.
- `negative-results.md` + `negative-map.md` — the recorded dead ends.

## The hooks call

```bash
python3 tools/hooks.py post-probe --hypothesis-id <hN> --class crypto-rsa \
  --verdict confirms --evidence-kind impact \
  --evidence "pow(m,e,n)==c" --response "$(python3 -c 'print(pow(m,e,n)==c)')"
```
