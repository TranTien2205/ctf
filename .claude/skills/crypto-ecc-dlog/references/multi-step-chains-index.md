# Multi-step chains index — the composed attacks → the files

## The nonce chains → files

| Chain | Files |
|---|---|
| sigs→reuse→d→forge→flag | `multi-step-chains*.md`,`ecdsa-nonce-reuse-deep.md` |
| sigs→bias→lattice→d→forge→flag | `multi-step-chains*.md`,`hnp-*.md` |
| leak→(t,u)→hnp→d→flag | `multi-step-chains*.md`,`hnp-deep.md` |

## The dlog chains → files

| Chain | Files |
|---|---|
| `h`→smoothness→PH→x→use→flag | `multi-step-chains*.md`,`pohlig-hellman-deep.md` |
| `h`→bound→bsgs→x→use→flag | `multi-step-chains*.md`,`bsgs-deep.md` |
| `h`→DH→shared→decrypt→flag | `multi-step-chains*.md`,`scenarios*.md` |

## The defect chains → files

| Chain | Files |
|---|---|
| params→`#E`→smart→x→decrypt→flag | `multi-step-chains*.md`,`smart-attack-deep.md` |
| params→`Δ`→singular→x→decrypt→flag | `multi-step-chains*.md`,`singular-ec-deep.md` |
| oracle→fake curves→bsgs→CRT→d→flag | `multi-step-chains*.md`,`invalid-curve-deep.md` |

## The layered chains → files

| Chain | Files |
|---|---|
| crypto step→protocol step→flag | `multi-step-chains*.md` |
| class→impact boundary | `evidence*.md`,`multi-step-chains*.md` |
