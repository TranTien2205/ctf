# The status-code field — the anomaly surface

    awk '{print $9}' access.log | sort|uniq -c|sort -rn

A single 200 on an odd path, a burst of 404s (scanning), a 500
(error-exploitation trail) — the status distribution names them.

## Reading it

- A 404 burst from one IP = a scanner.
- A 200 among 4xx/5xx = the request that worked.
- A 500 cluster = where the exploit caused an error.
- A 301/302 = a redirect (open-redirect or a moved flag path).
Pair the status with the IP and path fields for the full story.
