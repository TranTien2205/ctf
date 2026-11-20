# The rotated-read method

    ls -la /var/log/auth.log*
    zgrep -i 'Accepted' auth.log.*.gz

Compressed archives hold the earlier window — the brute-force may
sit in .gz while the success sits in the live file.
