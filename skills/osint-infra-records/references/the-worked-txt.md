# Worked — the flag in TXT

1. `--type TXT` → a planted string `flag{...}`.
2. Quote the verbatim answer.
TXT is always the first query — it's where flags live.

## Notes

- A domain can hold several TXT records — read all of them.
- The planted string may be the flag verbatim or encoded (base64).
- SPF (`v=spf1`) is normal; a non-SPF TXT string is the candidate.

## The confirm

The planted TXT is the answer — quote it verbatim. If it is base64/hex, decode it; a CTF TXT is usually the flag directly.

## Several TXT

A domain can hold many TXT records — a planted one sits beside real SPF tokens; read every record string.

## The finding

The planted TXT is the flag itself — the answer is read, not derived.
