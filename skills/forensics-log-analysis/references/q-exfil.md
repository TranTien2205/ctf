# Question — data exfil

Sort by response size or count large responses to one IP — a
single IP pulling big responses over a window is the exfil shape.

## The command

    awk '{print $1,$10}' access.log | sort|uniq -c|sort -rn|head

Or sum response sizes per IP — the IP with an outsized byte total
is the exfil destination.
