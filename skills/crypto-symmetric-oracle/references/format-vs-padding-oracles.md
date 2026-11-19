# Format oracles vs padding oracles

A 'padding oracle' is really a DECODE oracle: the check can be on any format,
not just PKCS#7. CTF authors exploit the assumption.

## The variants

| Check | Oracle question | Attack shape |
|---|---|---|
| PKCS#7 pad bytes | does it end in valid pad? | classic Vaudenay |
| JSON parse | does it decrypt to parseable JSON? | per-byte guess via parse error |
| Length field | is the decoded length sane? | 1-bit format oracle |
| Character whitelist | is it printable/ASCII? | per-byte narrowing |
| Checksum inside plaintext | does the inner CRC match? | chosen-ct format oracle |
| Ciphertext-stealing / CTS | does it parse + re-encrypt? | variant of Vaudenay |

## The rule

The exploit loop is identical: (1) identify the check the service applies
to the decrypted plaintext, (2) find an input byte that flips the check's
answer, (3) brute-force the byte via the check. PKCS#7 is just the most
convenient check — any distinguishable decode outcome works.

## Detection

The service returns 'invalid format' vs 'valid' — not 'bad pad'. The loop
is the same; only the distinguisher's meaning changes.

## Falsifier

The decode check is all-or-nothing with no distinguishable sub-answers:
no oracle.
