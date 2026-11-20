# utmp field order — ut_id before ut_user

`utmpdump` prints type, pid, ut_id, ut_user, ut_line, ut_host — NOT
struct order; a parser following print order shifts every field.
UT_LINESIZE/UT_NAMESIZE 32, UT_HOSTSIZE 256.

## Struct order

Print order != struct order — ut_id precedes ut_user.

## Order

ut_id before ut_user in the struct.
