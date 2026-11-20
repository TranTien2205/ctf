# The traps

- LogonType 3 called RDP.
- A 4672 read as an admin logon (it is a privilege assignment).
- `0x18` looked for on 4768 (it lives on 4771).
- btmp read as distinct sources (it counts attempts).
- lastlog's sparse file read as tampering (it keeps newest only).

- hayabusa LOCAL default, chainsaw UTC.
- An empty 4688 command line = auditing off, not nothing.
