# auth.log — the authentication log

"Mon DD HH:MM:SS host daemon[pid]: message". sshd entries: Accepted/
Failed password/publickey for user from IP. The brute-force shape:
many Failed from one IP then an Accepted — the pivot to name.

## The patterns

- `Failed password for invalid user X` — username probing.
- `Failed password for X` — valid-user password guessing.
- `Accepted publickey` — key auth (harder to brute-force).
- `Accepted password` — the credential worked.
- `Disconnecting` / `Connection closed` — the session end.

## The find

    grep 'Failed' auth.log | awk '{print $NF}' | sort|uniq -c|sort -rn

The IP owning the failures, then grep that IP + Accepted for the
compromise line.
