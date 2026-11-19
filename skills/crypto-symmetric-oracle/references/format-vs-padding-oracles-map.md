# Format oracles vs padding oracles — map

| Check | Oracle question | Attack shape |
|---|---|---|
| PKCS#7 pad bytes | does it end in valid pad? | classic Vaudenay |
| JSON parse | does it decrypt to parseable JSON? | per-byte guess via parse error |
| Length field | is the decoded length sane? | 1-bit format oracle |
| Character whitelist | is it printable/ASCII? | per-byte narrowing |
| Checksum inside plaintext | does the inner CRC match? | chosen-ct format oracle |
| Ciphertext-stealing / CTS | does it parse + re-encrypt? | variant of Vaudenay |

Expanded rows and abort conditions: `format-vs-padding-oracles.md` and `format-vs-padding-oracles-deep.md`.
