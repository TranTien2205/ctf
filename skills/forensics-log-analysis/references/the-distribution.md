# Distribution before lines — the outlier method

    awk '{print $1}' access.log | sort | uniq -c | sort -rn | head

The count distribution of a field (source IP, status, path, UA)
surfaces the anomaly — one IP with 5000 hits among 50s, one 404
on an odd path. Field order matters — get the column right for
the log's format.

## Both tails matter

- `sort -rn | head` — the top outlier (the scanner, the brute-force).
- `sort -n | head` — the one-off tail (the flag path, the exploit
  request hit exactly once).
Check both ends of the distribution, not just the top.
