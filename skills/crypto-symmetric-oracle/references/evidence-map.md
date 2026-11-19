# Evidence discipline for oracle challenges — map

| Stage | Evidence | post-probe kind |
|---|---|---|
| ECB fingerprint | two identical ciphertext blocks from repeated input | class |
| Padding-vs-MAC split | both responses verbatim | class |
| Nonce reuse | the two captured records with the same nonce | class |
| Forged tag accepted | the verify response | impact |
| Flag in response | the live response bytes | flag via pre-flag |

Expanded rows and abort conditions: `evidence.md` and `evidence-deep.md`.
