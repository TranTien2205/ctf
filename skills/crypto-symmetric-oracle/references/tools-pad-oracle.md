# tools/pad_oracle.py — CBC padding-oracle driver

HTTP driver for Vaudenay: feeds each candidate byte to the oracle URL, tracks the validity distinguisher, and prints the recovered plaintext.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --ct = hex ciphertext incl. IV | the captured target | byte chain to decrypt |
| --url has {CT} or {CTQ} | hex or url-quoted hex injection | match the endpoint's encoding |
| --ok-status/--ok-regex = the 'pad ok' answer | the distinguisher | measured BEFORE running |
| --max-requests bounds the loop | rate-limit safety | sized to the target |

## Steps

1. python3 tools/pad_oracle.py --selftest to prove the driver.
2. Capture the target ciphertext as hex INCLUDING the IV (usually the first block).
3. Identify the oracle URL template: {CT} where the ciphertext goes, {CTQ} if it must be percent-encoded.
4. Identify the 'padding ok' answer — a status (--ok-status) or body regex (--ok-regex). Measure it on known good vs bad pads first.
5. Run: python3 tools/pad_oracle.py --ct <hex> --url 'https://t/d?c={CT}' --ok-regex 'OK'.

## Falsifier

Falsifier — the distinguisher never fires (all requests look the same): the oracle doesn't exist, or the regex/status is wrong. Re-verify the distinguisher on a hand-crafted pad before blaming the tool.

## Traps

- The IV is part of --ct — omitting it shifts every block by one and the attack silently fails.
- A regex that matches the ERROR page instead of the OK page inverts the loop — check which answer you're keying on.
- --max-requests too low aborts mid-byte; too high can burn the rate limit permanently.

## Commands

```bash
python3 tools/pad_oracle.py --selftest
python3 tools/pad_oracle.py --ct <h> --url 'https://t/d?c={CT}' --ok-regex 'OK'
```

## Cross-references

`cbc-padding-oracle.md` · `response-distinguishers.md`
