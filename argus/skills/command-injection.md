# OS command injection

**When:** request data reaches a shell. Signals: params named `host`, `ip`,
`cmd`, `ping`, `domain`, `file`, `dir`; diagnostic utilities (ping/traceroute/
whois/dns lookup features); filename handling by backends that shell out.

## Detect - blind channels first

Direct output injection is rare; time and error oracles are the norm.

Separators to try (each with `sleep 4` / `timeout 4`):
`;` · `|` · `||` · `&` · `&&` · `` ` `` · `$()` · newline `%0a`

`probe_time` already covers `; sleep N`, `|sleep N`, `$(sleep N)` with a
measured baseline - a response delayed by ~N seconds beyond baseline is the
confirming signal, repeatable.

Echo channel check: `; echo ARGUS` or `; id` - look for `uid=` or the marker
in output. Writes: `; id > /var/www/html/x.txt` then GET it (cleanup after).

## Context shapes

- Inside quotes: you may need `"` or `'` first: `"; id #"`
- Inside command substitution already: close it `\`); id #\``
- Argument position (no shell): separators fail but extra flags may work -
  e.g. `host=--help` behavior change tells you it's argv injection instead.

## Filter bypasses

- Space filters: `${IFS}`, `$IFS$9`, `{cmd,arg}` brace expansion, `%09` tab
- Keyword filters: `s''leep`, `sl""eep`, `s\leep`, `s$@leep`, wildcards `/bin/s?eep`
- Encoding: base64 then `` `echo <b64>|base64 -d` ``, hex on some shells

## Falsifier

Every separator family produces identical responses and no timing oracle
holds after a repeat measurement.

## Severity guide

Command output or write/read-back demonstrated: critical. Blind timing-only
command exec confirmed twice: critical (still RCE). Argv-injection without
command control: medium-high, describe the exact primitive.
