# Worked example: url-web

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: supplied http://<target>:8080, nothing else.

1. python3 tools/web_probe.py http://<target>:8080
   -> status, headers, cookie, title. Header 'Server: Werkzeug/2.x'
   + session cookie shape => flask prior (stk-flask).
2. python3 tools/web/bundle_miner.py <url>
   -> /static/app.js -> endpoints: /api/login /api/items/<id>
   /api/export?url= .
3. python3 tools/web_enum.py <url>
   -> /robots.txt 200 'Disallow: /backup' -> pe-backupnames next.
4. stk-flask row: /console probed -> 404 (negative recorded).
5. Observation list emitted: stack=flask, endpoints(3),
   fetch-param url= on /api/export (surf-fetchparams),
   robots leak /backup.
6. classify.py '<the list>' -> ssrf candidate; chain_match
   -> a card for flask+fetch-param -> its first_confirming_probe.
## Pivot

Signal harvested -> out-*; route named -> that skill.
