# Error Analysis — what each failure tells you

## The status-code table

| Status | Means |
|---|---|
| 200 + `uid=` output | confirmed exec — record |
| 200, marker reflected literal | no eval reached it — quoting? argv? |
| 200, nothing reflected | blind path — timing/OOB |
| 302/303 | post-probe redirect — flag elsewhere |
| 400 | parser rejected the input — quoting/encoding issue |
| 403 | WAF/filter reject — `waf-bypass.md` |
| 500 | server-side error — often means the input DID reach an evaluator that then errored |
| 503/504 | timeout/upstream — possible blind-exec? verify with short probe |

## The error-message table — which layer rejected it

| Error text | Layer |
|---|---|
| `sh: 1: x;id: not found` | shell ran — the whole arg was argv (no split) — arg-injection |
| `sh: -c: line 0: syntax error` | shell DID parse — quoting broken |
| `Command failed: ping x;id` | node `exec` error — err.stderr has it |
| `ParseError`/`SyntaxError` php | eval reached, php rejected |
| `invalid syntax` python | python eval reached |
| `SyntaxError` node | node eval reached |
| `Mod_Security`/`Blocked`/`406` | WAF |
| `Illegal characters`/`invalid input` | app filter |
| `could not resolve` | ping tried the arg as hostname — argv |

## The "the command ran but errored" shape — error-channel

`system()`/`exec()`/`sh -c` write errors to stderr — some apps bubble
stderr into the response. `x;$(cat /flag)` → `flag{...}: command not
found` — the error IS the read — `blind-cmdi.md`'s error channel.

## The `errno`/`exit-code` leak — status-of-the-child

- `Command failed: ping x — exited 1` — exit code in the error
- `child_process` errors include `err.code`/`signal`/`stderr`
- the exit code is a 1-bit channel — `data-exfil-channels.md`

## The "marker reflected but not executed" — what it means

`x;id` shown literally in response → the value never reached a shell —
the input is printed/escaped — either:

- the sink is argv-form (`execFile`)
- the value is HTML-escaped before display (`;id` shown as `;id`)
- the value is sanitized before exec (strips `;`)

Distinguish: send `x` alone — does it reflect? Then send `x;` — does the
`;` survive? The surviving-subset map decides which bypass.

## The "everything 500s" — evaluator that's too eager

An `eval()`/`exec()` sink that 500s on garbage input is CONFIRMED —
it's evaluating — send `7*7`/`1+1`/`id` to find which evaluator —
`eval-injection.md`.

## The `sh: ping: not found` — the tool itself missing

The wrapped binary (`ping`/`convert`/`dig`) isn't installed — the shell
IS reachable (the error proves sh parsed it) but the fixed command
fails — the injection is LIVE, the fixed binary is the missing piece.
`x;id` still works — the injection runs your command, not `ping`.

## The `invalid hostname`/`name or service not known` — DNS error

The value went to `nslookup`/`host`/`dig` as a HOSTNAME — the tool ran
but the value wasn't a valid name — `x;id` would have been parsed by sh
first anyway; if the error shows the WHOLE `x;id` as one arg — argv —
arg-injection.

## The "no output but `sleep` worked" — the timing channel

`sleep 5` delayed 5s but `id` showed nothing → exec confirmed blind →
OOB/file-write/error channel — `blind-cmdi.md`.

## Falsifiers

- the error names a layer that proves the value never reached a shell
  (e.g. `execFile ping` error) → class dead, arg-injection is the live
  class

## Output to record

- the verbatim error text + which layer it names
