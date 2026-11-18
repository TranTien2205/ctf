# The fetcher-matrix — per-library behavior reference

What each common fetcher accepts, what it follows, what it leaks.
The callback's User-Agent identifies which one you're talking to.

---

## libcurl (curl/x.y UA) — the scheme-king

```text
schemes:   http https ftp ftps scp sftp telnet ldap ldaps dict file
           tftp imap imaps pop3 pop3s smb smbs smtp smtps rtsp rtmp
           gopher gophers mqtt ws wss — the full set (build-
           dependent — curl --version lists them)
redirects: follows by default? — depends on the app's
           CURLOPT_FOLLOWLOCATION — CTF apps usually set it
           max-redirs default 50
proto-gate: CURLOPT_PROTOCOLS + CURLOPT_REDIR_PROTOCOLS — which
           schemes the request and the redirect can use — default
           CURLPROTO_ALL minus-file? — file IS in the default set —
           the default allows file:// unless the app pins it
auth-fwd:  CURLOPT_UNRESTRICTED_AUTH=0 default — auth stays same-
           host
crlf:      %-encoded crlf in the url-path reaches the wire — the
           url-parser decodes — the request splits — the injection
           vector
gopher:    the _-typechar — path-sent-verbatim — %-decoded once
dict:      <cmd>/<args> per line — the dict-protocol — works on any
           line-protocol
file:      file:///path — direct-read — the default-set
```

## python-requests — http-only

```text
schemes:   http https — hard-coded — anything else →
           "InvalidSchema: No connection adapters" — the scheme-
           error means requests — NO file://, NO gopher
redirects: follows by default — 30-max — allow_redirects=True
           per-hop scheme-change allowed by default
auth-fwd:  Authorization-header stripped on cross-host redirect —
           the header doesn't cross origins
crlf:      requests %-decodes then re-encodes — crlf-in-path →
           the request-line has the CRLF-encoded? — requests keeps
           %0d%0a as %-bytes in the path → NO split → requests
           doesn't inject — the encoding survives as text
file:      NOT supported — "InvalidSchema" — file:// is a hard-no
           — switch to urllib-shaped sinks for file
```

## python-urllib — http + file + ftp

```text
schemes:   http https file ftp data — the handler-set — FILE WORKS!
           file:///etc/passwd via urllib — the classic python-ssrf
           read — urllib's file-handler
redirects: follows — the redirect-handler — file-redirects gated
auth-fwd:  headers-forward — the unverifiable-header-set
crlf:      %-decode — similar-survives
file:      works — the read-path
```

## java URL — http + jar + netdoc + file

```text
schemes:   http https ftp file jar netdoc mailto — the handler-
           registry — jar:// and netdoc:// are java's unique doors
redirects: HttpURLConnection follows http-redirects — 20-max —
           protocol-change allowed — file-jar-redirects gated
crlf:      java's url-parse rejects raw-crlf — %-encoded reaches —
           the split depends on the transport — httpconn re-
           encodes mostly
jar:       jar:file:///x.jar!/inner — reads archive-inner — the
           !/-separator — jar+ssrf reads inside-archives
netdoc:    netdoc:///path = file:///path — the alias-scheme —
           the file-filter that checks "^file:" misses netdoc!
URL.equals: triggers DNS-lookup — the object-compare resolves —
            the dns-side-channel — a HashMap<URL> touch resolves
```

## node http/https/fetch/axios — http-only

```text
schemes:   http https ws wss (for ws-clients) — no file — no
           gopher — node's url-fetch is web-only
redirects: axios/fetch follow — maxRedirects — method+body
           preserved on 307/308
url-parse: url.parse (legacy) vs new URL (WHATWG) — DIFFERENT
           results on \/\@/\# — the parser-diff family — the
           app may validate with one and fetch with the other
crlf:      node's http rejects crlf in the request-line —
           %-encoded survives as text — less injectable than curl
           — but undici/axios have their own quirks
ws:        ws://internal — websocket-scheme — a ws-client fetch
           reaches internal-websockets
```

## Go net/http — http-only, strict-ish

