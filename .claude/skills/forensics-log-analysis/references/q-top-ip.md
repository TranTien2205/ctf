# Question — the top talker

    awk '{print $1}' access.log | sort|uniq -c|sort -rn|head

One IP 10x the rest = the scanner/attacker. Then distribute ITS
paths/methods to see what it did.

## Follow-up

    grep '^1.2.3.4' access.log | awk '{print $7}' | sort|uniq -c|sort -rn

The top IP's path distribution shows the attack's path — the
scanned paths then the one that worked.
