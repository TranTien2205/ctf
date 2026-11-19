# CBC IV prediction — the BEAST-shaped case — map

| Need | Check |
|---|---|
| You see IV_next before choosing plaintext | the protocol emits it |
| You can submit chosen plaintext blocks | an encrypt oracle |
| Byte-boundary control | prefix alignment as in ECB |

Expanded rows and abort conditions: `cbc-iv-prediction.md` and `cbc-iv-prediction-deep.md`.
