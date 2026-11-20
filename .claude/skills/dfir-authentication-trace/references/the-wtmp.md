# wtmp/btmp — the binary trio

384-byte utmp records; `ut_type` 7 USER_PROCESS (login), 8
DEAD_PROCESS (logout), 2 BOOT_TIME. `wtmp_parse.py` decodes to JSON;
`--lastlog` reads the 292-byte uid-indexed lastlog. btmp counts
attempts — `ut_host` is the source; lastlog keeps only the newest
per uid, sparse is normal.

## The trio

utmp now, wtmp history, btmp fails, lastlog newest.

## 384 bytes

ut_type 7/8 the login/logout pair.
