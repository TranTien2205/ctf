# Argument Order & getopt Quirks — position games inside argv

## The parsing model — getopt vs hand-rolled

`getopt()`/`getopt_long()` permute args — flags can come AFTER operands:
`tar cf x --checkpoint-action=y` reorders fine. Hand-rolled parsers may
stop at first non-flag arg (`--` or a positional) — position decides
whether your flag lands pre- or post-stop.

## `--` end-of-options — the boundary

```
cmd -- $INPUT        → INPUT can't be a flag — falsifier for flag-inject
cmd $INPUT           → INPUT can be a flag
cmd a $INPUT b       → INPUT between args — flag still parsed by getopt
```

`--` kills flag injection; `-` alone is just an arg.

## Trailing vs leading — which position accepts flags

`tar cf out.tar $input`:

- `input=/path` → tar archives /path (file read into tar!)
- `input=--checkpoint-action=exec=id` → flag parsed
- `input=-T /etc/passwd`? needs two slots — `-T` alone gets next arg as
  value — if the template is `tar cf out.tar $input /other/arg`, then
  `-T` consumes `/other/arg` as the list file — no exec but weird

## The "one arg, two effects" — flags that take a value in same token

`--opt=val`/`--opt val` — if you control one argv slot,
`--checkpoint-action=exec=id` works as ONE token (the `=` form).
Separated-form flags need two slots — usually out of reach unless args
are space-split.

## The repeated-flag last-wins — overrides

`-o a -o b` — most getopt tools use the LAST `-o`. If the app sets
`-o safe` and you inject another `-o path` — yours wins.

## Value-positional flags — stealing the next arg

Template: `tool -x $INPUT -o output`:

- `INPUT` as `--other` consumes `-o`? — no — `--other` is just a flag;
  but `INPUT=--other` where `--other` takes a value CONSUMES `-o` as its
  value → `output` becomes a positional — the parser reshuffles
- classic: inject a value-taking flag to eat the security-relevant next
  arg — e.g. `-T` eating `-o`'s slot

## The abbreviation trick — `--check` for `--checkpoint-action`

GNU getopt accepts unambiguous abbreviations: `--checkpoint-action` ←
`--check` if unique — shorter forms fit length caps.

## `-abc` bundling — short-option stacking

`-abc` = `-a -b -c` — if the tool accepts bundling, one argv slot can
carry three flags — `-T` needs its own arg though.

## Order-of-parse bugs — the flag that reads a FILE

`-K config` (curl) reads MORE options from a file — if you can land a
config file (upload) then flag `-K x` → option-file parse → more flags.

## `:`/`=` separators in values

`--opt=val` vs `--opt val` — the `=` form keeps it one token;
`--opt val` splits. For smuggling a space-separated value into one arg:
`--opt=val with spaces` keeps it one token.

## The `--no-` prefix family

`--no-OPT` negates a boolean — some tools auto-generate `--no-*` forms —
inject `--no-verify`/`--insecure`/`--no-check-certificate` to weaken a
check the fixed command relied on (curl `--insecure` → TLS-unsafe fetch).

## The env-var route past `--`

`CURL_HOME`, `GIT_SSH_COMMAND`, `TAR_OPTIONS`, `RSYNC_PROXY`,
`WGETRC`, `PSQL_OPTIONS` — env vars inject options past `--` — but env
control needs `env-var-injection` reach.

`TAR_OPTIONS=--checkpoint-action=exec=id tar cf x file` — the env var
injects the flag even behind `--`!

## Falsifiers

- `--` precedes input AND no env-var reaches the tool's option-parse
- the tool's flag set has no exec/write/read-capable flag at all

## Output to record

- the argv layout (which slot is yours) + the flag that lands there +
  whether `--` blocks it
