# Verified chains — honest status

This is a **catalogue class**: nothing in this toolkit has solved a
symmetric-oracle challenge yet. There are no verified chain cards to copy.

## What that means operationally

- Everything here is standard published knowledge (Vaudenay, cryptopals
  sets, classic CBC/ECB attacks), not local experience.
- The tools (`pad_oracle.py`, `ecb_oracle.py`, `gcm_nonce.py`,
  `parity_oracle.py`) have offline `--selftest` that proves the drivers —
  run the selftest before trusting the loop, because no solved challenge
  here has run them against a live target.
- When you DO solve one, the solve writes the first chain card — the class
  then becomes verified and this file gets replaced.

## What a solve must record to make a card

- The oracle shape (which of the four).
- The distinguisher (status/body/timing and the exact two answers).
- The attack file used.
- The request count and rate for the loop.
- The flag's pre-flag evidence.

## Standing borrow

`tools/chain_match.py` returns nothing for this class today — the corpus
itself is the card. Route by `detection.md`, not by recall.
