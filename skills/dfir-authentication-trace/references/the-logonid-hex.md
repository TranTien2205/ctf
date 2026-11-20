# Logon IDs are hex — normalize the case

`0x3E7` vs `0x3e7` — compare case-insensitively; SYSTEM is always
`0x3e7`, and `0x0` on TargetLinkedLogonId means no paired session.

## Normalize

Case-insensitive compare; 0x3e7 = SYSTEM, 0x0 = none.
## Hex

Normalize the case.
