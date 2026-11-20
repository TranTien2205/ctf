# The IP distribution — who hammered it

    awk '{print $1}' access.log | sort|uniq -c|sort -rn|head

One IP with thousands of hits among tens = the scanner/attacker.
The top IP's requests reconstruct the attack path.

## Following the top IP

    grep '^ATTACKER_IP' access.log | awk '{print $7}' | sort|uniq -c|sort -rn

What the top IP actually requested — the path distribution of its
requests shows the scan-then-hit path. A second IP at a lower count
can be a second actor — check both.
