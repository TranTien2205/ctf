# Per-probe map — the canonical probes and what each proves — checklist

| Probe | Request(s) | Proves |
|---|---|---|
| Replay | same input ×2 | deterministic vs per-request IV |
| Length-step | input k vs k+1 | block vs stream, block size |
| Repetition | 'A'*48 | ECB fingerprint |
| Corruption-A | flip byte in C_{i-1} | does a pad-ish error appear |
| Corruption-B | keep pad valid, break MAC | the second answer → oracle exists |
| Tag-tamper | corrupt the tag field | tag verified? before decrypt? |
| Nonce-diff | collect two records | nonce reuse present |
| Prefix-map | vary each input field | which ct block holds which field |
| Alignment-pad | 'A'*k sweep | fixed prefix length mod block |
| Secret-length | grow input, watch plateaus | hidden suffix length |
| Rate measure | N requests timed | loop feasibility |
| Timing-pair | 50+ samples ×2 conditions | timing channel exists |
| Truncation | tag prefixes len 1..16 | minimum accepted tag |
| Encoding-peel | decode ct hex→b64→raw | what's actually encrypted |
| Verify-shape | valid vs invalid tag | verify oracle exists |

## Checklist

- [ ] check: Replay
- [ ] check: Length-step
- [ ] check: Repetition
- [ ] check: Corruption-A
- [ ] check: Corruption-B
- [ ] check: Tag-tamper
- [ ] check: Nonce-diff
- [ ] check: Prefix-map
- [ ] check: Alignment-pad
- [ ] check: Secret-length
- [ ] check: Rate measure
- [ ] check: Timing-pair
- [ ] check: Truncation
- [ ] check: Encoding-peel
- [ ] check: Verify-shape

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
