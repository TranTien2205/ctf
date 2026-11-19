# tools/pad_oracle.py — CBC padding-oracle driver — operational checklist

HTTP driver for Vaudenay: feeds each candidate byte to the oracle URL, tracks the validity distinguisher, and prints the recovered plaintext.

## Checklist

- [ ] python3 tools/pad_oracle.py --selftest to prove the driver.
- [ ] Capture the target ciphertext as hex INCLUDING the IV (usually the first block).
- [ ] Identify the oracle URL template: {CT} where the ciphertext goes, {CTQ} if it must be percent-encoded.
- [ ] Identify the 'padding ok' answer — a status (--ok-status) or body regex (--ok-regex). Measure it on known good vs bad pads first.
- [ ] Run: python3 tools/pad_oracle.py --ct <hex> --url 'https://t/d?c={CT}' --ok-regex 'OK'.

## Abort conditions

- The IV is part of --ct — omitting it shifts every block by one and the attack silently fails.
- A regex that matches the ERROR page instead of the OK page inverts the loop — check which answer you're keying on.
- --max-requests too low aborts mid-byte; too high can burn the rate limit permanently.

## Falsifier

Falsifier — the distinguisher never fires (all requests look the same): the oracle doesn't exist, or the regex/status is wrong. Re-verify the distinguisher on a hand-crafted pad before blaming the tool.

## Cross-references

`cbc-padding-oracle.md` · `response-distinguishers.md`
