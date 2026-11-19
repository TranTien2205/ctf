# POODLE and the legacy TLS padding family — map

| Variant | Pad semantics | Oracle answer |
|---|---|---|
| PKCS#7 (app-layer) | last N bytes = N | strict — full Vaudenay |
| SSL3 POODLE | last byte = pad len only | weaker — needs block shifting |
| TLS1.0 explicit IV | first block is IV | treat IV as C_{i-1} |
| Lucky13 timing | pad check timing differs | timing-channel variant |

Expanded rows and abort conditions: `poodle-and-legacy.md` and `poodle-and-legacy-deep.md`.
