# The duration answer — session record, not auth line

Brutus: `Accepted` 06:32:44 vs wtmp `ut_type` 7 at 06:32:45 —
`Removed session` 06:37:24 - 06:32:45 = 279. Take the start from the
SESSION record, not the authentication line. Windows: 4624
`TargetLogonId` to its 4634, `SystemTime` delta.

## The start

Session record, not the auth line — 279 not 280.

## The record

ut_type 7 start, 8 end — not the Accepted second.
