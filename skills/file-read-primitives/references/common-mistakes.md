# Common Mistakes — the budget-burners

## "The echo is the read" — `?file=../../x` → `../../x`

A param that echoes your input is REFLECTION, not file-read — the
`&x;`/`XXE_PROBE`-equivalent is the file's CONTENT, not your path —
check for `root:x:0:0:` not `../../x`.

## "A 404 = no read" — the sanitizer oracle

A `404`/`400` that echoes your cleaned input — `?file=../../x` → `x`
— is the SANITIZER stripping `../../` — not a "no file" — the read
still happens with the right syntax — `filter-bypass.md`.

## "Traversal is always needed" — the absolute-path-first rule

Many apps `join(base, input)` — `join("/app", "/etc/passwd")` =
`/etc/passwd` — absolute wins — traversal not needed — test absolute
FIRST.

## "The file content IS the flag" — the flag-shaped-string trap

A `?file=/flag{abc}` echo — the flag-shaped string was IN YOUR PATH —
not the file's content — only a flag that came FROM the file counts —
`evidence-rules.md`.

## "All `file:`-reads are the same" — the sink-type confusion

`file_get_contents` reads, `include` execs, `file_exists` oracles —
the sink TYPE decides the primitive — `include` + `php://input` = RCE,
`file_get_contents` + `php://input` = read-of-the-body.

## "The read failed because the file doesn't exist" — the mechanism-vs-path split

`FileNotFound` = the RESOLVER worked, the file is missing = the read
MECHANISM is live. `Entity not defined`/`no such file` on a KNOWN-
existing file (`/etc/passwd`) = the mechanism is dead. A `FileNotFound`
on `/etc/passwd` means something else is wrong.

## "php://filter works everywhere" — the PHP-only trap

`php://filter`/`phar://`/`expect://`/`data:`/`zip://`/`glob://` are
PHP stream-wrappers — they don't exist in Python/Node/Java/Go — a PHP-
specific payload on a non-PHP target is a wasted probe.

## "The traversal always needs `..`" — the normalize-tricks

`/etc/../etc/passwd`/`/./etc/passwd`/`//etc/passwd` — `..`-less
traversal exists — normalization is the trick — `traversal-variants.md`.

## "The encoding is the answer" — the decode-order mistake

`%2e%2e%2f` works when the app decodes once — `%252e%252e%252f` when
twice — the wrong decode-depth fails — the oracle-chain determines
the depth before the payload.

## "The flag is in `/flag`" — the guess-order mistake

`/flag` is the default — but `/proc/self/environ`/`/app/.env`/the
source-path often carry it — the source-read names the flag-path —
read the source first, then guess.

## "The read is in-band" — the blind-read miss

A read that lands in the response is in-band — a `filesize`-oracle is
blind — a `file_get_contents` that suppresses echo is blind — the
blind-read needs error/timing/OOB channels — `blind-techniques`-equivalent
or just record `surface`-level.

## "The dir-listing is a read" — the listing-vs-read split

`glob://*`/`file:///dir/`/`scandir`/`opendir` give a LISTING — a
listing is a weaker primitive — a listing reveals filenames to read —
record it separately.

## "A write primitive is a read" — the write-family mistake

`file_put_contents`/`unlink`/`copy`/`move_uploaded_file` are WRITES —
a `phar://`/`zip://` trigger through a write-sink = deser, not read —
`include-vs-read.md`'s sink-map.

## "The first sink is the only sink" — the multi-sink surface

The same `?file=` may feed `file_get_contents` (read) AND `include`
(exec) at different endpoints — each sink is its own test — the
class is per-sink, not per-param.
