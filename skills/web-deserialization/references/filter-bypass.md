# Filter & WAF Bypass — when the sink checks your bytes

## The taxonomy — what the filter can be

1. **byte blacklist** — `if (strpos($x,'O:')) die;` on the raw blob
2. **type/grammar filter** — `unserialize($x,['allowed_classes'=>[...]])`
3. **length gate** — `strlen($x) > N` reject
4. **encoding mangle** — `addslashes`, `htmlspecialchars`, `urldecode` pairs
5. **signature/MAC** — see `signature-bypass.md`
6. **WAF regex** — `O:\d|__destruct|system|eval`
7. **content-type gate** — only accepts `application/json` but the JSON
   field holds a serialized string

## Byte-blacklist bypasses

### `O:` / `a:` detection evasion (PHP)

```
O:4:"User"...        → blocked by /O:\d/
+O:4:"User"...       → leading + on int — some parsers accept
O:+4:"User"...       → signed length — PHP accepts O:+4:
a:1:{...}            → the array wrapper around the object
S:5:"\4f..."         → escape the O byte inside a string
```

PHP's `unserialize` accepts `O:+4:"User"` (signed length). A regex on
`O:\d` misses it. `\x4f` inside an `S:` string is the O byte smuggled.

### Magic-byte smuggling (binary formats)

- A `pickle` can be base64'd, hex'd, zlib'd, or wrapped in another format —
  the blacklist on `gAN`/`80 03` misses the wrapper.
- `pickle.dumps(obj, 0)` is pure ASCII — no `80` byte at all.
- A `p5` out-of-band-buffer pickle splits the payload across the framing.

### Case and whitespace (JSON/XML)

```json
{"$TYPE":"..."}      → some Json.NET paths are case-sensitive — test
{"$type":"..."}      → but the attr name itself can't change
```

```xml
<object class="java.lang.ProcessBuilder">   → blacklist on 'ProcessBuilder'
<object class="java.lang.\x50rocessBuilder">?  → no — XML doesn't hex-escape
```

XML can't escape inside a tag name — instead use a CDATA/dtd indirection or
a different gadget class not in the blacklist.

## `allowed_classes` bypasses (PHP ≥7.0)

```php
unserialize($x, ['allowed_classes' => ['Session','User']]);
```

- An allowed class that itself has a magic method → chain INSIDE the allowed
  class. `Session` often has a `__destruct`/`__wakeup` that touches a prop.
- `__PHP_Incomplete_Class` objects still carry their props — a later
  `serialize()`/`get_object_vars`/`var_dump` may still trip a magic method.
- `allowed_classes => true` (default) → all classes — only `false`/`[]` blocks.
- The filter checks the TOP-level class name — a nested `O:` inside an
  allowed `a:` still instantiates if the parent is allowed. Actually no —
  the check is per-object. But the *name* comparison is case-insensitive
  and namespace-sensitive — `App\User` vs `app\user` matching matters.

## Length-gate bypasses

- `pickle.dumps(obj, 4)` vs `protocol=0` — size differs ~3x
- PHP: `i:1;` vs `b:1;` — pick the smallest type
- PHP: short class names — use an alias or a single-char class the app has
- a compressed wrapper if the app `gzuncompress`es first
- reference short names via `R:`/`r:` back-refs instead of repeating strings

## Encoding-mangle bypasses

- `addslashes`/`'` filter → `S:` hex-escape type carries arbitrary bytes
  without a real quote/NUL in the stream (`php_ser_gen.py --str-type S`)
- `htmlspecialchars` → deliver in a field the app base64-decodes after
  the encode, or use `S:` so no `"`/`<`/`>` byte is literal
- double `urldecode` → double-encode the whole blob (`%253a`)
- `stripslashes` BEFORE `unserialize` → your `\xNN` escapes lose the `\` —
  deliver them `\\xNN` so one strip leaves `\xNN`

## WAF-regex bypasses

| Regex | Bypass |
|---|---|
| `/O:\d+:"/"` | `O:+4:"User"` (signed len) or `O:04:"User"` (padded) |
| `/unserialize|__wakeup|__destruct/` | those strings don't appear in the PAYLOAD — the class method names do; a class named differently evades |
| `/system|exec|shell_exec/` | use `passthru`, `proc_open`, `popen`, `pcntl_exec`, `assert`, `preg_replace` /e, `create_function`, `call_user_func` |
| `/eval/` | `assert()`, `array_map(''.'assert')`, `preg_replace` /e, `create_function` |
| `/php:\/\/|phar:\/\//` | `Phar://`, `phar%3a//`, `php://filter` inside a string |

## The `unserialize` wrapper-eat-blob trick

`unserialize` ignores trailing garbage — `O:4:"User":...{}}}}}GARBAGE` is
fine. A WAF scanning for `^O:` misses a blob prefixed `x=O:4...` if the app
extracts the value. And `unserialize` accepts leading whitespace in some
builds.

## The "change the channel" bypass

- JSON field carrying the serialized string (when the WAF only scans
  `application/x-www-form-urlencoded` bodies)
- multipart file upload the app reads then unserializes
- a header (`X-Data:`) the app base64-decodes into the sink
- a WebSocket frame — WAFs often don't inspect ws frames
- a cookie the app base64+unserializes — WAF scanned the raw cookie value,
  which is already encoded

## Output to record

- Which filter layer was bypassed + the exact evasion used
- The verbatim response proving the sink still fired
