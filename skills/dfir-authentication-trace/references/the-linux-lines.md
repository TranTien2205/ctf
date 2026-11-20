# Linux — the line shapes (OpenSSH auth.c)

`Accepted password for U from IP port P ssh2` (the second + source);
`Accepted publickey ... ssh2: RSA SHA256:<b64>` (the key);
`Failed password for invalid user X` = account absent (the 064
analogue); `pam_unix session opened`; `systemd-logind New/Removed
session N`; `sudo: U : ... COMMAND=` with the target account.

## The shapes

Accepted/Failed/Invalid-user/pam/logind/sudo/useradd.

## The format

auth.c format strings name the fields.
