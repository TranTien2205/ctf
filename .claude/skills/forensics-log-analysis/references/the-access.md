# access.log — the web request log

Common/combined format: IP - - [time] "METHOD path HTTP/ver" status
size "referer" "UA". Fields: $1 IP, $4 time, $6-7 method+path,
$9 status, $11+ UA. The path distribution + status anomalies are
the meat.

## The quoted-string caveat

The referer and UA fields are quoted and can contain spaces — a
naive awk '{print $N}' splits inside them. For those fields use a
regex cut (or log_summary's field --regex) instead of positional
awk.

## Common questions

- Top IP / scanner: the $1 distribution.
- The odd path: the $7 distribution's tail.
- The tool: the UA field.
- The success-after-failures: $9 transitions for one IP.
