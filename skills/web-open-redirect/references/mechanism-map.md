# Mechanism map — the component-to-arm navigation

## The mechanism chain — component by component

```text
[1] PARAM      the request value — next/url/redirect_uri/...
      |-> param-inventory.md, per-param.md
      v
[2] FILTER     the server's check — startswith/contains/endswith/parse/scheme/decode
      |-> filter-bypass-deep.md, per-check.md, framework-matrix.md
      v
[3] RESOLUTION how the param becomes the Location — verbatim/decode/join
      |-> mechanism-deep.md
      v
[4] CARRIER    the Location:/Refresh:/meta/JS where it lands
      |-> detection.md, client-side.md, stored-and-referer.md, edge-cases.md
      v
[5] NAVIGATION the browser's WHATWG parse — the differential
      |-> parser-differentials.md
      v
[6] LAUNDER    the downstream trust — the OAuth/SSRF/XSS/bot/phishing
      |-> chain-routes.md, per-route.md, multi-step-chains.md
```

## The component → the arm map

```text
component 1 (the param):
  the vocabulary              -> param-inventory.md
  the context (login/oauth/...) -> per-param.md, per-endpoint.md
  the carrier                 -> per-param.md

component 2 (the filter):
  startswith('/')             -> the //, /\, \\, %5c arms -> per-check.md
  contains('target.com')      -> the substring arms -> per-check.md
  endswith('target.com')      -> the no-boundary arms -> per-target.md
  parse-host                  -> the userinfo/\@/encoded arms -> parser-differentials.md
  scheme in [http,https]      -> the https:/javascript:/data: arms -> per-vector.md
  decode-order                -> the encoded/double arms -> encoding-attacks.md
  the framework               -> framework-matrix.md

component 3 (the resolution):
  verbatim / decode / join / template -> mechanism-deep.md

component 4 (the carrier):
  Location:                   -> detection.md
  Refresh: / meta / JS        -> client-side.md
  stored / Referer            -> stored-and-referer.md
  edge                        -> edge-cases.md

component 5 (the navigation):
  the WHATWG parse            -> parser-differentials.md
  the differential arms       -> filter-bypass-deep.md

component 6 (the launder):
  the OAuth route             -> chain-routes.md, per-route.md
  the SSRF route              -> chain-routes.md
  the XSS route               -> chain-routes.md
  the bot route               -> chain-routes.md
  the phishing route          -> chain-routes.md
  the CRLF route              -> chain-routes.md
```

## The arm → the component map

```text
//evil.com          -> crosses the startswith('/') boundary (comp 2+5)
/\evil.com          -> the \ -> / normalize (comp 2+5)
\\evil.com          -> the \\ -> // normalize (comp 2+5)
%5c / %2f           -> the decode-order (comp 2+3)
%40 / \@            -> the userinfo parse (comp 2+5)
subdomain           -> the suffix boundary (comp 2)
substring           -> the contains boundary (comp 2)
https:evil.com      -> the scheme-no-// (comp 2+5)
javascript:/data:   -> the scheme boundary (comp 2)
the meta/JS         -> the client-side carrier (comp 4)
the Referer         -> the header carrier (comp 1+4)
the stored          -> the two-step carrier (comp 1+4)
```

## The map-record

`map: <the-component> -> <the-arms>` — each component's bypass surface.
