# Framework checks — how each stack actually validates URLs

The per-framework filter-implementations — the checks you'd see in
real code, the gaps each one has.

---

## 1. PHP — the parse_url world

```php
// the shapes you'd see in source:
$u = parse_url($url);
if ($u['host'] !== 'allowed.com') die();        // the parse-check —
                                              //   the host-field —
                                              //   the @-differential —
                                              //   parse_url takes the
                                              //   LAST @ — "a@b@c"
                                              //   → host=c — curl takes
                                              //   FIRST? — the diff
if (!filter_var($url, FILTER_VALIDATE_URL)) die();  // the validator —
                                                    //   strict — rejects
                                                    //   the malformed —
                                                    //   not the internal —
                                                    //   it validates FORM
                                                    //   not SAFETY — an
                                                    //   internal-URL is
                                                    //   a VALID url —
                                                    //   the check does
                                                    //   nothing
if (preg_match('/^https?:\/\/allowed\.com/', $url)) die();  // the regex —
                                                    //   the prefix-check —
                                                    //   the @-swap beats it
$host = parse_url($url, PHP_URL_HOST);            // the field-extract
if (ip2long($host) && filter_var($host, FILTER_VALIDATE_IP,
    FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) die();
                                              // the ip-range-check —
                                              //   ip2long misses hex/
                                              //   short/octal — the
                                              //   ip-encoding family
                                              //   beats it — 0x7f000001
                                              //   isn't a "valid-ip" to
                                              //   ip2long? — it IS —
                                              //   ip2long handles some —
                                              //   the forms matter
```

PHP's parse_url quirks: takes the LAST @ for userinfo — `a@b@c` →
host=c; accepts `\` in some positions; the port-range-validation
differs. The `ip2long`+FILTER_NO_PRIV_RANGE is the common ip-check —
it validates the STRING as an ip — the encoded-forms may not parse
as "ip" → the check doesn't apply → they resolve anyway.

## 2. Python — the urlparse world

```python
# the shapes:
u = urlparse(url)
if u.hostname != 'allowed.com': return     # the hostname-field — the
                                           # .hostname is the parsed —
                                           # the @-split — urlparse
                                           # takes the LAST @ —
                                           # "a@internal@x" → host=x
if u.hostname in BLOCKLIST: return         # the name-check — the
                                           # nip.io-forms beat it —
                                           # the name is "external"
                                           # — resolution is the gap
ip = socket.gethostbyname(u.hostname)      # the resolve-check —
                                           # the two-lookup gap —
                                           # rebind — OR the ip-
                                           # encoding — "0x7f000001"
                                           # → gethostbyname resolves
                                           # it → sees 127.0.0.1 →
                                           # blocked — UNLESS the
                                           # name-not-resolving check —
                                           # the resolve-check catches
                                           # encoded-ips — rebind needed
if u.scheme not in ('http','https'): return  # the scheme-check — the
                                           #   urllib file:// trick —
                                           #   "File" uppercase? the
                                           #   check-lowered? the
                                           #   case-diff
```

Python's urlparse: takes the LAST @; `.hostname` lowercases; the
`urljoin` behavior — the relative-url tricks — `urljoin(base,"//internal")`
→ internal — the protocol-relative. requests is http-only — urllib
does file/ftp — which lib is the fetcher matters.

## 3. Java — the URL/URI split

```java
// the shapes:
URL u = new URL(url);
if (!u.getHost().equals("allowed.com")) return;  // the getHost — java's
                                                 //   parsing — different
                                                 //   @/\ handling than
                                                 //   curl — java accepts
                                                 //   \ differently — the
                                                 //   java-vs-curl diff
URI u = new URI(url);                            // the URI-class —
                                                 //   stricter — different
                                                 //   results
InetAddress addr = InetAddress.getByName(u.getHost());
if (addr.isLoopbackAddress() || addr.isSiteLocalAddress() ||
    addr.isAnyLocalAddress() || addr.isLinkLocalAddress()) return;
                                                 // the inet-check — the
                                                 //   private-range-check —
                                                 //   catches internal-names —
                                                 //   the rebind is the gap —
                                                 //   isSiteLocal covers
                                                 //   10/172.16/192.168 —
                                                 //   isLinkLocal covers
                                                 //   169.254 — the check is
                                                 //   good — rebind-only —
                                                 //   or the A/AAAA diff —
                                                 //   getByName returns one —
                                                 //   which? the ipv6-shadow
