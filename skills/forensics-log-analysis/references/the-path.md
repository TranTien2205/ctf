# The path field — what was requested

    awk '{print $7}' access.log | sort|uniq -c|sort -rn|head|tail

The head shows the heavy paths; the tail shows the one-off hits —
the flag path or the exploit request is usually a one-off.

## Reading the tail

    awk '{print $7}' access.log | sort|uniq -c|sort -n|head -30

Ascending count — the paths hit exactly once. A GET /flag.txt, a
?cmd=, a traversal — the exploit is almost always a singleton.
Cross-check the one-off paths' status codes.
