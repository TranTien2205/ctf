# Payload dictionary catalogue — the invocations, indexed

## The identify invocations

| Command | The output |
|---|---|
| `cipher_id.py --text 'CT'` | IC/chi²/Kasiski/freq/verdict |
| `cipher_id.py --selftest` | the offline self-test |
| `enc_detect 'CT'` | the encoding path |
| `enc_detect.py --selftest` | the encoding self-test |

## The `caesar`/`atbash` invocations

| Command | The output |
|---|---|
| `classical_solve caesar --text 'CT'` | the 25 `k` ranked |
| `classical_solve atbash --text 'CT'` | the reflection |

## The `vigenere` invocations

| Command | The output |
|---|---|
| `classical_solve vigenere --text 'CT'` | `L` + the key |
| `classical_solve vigenere --text 'CT' --keylen L` | the `L`-forced key |
| `classical_solve vigenere --text 'CT' --key WORD` | the `WORD`-decode |

## The `subst` invocations

| Command | The output |
|---|---|
| `classical_solve subst --text 'CT'` | the `σ` |
| `classical_solve subst --text 'CT' --restarts N --iters M` | a harder `σ` |

## The `railfence` invocation

| Command | The output |
|---|---|
| `classical_solve railfence --text 'CT'` | the depths ranked |

## The named others — not in the tool

`other-ciphers.md`,`playfair-polybius*.md` — a script / dcode.fr.

## The verify

`pt` language + `enc(pt)=ct`.
