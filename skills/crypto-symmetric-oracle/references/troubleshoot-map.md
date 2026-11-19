# Troubleshooting — symptom → cause → fix — map

| Symptom | Likely cause | Fix |
|---|---|---|
| ecb_oracle recovers garbage after byte ~10 | wrong --resp decoding | try hex/b64/raw; verify one known byte |
| No identical blocks with 'A'*48 | fixed prefix offset | pad to alignment; check duplicate at ANY offset |
| pad_oracle accepts everything | regex matches error page | --ok-regex must match the OK answer, not the failure |
| pad_oracle decrypts wrong byte at position 0 | \\x01 false positive | re-probe with byte[14] modified |
| crib-drag finds nothing | different nonces, or compressed plaintext | verify nonce equality; check for gzip magic in ct |
| length-extension forge rejected | wrong --secret-len or HMAC | iterate secret-len; confirm raw-hash construction |
| gcm_nonce produces no H | records not actually nonce-shared | print both nonces; check AAD flags |
| forged token parses but no privilege | forged the wrong field | map which field carries the privilege |
| token rejected as malformed | pad bytes stripped by transport | submit hex/raw body, not a form field |
| loop dies at request ~2000 | rate limit or --max-requests | measure accepted rate; raise bound within limit |
| same input, different ct each time | per-request IV, not ECB | replay test already told you; don't force ECB |
| timing oracle reads noise | too few samples, loaded host | 50+ samples, quiet measurement, median not mean |

Expanded rows and abort conditions: `troubleshoot.md` and `troubleshoot-deep.md`.
