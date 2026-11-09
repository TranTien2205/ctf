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

Echo channel check - and the one that settles the class: `probe_cmdi` sends
`id; echo <nonce>` (and `whoami & echo <nonce>`) across eight separator
families and reads the response rather than the clock. A finding needs the
identity line AND the nonce, both returned by the target; `argus proof rce`
prints the requirement.

The nonce matters for a specific reason: a parameter that merely REFLECTS
your payload puts the string `uid=` in the response with nothing executed.
The grading rejects an identity line that also appears in the request that
produced it, and `probe_cmdi` reports that case as "reflected, not executed".

Do NOT write a file to prove it. `; id > /var/www/html/x.txt` then fetching
it leaves an artifact on someone's server, needs a cleanup step that may
fail, and proves nothing the echo channel did not already prove. Output
alone satisfies the requirement, and a destructive or persistent payload in
the cited request voids the evidence outright - the rce spec vetoes it.

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

## When only the timing oracle holds

A delay is a candidate, not an rce finding: the class requires output. Say so
in the report, name the separator family that delayed, and record it as a
candidate rather than rounding it up - `probe_cmdi` does exactly this and
returns the blind results separately.

## Severity guide

Command output or write/read-back demonstrated: critical. Blind timing-only
command exec confirmed twice: critical (still RCE). Argv-injection without
command control: medium-high, describe the exact primitive.
