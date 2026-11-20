# Rotated siblings — the earlier window

`*.log.1`, `*.log.2.gz` hold the earlier window — a single-file
baseline hides the anomaly in a file never read. zgrep/zcat the
rotated ones.

## The sweep

    ls -la /var/log/auth.log*
    zcat auth.log.2.gz | grep 'Accepted'
    zgrep 'Accepted' auth.log.*.gz

The brute-force may sit in .gz while the success sits in the live
file — only the sweep finds both halves.
