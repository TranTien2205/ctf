# escapeshellarg / escapeshellcmd / addslashes — what they do and what they leave

## The three functions — the actual behavior

| Call | What it does | What it leaves |
|---|---|---|
| `escapeshellarg($x)` | wraps `'`x`'` + escapes inner `'`→`'\''` | inner `'` killed, arg-form preserved |
| `escapeshellcmd($x)` | escapes `&#;`|\`?~<>^()[]{}$*\\\x0A\xFF` + `'`|"` inside pairs | many metas blocked but... |
| `addslashes($x)` | escapes `'` `"` `\` `\0` | NOTHING else — `;` `|` `&` live |

## `escapeshellarg` — the `'`-wrap that LOOKS safe

`system('ping '.escapeshellarg($x))` produces `ping 'x;id'` — the `;id`
is INSIDE the arg — safe against `;`-injection BUT:

### Attack 1 — the `-` flag position

`ping '-c4 x'` — the arg IS a flag — `argument-injection.md` —
`x=--param=value`/`x=-e`/`x=-T` — flags are INSIDE the quotes, immune
to the escaping.

### Attack 2 — the quoting-break via `'` (old/dodgy escapeshellarg)

PHP `escapeshellarg` pre-5.4.43/5.5.9 on some builds: `'` handled by
`'\''` — but on WINDOWS the function was *known-broken* —
`escapeshellarg` on Windows just double-escapes; the `'` isn't fully
protected → `'&calc&'` — the `&` runs cmd-side.

### Attack 3 — the second-argument concat bug

`system('ping '.escapeshellarg($host).' '.escapeshellarg($opt))` — if
`$opt` is user too and the developer forgets the wrap on one of them —
the unwrapped one is a raw separator.

### Attack 4 — the `%`-format/`$( )`-in-arg games

`'x'` is literal — but what the COMMAND does with `'x'`:

- `ping 'x'` — `x` is the hostname arg — the SHELL won't split it but
  `ping` will still parse `x` as hostname — arg-injection to ping's flags
- `tar xf 'x'` — `x` is the archive name — `phar://`/`expect://`/`php://`
  stream-scheme args — the `phar://`/`expect://`/`php://` family
- `curl 'x'` — `x` is the URL — `file://`/`gopher://`/`dict://`

## `escapeshellcmd` — the meta-stripper that's incomplete

Escapes `&#;`|\`?~<>^()[]{}$*\\\x0A\xFF` — but NOT:

- ` ` — space — so `x -e` still arg-injects
- `-` — flag chars
- `=` — `x=y` env-assign style in some shells
- `%` — env-var / cmd-arg
- `!` — history (interactive-only anyway)
- `/` — path
- `.` — hidden-file

AND it leaves *unescaped* `'` and `"` inside correctly-paired quotes —
so `'a;id'` inside a `''` context... the pairing rule: `escapeshellcmd`
only escapes a `'`/`"` if it's UNPAIRED. A paired `'a'`/`"b"` survives
UNESCAPED — the quoted substring is preserved → content inside can
still carry metas if they're inside the pair?

NO — the metas inside the pair are still escaped when they appear in
the list. The real gap is: `x 'y' z` — the `'y'` stays quoted — and
the developer might concatenate `'ping '.escapeshellcmd($x)` where
`$x="a'b'"` — the `'b'` becomes a quoting boundary → `ping a'b'` — the
`b` outside its own quote? The pairing is fragile — `escapeshellcmd`
is NOT the same guarantee as `escapeshellarg`.

## `addslashes` — barely a sanitizer

`'` `"` `\` `\0` → `\'` `\"` `\\` `\x00`. Everything else passes:

`x;id` → `x;id` — `;` unescaped — the injection lives fully.

## `escapeshellarg`'s *documented* weakness — the quoting IS the attack

From the man page: it "should only be used to escape INDIVIDUAL
arguments to shell functions" — when the developer does
`system('ping '.escapeshellarg($x).' '.escapeshellarg($y))` — each arg
IS wrapped — but the SEQUENCE of two `'...'` args can still be
manipulated if `x`/`y` carry `'` tricks in old PHP. The reliable
attack remains flag-position.

## The real escape — `escapeshellarg` + arg-injection

```php
system('dig '.escapeshellarg($name))
// send: name = -f/etc/passwd  OR  name = @server  OR  name = x.example.com
```

The `'`x`'` wrap preserves `x` as one arg — but that arg can BE a flag
— `-f`/`@`/`+options`/`--xxx` — `argument-injection.md`'s flag list is
the real attack surface under `escapeshellarg`.

## PHP version notes

- PHP < 5.4.43/5.5.9/5.6.x — `escapeshellarg` had known edge cases
  (empty-string arg, multibyte, quoting on Windows)
- PHP < 7.2 — `escapeshellcmd` didn't escape `\x0A` — newline survived
- all versions: `escapeshellcmd` on paired `'`/`"` preserves the quote —
  pairing-boundary attacks

## The bypass check-list per call

```
escapeshellarg present?
  → send '-f/etc/passwd'  '-c id'  '--upload-pack=id'  '@server'
    → flag-injection only
escapeshellcmd present?
  → send the unblocked metas: -, =, %, /, ., !, spaces
    → arg-injection + flag-position
addslashes only?
  → `;id` `|id` `&id` — full metacharset lives
preg_filter stripping metas?
  → `char-restriction.md` — find what's left
```

## Falsifiers

- `escapeshellarg` + the arg can only be a value (no flags possible
  because the called binary doesn't take flags) → shell-cmdi is dead —
  flag-injection is the remaining surface

## Output to record

- which sanitizer + which bypass form passed through it
