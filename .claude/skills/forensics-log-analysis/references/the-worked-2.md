# Worked — brute-force then success

1. auth.log: many "Failed password" from one IP.
2. Then "Accepted password for X from that-IP" — the compromise.
3. The accepted line + its timestamp is the finding.

## Notes

- The Failed→Accepted transition for one IP is the whole finding —
  count the failures, name the accepted user.
- `invalid user` failures are username probing; valid-user
  failures are real password guessing — the distinction matters.
- The timestamp is the answer to "when did they get in".
