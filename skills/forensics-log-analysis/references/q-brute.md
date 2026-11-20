# Question — a brute-force

auth.log: many "Failed password" from one IP, then an
"Accepted password for X from that-IP" — the success after the
failures is the compromise; its timestamp is the answer.

## The command

    grep 'Accepted' auth.log
    grep 'Failed' auth.log | awk '{print $NF}' | sort|uniq -c|sort -rn

The IP owning the failures, and the user the Accepted names —
together the brute-force result.
