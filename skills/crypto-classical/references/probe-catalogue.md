# Probe catalogue — the reads → the output

## The identify reads

| Read | Output |
|---|---|
| `cipher_id --text` | IC/chi²/Kasiski/frequency/verdict |
| the charset | cipher vs encoding |
| a name | the decoder |

## The solve reads

| Read | Output |
|---|---|
| `classical_solve caesar --text` | the 25 `k` ranked |
| `classical_solve atbash --text` | the reflection |
| `classical_solve vigenere --text` | `L` + the key |
| `classical_solve subst --text` | the `σ` |
| `classical_solve railfence --text` | the depths |

## The verify reads

| Read | Output |
|---|---|
| the plaintext | language or `flag{...}` |
| `enc(pt)==ct` | the transform confirmed |
