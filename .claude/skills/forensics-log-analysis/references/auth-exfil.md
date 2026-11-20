# data exfil in a authentication log

**Log:** authentication log — `Mon DD HH:MM:SS host sshd[pid]: Accepted/Failed ... for USER from IP`.

**Question:** data exfil — large responses to one IP.

Bracket with `log_summary.py summary`, then distribute the relevant field, then window the hit. Quote the verbatim line.
