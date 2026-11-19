# tools/pad_oracle.py — CBC padding-oracle driver — case catalogue

HTTP driver for Vaudenay: feeds each candidate byte to the oracle URL, tracks the validity distinguisher, and prints the recovered plaintext.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | --ct = hex ciphertext incl. IV | the captured target | byte chain to decrypt |
| 2 | --url has {CT} or {CTQ} | hex or url-quoted hex injection | match the endpoint's encoding |
| 3 | --ok-status/--ok-regex = the 'pad ok' answer | the distinguisher | measured BEFORE running |
| 4 | --max-requests bounds the loop | rate-limit safety | sized to the target |

## Falsifier

Falsifier — the distinguisher never fires (all requests look the same): the oracle doesn't exist, or the regex/status is wrong. Re-verify the distinguisher on a hand-crafted pad before blaming the tool.

## Coverage notes

- The IV is part of --ct — omitting it shifts every block by one and the attack silently fails.
- A regex that matches the ERROR page instead of the OK page inverts the loop — check which answer you're keying on.
- --max-requests too low aborts mid-byte; too high can burn the rate limit permanently.

## Cross-references

`cbc-padding-oracle.md` · `response-distinguishers.md`