```text
schemes:   http https — go's client — no others — url-parse is
           strict — rejects raw control-chars
redirects: follows — default-10 — the CheckRedirect hook controls
           — per-hop re-checkable — go-apps often pin it
crlf:      go's url-parse rejects control-chars in most positions —
           %-encoded survives as text — the split is rare
file:      not-supported — "unsupported protocol scheme"
```

## PHP — the wrapper-world

```text
schemes:   stream-wrappers — http https ftp ftps file php data zlib
           phar glob rar ssh2 expect ogg compress.* — the
           registered-set is per-build — file_get_contents takes
           ANY registered wrapper — the scheme-surface is the
           wrapper-list
redirects: stream-context max_redirects — default follows —
           protocol-changes follow mostly
wrappers-that-matter:
   php://filter   — the read-everything chain — resource=X —
                    filter-pipeline — base64/iconv/zlib — the LFI-
                    family — the whole filter-grammar
   php://input    — the request-body as a file
   php://fd/N     — an open-fd
   expect://      — ext-expect — executes! — RCE-direct
   phar://        — phar-archive — metadata-unserialize on open —
                    the deserialization-trigger
   data://        — inline-content — data://text/plain;base64,<?php
                    + include → RCE — needs allow_url_include
   glob://        — dir-listing — glob:///*.php — enumeration!
   compress.zlib:// — zip-contents
   phar://path.phar/inner — inner-file-read
```

## ruby open-uri — http + file + pipe-RCE

```text
schemes:   http https file ftp — open-uri adds file to Kernel#open
THE TRICK: Kernel#open("|id") — a string starting "|" runs it as
           a COMMAND — if the app does open(params[:url]) —
           url="|id" → RCE — not ssrf — command-injection — the
           sink-shape matters — open() is a COMMAND-RUNNER for
           pipe-strings — the most dangerous url-sink in ruby
redirects: open-uri follows — the open_uri_redirections —
           http→ftp/file transitions gated by OpenURI.redirectable?
file:      via open-uri — file:///path
crlf:      ruby's uri-parse historically took \n — the \n-in-url
           family — modern versions stricter
```

## .NET HttpClient/WebRequest/WebClient

```text
schemes:   HttpClient → http/https only
           WebRequest.Create → http file ftp — FILE!
           WebClient.DownloadString → http file ftp
           XmlDocument.Load(url) → the xml-fetch — XXE-adjacent —
           the url-load resolves entities → web-xxe boundary
redirects: HttpClient auto-follows — max-50 — authorization-
           header stripped on cross-host
file:      WebRequest/WebClient — file:///C:/x — windows-paths —
           \\\\smb → UNC → NTLM-leak
```

## The comparison-table

| Fetcher | file | gopher | jar/netdoc | ws | redirect | header-fwd | crlf-inject |
|---|---|---|---|---|---|---|---|
| libcurl | ✓ | ✓ | — | ✓ | by-app | same-host | ✓ (path) |
| py-requests | — | — | — | — | ✓ 30 | same-host | rare |
| py-urllib | ✓ | — | — | — | ✓ | varies | rare |
| java | ✓ | — | ✓ | — | ✓ 20 | varies | rare |
| node | — | — | — | ✓ | ✓ | varies | rare |
| go | — | — | — | — | ✓ 10 | per-app | rare |
| php-fgc | ✓ | wrapper | — | — | ✓ | varies | possible |
| php-curl | ✓ | ✓ | — | — | by-app | same-host | ✓ (path) |
| ruby-open | ✓ | — | — | — | gated | varies | old-versions |
| dotnet-wr | ✓ | — | — | — | ✓ | same-host | rare |

## The UA-to-strategy table

| UA | Reach | First escalation |
|---|---|---|
| curl/* | everything | file:// → gopher→redis |
| python-requests/* | http(s) | url-parsing + internal-services |
| Python-urllib/* | http+file | file:///flag |
| Java/* | http+jar+netdoc | netdoc:///flag + jar-inner |
| Go-http-client/* | http(s) | url-parsing only |
| GuzzleHttp/* | http(s) | internal-http-services |
| okhttp/* | http(s) | internal-http |
| WordPress/* | http(s) | wp-fetch — internal-http |
| node-fetch/undici/axios | http(s)+ws | ws:// internal + http |
| faraday/Ruby | http(s) | open()-pipe trick if open() sink |
| Headless-Chrome | browser | different class — web-xss bot-visit |
