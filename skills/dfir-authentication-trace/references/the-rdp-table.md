# RDP — the LSM event set

21 logon, 22 shell start, 23 logoff, 24 disconnect, 25 reconnect;
39 = disconnected BY another session (differing session ids = kicked
off), 40 = disconnect with `<Reason>`. 40 is NOT 'session created' —
the ctf-forensics row is wrong; use this table.

## The set

21-25, 39 by-another, 40 with Reason.
## Wrong row

40 = disconnect with Reason, not created.

## Kicked

39 differing ids = kicked off.
