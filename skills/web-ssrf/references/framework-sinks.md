# Framework sinks — where the url-parameter actually lives

The fetch-call differs by stack; the params, schemes, and bypass-
surface differ with it. Match the framework first — the payload
follows the fetcher.

---

## 1. The fetcher-fingerprint table — who's fetching

```text
User-Agent "curl/x.y"            → libcurl — gopher/dict/file/ldap/
                                   ftp/tftp/imap/all — scheme-rich
User-Agent "python-requests/x"   → python — http(s) only — no gopher
User-Agent "Python-urllib/x"     → urllib — http/file/ftp — file ok!
User-Agent "Java/x.y"            → java-url — jar/netdoc/http —
                                   jar:// + netdoc:// reach files
User-Agent "okhttp/x"            → java-android — http(s) only
User-Agent "Go-http-client/x"    → golang — http(s) only
User-Agent "GuzzleHttp/x"        → php-guzzle — http(s) — no gopher
User-Agent "WordPress/x"         → php-wp — http(s) — gopher stripped
User-Agent "Symfony HttpClient"  → php — http(s)
User-Agent "faraday" / "Ruby"    → ruby — http(s)
User-Agent "node-fetch" / "undici" → node — http(s)
User-Agent "Mozilla/... Headless" → a BROWSER — client-side nav —
                                   different class — xss-adjacent
User-Agent "axios/x"             → node — http(s)
no-User-Agent                     → raw-socket / default-lib — varies
```

The callback's User-Agent is the fetcher — it picks the scheme-
list before you probe. `oob_listener hits` reads it.

## 2. PHP — the scheme-rich fetcher

```text
sinks:    file_get_contents($url) — takes file:// php:// http://
                                   data:// ftp:// ftps:// — the
                                   stream-wrapper list — wrappers
                                   are the whole surface
          file($url), readfile($url), fopen($url)
          include($url)/require($url) — CODE-EXEC via wrapper!
          curl_exec — ext-curl — the libcurl scheme-list
          fsockopen — raw-socket — no scheme
          SoapClient($wsdl) — wsdl-fetch — ssrf-via-wsdl
          DOMDocument::load($url)
          simplexml_load_file($url)
          getimagesize($url) — image-validator — still fetches!
          get_headers($url)
          parse_url + manual socket
wrappers: http https ftp ftps file php data zlib bzip2 glob phar
          rar ssh2 expect ogg rar compress.zlib compress.bzip2
          http2? — the registered-wrapper list is per-build
tricks:   php://filter chains — the resource-param — reads ANY
          file — see web-lfi filter reference
          expect:// — ext-expect — direct RCE — rare-build
          phar:// — phar-deserialize on metadata-read — the
          unserialize-trigger — web-deserialization chain
          data://text/plain;base64,<php> + include → RCE
```

## 3. Python — requests/urllib split

```text
sinks:    requests.get(url) — http/https only — urllib3 — no
            file-scheme → SSRF limited to http-reaches — the
            filter-bypass surface is url-PARSING not schemes
          urllib.request.urlopen(url) — http/file/ftp — FILE
            WORKS! — file:///etc/passwd reads!
          urllib.urlopen — py2 — same
          http.client.HTTPSConnection — http
          socket.create_connection — raw — the url must be a
            host:port — no scheme — direct-tcp
          xmlrpc.client — xmlrpc-urls
          smtplib/imaplib — mail-libs — host-params
          redis.Redis(host=...) — the redis-lib — host-control
          pycurl — the libcurl binding — gopher!
schemes:  requests → http/https
          urllib → http/https/file/ftp/data — FILE!
          pycurl → the libcurl set — gopher/dict/ldap/…
tricks:   urllib file:// — the read primitive
          py \x85 nextline — splitlines() quirks — the control-
            char family — \x85 splits py's url-lines
          requests skips file:// — swap-to-urllib pattern in
            CTF apps that use BOTH
```

## 4. Java — the jar/netdoc family

```text
sinks:    new URL(url).openStream() — the handler-set —
            http/https/ftp/file/jar — JAR! FILE! — java-ssrf is
            scheme-rich
          new URL(url).openConnection()
          HttpURLConnection — http/https
          URLClassLoader — class-load remote
          ImageIO.read(url) — still fetches
          Jsoup.connect(url) — http
          RestTemplate/WebClient — http
          HttpClient (java11) — http
schemes:  http https ftp file jar netdoc mailto
tricks:   jar:url!/inner — read archive-contents
          netdoc:// = file://
          java-url-parsing quirks — the # and \ differentials —
            the classic java-vs-curl split
          URL.equals triggers DNS — the hashmap-DNS side-channel!
          — java.net.URL.equals() RESOLVES — the object-compare
            is a network-op — dns-rebind's sibling
```

## 5. Node — http(s)-only mostly

