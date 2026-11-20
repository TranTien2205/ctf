# syslog — the system message log

"Mon DD HH:MM:SS host daemon[pid]: message" — mixed services.
The daemon field splits it; grep the relevant service first.

## Splitting it

    awk '{print $5}' syslog | sed 's/\[.*//' | sort|uniq -c|sort -rn

The daemon/process distribution names which services logged; then
grep the daemon of interest (cron, sshd, sudo, kernel) and read
its message stream.

## What lives here

- cron entries — scheduled execution
- sudo entries — privilege use with the command
- kernel messages — module loads, OOM, netfilter
- User-added entries — a planted message (the flag may be one)
