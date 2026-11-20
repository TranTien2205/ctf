# The join key — TargetLogonId vs LogonGuid

`TargetLogonId` joins 4634/4647/4672 and `SubjectLogonId` on 4688;
`LogonGuid` joins 4648 and 4964 when the Logon ID does not line up
(Microsoft Learn, 4624/4964). `0x3e7` is SYSTEM, not a user.

## Two keys

LogonId for session joins; LogonGuid for 4648/4964.

## The pair

0x0 linked = no split-token pair.