```text
sinks:    axios/fetch/request/got — http(s)
          http.get / https.get
          undici — http(s)
          ws — websockets — ws://wss:// reach!
          socket.io-client
          grpc — grpc-urls
schemes:  http https ws wss — file:// NOT supported by http-libs
          — node fs.readFile isn't url-shaped — but fs.readFile
            with a path-param is web-lfi not ssrf
tricks:   ws:// — the websocket-scheme — when the fetch is a
          ws-client → internal-websocket reach
          node's url-parse quirks — the \ and @ differentials —
          url.parse vs new URL — legacy-vs-WHATWG — the classic
          node-diff — url.parse accepts \ as / — new URL stricter
          axios base-url-join quirks — relative-url resolution
```

## 6. Ruby — net/http

```text
sinks:    Net::HTTP.get(URI(url)) — http(s)
          open-uri — http/file/ftp — FILE! — Kernel#open in old
            ruby even runs commands: open("|id") — the pipe-trick!
          RestClient — http
          HTTParty — http
          Faraday — http
schemes:  http https ftp file (open-uri)
tricks:   Kernel#open("|command") — open-uri's pipe-form —
          RCE-direct — a url starting "|" runs a command —
          the most dangerous sink — open("|cat /flag")
          open-uri's file:// — read
          the %0a tricks — ruby's uri-parse accepted newlines
          historically — the \n-in-url family
```

## 7. Go — http only, but raw

```text
sinks:    http.Get/Client.Do — http(s)
          http.NewRequest — http
          net.Dial — raw-tcp — host:port
          websocket-clients — ws
schemes:  http https — go's net/http doesn't take file://
tricks:   go's url-parse is strict-ish — the \ rejection differs
          from java — parser-diff against a java-validator
          net.Dial("tcp","internal:6379") — raw — if the app dials
          a host-param directly → any-port-tcp — the line-protocol
          write path — but the app must build the request — limited
          ssrf is "fetch a URL" — go's url-fetch is http-only —
          the scheme-tricks don't apply — bypass via parsing not
          schemes
```

## 8. .NET — HttpClient/WebRequest

```text
sinks:    HttpClient.GetAsync — http(s)
          WebRequest.Create — http/file/ftp — FILE!
          WebClient.DownloadString — http/file/ftp
          XmlDocument.Load(url) — xml-fetch — XXE-adjacent!
          Process.Start with a url?
schemes:  http https file ftp — WebRequest-family
tricks:   file:// — the read — windows-paths — file:///C:/x
          \\\\smb — UNC — the NTLM-leak — the fetcher's creds to
          your share — windows-only
          the URI-parse quirks — dotnet's Uri-class vs a java-
          validator
```

## 9. The curl-lib bindings — the scheme-rich set

```text
php-ext-curl, python-pycurl, ruby-curb, perl-lwp+curl, node-curl —
   all expose the FULL libcurl scheme-list:
   http https ftp ftps scp sftp telnet ldap ldaps dict file tftp
   imap imaps pop3 pop3s smb smbs smtp smtps rtsp rtmp gopher
   gophers mqtt ws wss — gopher is the money-scheme
the UA is usually "curl/x.y.z" or the binding's name
```

## 10. The headless-browser case — a different beast

```text
The "fetch" is a Chromium visit — the url goes to a real browser —
  - javascript runs — window.location, fetch(), XHR all free
  - the page runs with the BROWSER's origin — your url's origin
  - cookies/session attached — it's a bot-visit — the XSS-adjacent
    class — the payload is html+js not a server-fetch
  - file:// in a browser = the browser's own fs — sandboxed —
    different semantics
  - chrome's url-parse is WHATWG — different quirks
```

## 11. The sink-shape questions — what to ask the code

```text
white-box — grep the fetch-sites:
  php:    file_get_contents|curl_exec|fsockopen|include\(|SoapClient|
          get_headers|getimagesize|simplexml_load_file|DOMDocument::load
  python: requests\.|urlopen|pycurl|http\.client|socket\.create|
          xmlrpc|urlretrieve|requests\.get|requests\.post
  java:   openStream|openConnection|HttpURLConnection|RestTemplate|
          WebClient|Jsoup\.connect|ImageIO\.read|URLClassLoader
  node:   axios|fetch\(|http\.get|request\(|got\(|undici|new WebSocket
  ruby:   Net::HTTP|open-uri|open\(|RestClient|HTTParty|Faraday|URI\.open
  go:     http\.Get|Client\.Do|NewRequest|net\.Dial
  dotnet: HttpClient|WebRequest|WebClient|DownloadString|XmlDocument

the question the code answers: WHAT does the value reach —
  - a url-scheme (scheme-rich → gopher/file work)
  - a host (any-port-tcp → connect-anywhere)
  - a command-argument (→ command-injection — different class)
  - a header (→ header-injection)
  - a template (→ ssti — different class)
```

## 12. The proxy-env surface — the fetcher's env

```text
http_proxy/https_proxy env-vars — the fetcher may route through
  a proxy — the proxy's scheme-cap is ITS OWN — a squid strips
  non-http — the env decides whether gopher reaches the wire —
  file:///proc/self/environ shows them
all_proxy — socks — socks-proxies carry tcp — gopher-through-socks
no_proxy — the bypass-list — the app-domain usually no-proxied —
   meaning your-url-to-the-app goes DIRECT — the egress-path
   differs by target
```
