# Payload dictionary — the crypto_attack.py invocations

All attacks go through `tools/crypto_attack.py`. `list` prints every id with its
applicability bound. `<attack-id> --help` shows the exact flags for that attack —
flag names differ per id, so run `--help` before composing.

```bash
# the inventory + bounds
python3 tools/crypto_attack.py list

# single-modulus attacks
python3 tools/crypto_attack.py fermat          --n <n> [--max-iters <K>]
python3 tools/crypto_attack.py wiener          --n <n> --e <e>
python3 tools/crypto_attack.py boneh-durfee    --n <n> --e <e> [--delta <d>] [--m <m>] [--t <t>]
python3 tools/crypto_attack.py boneh-durfee-escalate --n <n> --e <e> [--m <m>] [--t <t>]
python3 tools/crypto_attack.py small-e-root    --n <n> --e <e> --c <c> [--max-k <K>]
python3 tools/crypto_attack.py pollard-pm1     --n <n> [--b <B>]
python3 tools/crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b> [--p-bits <pb>] [--m <m>] [--t <t>]
python3 tools/crypto_attack.py coppersmith-core --n <n> --a <a> --X <bound> [--m <m>] [--t <t>]

# multi-modulus / multi-message
python3 tools/crypto_attack.py batch-gcd       --moduli n1 n2 n3 ...   # or --file <path>
python3 tools/crypto_attack.py hastad          --pairs "n1,c1;n2,c2;n3,c3" --e <e>   # or --n/--c lists
python3 tools/crypto_attack.py common-modulus  --n <n> --e1 <e1> --c1 <c1> --e2 <e2> --c2 <c2>
python3 tools/crypto_attack.py crt             --residues "r1,r2,..." --moduli "p1,p2,..."

# terminal step
python3 tools/crypto_attack.py factor-from-d   --n <n> --e <e> [--d <d> | --phi <phi>]
python3 tools/crypto_attack.py rsa-decrypt     --n <n> --e <e> --c <c> --p <p> --q <q>
python3 tools/crypto_attack.py eth-root        --c <c> --e <e> --factors "<p>,<q>"
python3 tools/crypto_attack.py nth-root        --x <x> --n <n>
```

**Note:** `crypto_attack.py` does not implement `franklin-reiter`, a Bellcore
`sig`/`sig-faulty` split, or a `dp`/`dq`/`qInv` recovery — those are manual
techniques (see `franklin-reiter.md` / `crt.md`), run as a short Python script
over `sympy`/`gcd`, not a tool subcommand. A `d`-recovery is handled by
`factor-from-d` (it emits `p`,`q`), then `rsa-decrypt --p --q` — `rsa-decrypt`
takes the factors, not `--d`.
