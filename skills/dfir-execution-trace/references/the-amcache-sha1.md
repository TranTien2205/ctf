# Amcache FileId — SHA-1 + four zeroes

`FileId` is SHA-1 with `0000` prefixed (strip it for 40 hex), computed
over only the first 31,457,280 bytes — a bigger file's FileId never
matches a hash you compute. Presence, not execution.

## 31MB cap

Presence + capped SHA-1 — never execution.

## Strip

0000 prefix for the 40-hex SHA-1.