// the URL.equals trap — URL.equals() RESOLVES — a HashMap<URL> lookup
//   performs DNS — the compare is a network-op — the dns-side-channel
```

Java's URL-class is famously quirky — the `equals` resolves, the
`\` handling differs from curl, the jar/netdoc handlers are unique.

## 4. Node — the url.parse vs new URL split

```js
// the shapes:
const u = new URL(url);
if (u.hostname !== 'allowed.com') return;   // the WHATWG-parser — strict —
                                            //   the @ the same as python —
                                            //   LAST-@ — the \ is normalized —
                                            //   WHATWG is the strict-one
const u2 = url.parse(url);                   // the LEGACY-parser — different —
                                             //   looser — accepts \ —
                                             //   the two-parser-diff in the
                                             //   SAME app — the validator
                                             //   uses new URL, the fetcher
                                             //   axios uses its own —
                                             //   the parse-mismatch is the
                                             //   node-specific-diff
if (!url.startsWith('http')) return;         // the string-check — the prefix —
                                             //   "http:\\internal" — the
                                             //   backslash — axios normalizes
// the dns.lookup check:
dns.lookup(u.hostname, (e, addr) => { if(isPrivate(addr)) return });
                                             // the resolve-check — rebind —
                                             //   or the encoding — dns.lookup
                                             //   resolves the ip-forms —
                                             //   rebind is the answer
```

The node-diff: `url.parse` (legacy, looser) vs `new URL` (WHATWG,
stricter) — an app validating with one and fetching with the other
is the differential — the `\` and `@` handling differ.

## 5. Go — the url.Parse + the strict-ish

```go
// the shapes:
u, err := url.Parse(url)
if u.Hostname() != "allowed.com" { return }   // the hostname — go's
                                              //   parser — the @ the
                                              //   standard-split — the
                                              //   stricter-charset — go
                                              //   rejects control-chars
if u.Scheme != "http" && u.Scheme != "https" { return }
                                              // the scheme-check — go's
                                              //   scheme-must-match — the
                                              //   case-folded? go lowercases
                                              //   schemes
ip := net.ParseIP(u.Hostname())
if ip != nil && ip.IsPrivate() { return }     // the ip-check — go's
                                            //   IsPrivate — the private-
                                            //   ranges — catches the ip-
                                            //   forms? — ParseIP parses
                                            //   127.0.0.1 but NOT the
                                            //   encodings — "0x7f000001"
                                            //   isn't an ip to ParseIP —
                                            //   the name resolves though —
                                            //   the resolve-vs-parse gap —
                                            //   ParseIP-check then Dial —
                                            //   Dial re-resolves — the gap
```

## 6. Ruby — the URI.parse world

```ruby
# the shapes:
u = URI.parse(url)
if u.host != 'allowed.com' then return end    # the host — ruby's parser —
                                              #   the \n historically —
                                              #   modern stricter — the
                                              #   control-char family
if u.scheme !~ /^https?$/ then return end     # the scheme — the regex —
                                              #   the case/unicode tricks
# Kernel#open — the dangerous sink — open("|command") — the pipe-trick —
#   the url starting "|" runs it — RCE — the most-dangerous — the url
#   is a command — not-ssrf — command-injection — the sink-shape
```

## 7. The common gaps — what every check misses

```text
- the encoding-forms — every string-check misses the ip-encodings —
  the "127." literal is never the only form
- the @-differential — every parse-check has a parser-side — the
  fetcher's parser may differ
- the case/unicode — the check's string-compare vs the resolver's
  normalization
- the resolve-twice — every resolve-check has the gap before the
  fetch's own resolution
- the redirect — every check that validates only the entry — the
  hops go unchecked
- the trailing-dot — the fqdn-form — same-name different-string
- the v6-shadow — the ipv4-only check misses the AAAA-answer
- the scheme-looseness — "http"-startswith misses "HtTp://" and
  "http:\\" and the alternate-schemes the fetcher still takes
- the port-forms — the int-vs-string port-compare
- the decode-order — %-encoded-forms that decode AFTER the check
```

## 8. The check-code-detection — read the validation

```text
white-box → grep the validation:
  php:    parse_url|filter_var|FILTER_VALIDATE|ip2long|FILTER_FLAG_NO_PRIV
  python: urlparse|urlsplit|hostname|gethostbyname|ip_address|is_private
  java:   new URL|new URI|getHost|getByName|isSiteLocal|isLoopback
  node:   new URL|url\.parse|urlParse|dns\.lookup|isPrivate|net\.isIP
  go:     url\.Parse|Hostname|ParseIP|IsPrivate|net\.Dial|LookupHost
  ruby:   URI\.parse|URI\.open|open\(