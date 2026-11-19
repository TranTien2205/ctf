# Scenarios deep — the challenge presentations, annotated

## The `.pem` + `.txt` pair

A public `.pem` (`n`,`e`) and a `.txt` with `c`. Read `RSA.importKey` → `n`
bits, `e`. The attack is single-modulus — `fermat`/`wiener`/`coppersmith`/
`small-e-root` by the other signals.

## The `keygen.py` + output

`keygen.py` (or `chal.py`) generates `n`,`e`,`c` — read it for the tell
(`next_prime`,`seed`,`getPrime(d)`,`e=3`,no pad,`m2=a·m1+b`,`dp`,`dq`,`qInv`,
`redact`). The tell routes the attack.

## The `.json` of keys/messages

`output.json`/`keys.json`/`messages.json` — a list of `n`/`c`/`e` objects.
`batch-gcd` (a shared `p`), `hastad` (a broadcast), or a leak in a field.

## The partial private key

`private.pem` redacted/`XXXX`/truncated — `dp`,`dq`,`qInv`,`d`,`phi`, or `p`/`q`
bits present → `crt`/`factor-from-d`/`coppersmith`/`rsa-decrypt`.

## The `.pcap`

A TLS handshake + a `c` — `tshark`/`scapy` extracts `n`,`e`,`c`, then the RSA
attack.

## The service (`nc`/`host`)

A live `nc` service that encrypts `m` on request or leaks `d`/`phi`/a `sig`
fault — the oracle is the leak; the attack is the same.

## The signed/faulty oracle

A `sig` oracle that returns a correct+faulty pair → `crt` Bellcore `gcd`.

## The verify

`pow(m,e,n)==c` / `p*q==n` — the artifact is the identity.
