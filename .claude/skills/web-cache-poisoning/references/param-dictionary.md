# Param dictionary — every param and path that may poison

The complete list of query params and paths — the keyed-vs-unkeyed question.

---

## 1. The tracking-param family — the usually-keyed params

```text
?utm_source=<v>         — a tracking param (usually keyed in $request_uri)
?utm_medium=<v>         — a tracking param
?utm_campaign=<v>       — a tracking param
?utm_content=<v>        — a tracking param
?utm_term=<v>           — a tracking param
?fbclid=<v>             — a Facebook tracking param
?gclid=<v>              — a Google tracking param
?msclkid=<v>            — a Bing tracking param
?dclid=<v>              — a DoubleClick tracking param
```

## 2. The cache-buster family — the keyed-by-design params

```text
?_=<v>                  — a cache-buster (keyed by design)
?cb=<v>                 — a cache-buster
?cache=<v>              — a cache-buster
?nocache=<v>            — a cache-buster
?t=<v>                  — a timestamp buster
?v=<v>                  — a version buster
?rand=<v>               — a random buster
```

## 3. The functional-param family — the app-logic params

```text
?id=<v>                 — an object id (usually keyed)
?page=<v>               — a page number (usually keyed)
?q=<v>                  — a search query (usually keyed)
?search=<v>             — a search param
?filter=<v>             — a filter param
?sort=<v>               — a sort param
?lang=<v>               — a language param
?theme=<v>              — a theme param
?debug=<v>              — a debug param
?preview=<v>            — a preview param
```

## 4. The path family — the normalization boundaries

```text
/static/../admin        — a path-traversal normalization boundary
/%2e%2e/admin           — an encoded path
/static/%2e%2e/admin    — a mixed-encoding path
/%252e%252e/admin       — a doubly-encoded path
/Page                   — a case-normalization boundary
/page/                  — a trailing-slash boundary
/page//admin            — a double-slash boundary
/page.%2f               — a dot-slash boundary
/%2f/admin              — a leading-encoded-slash boundary
```

## 5. The param-keyedness check — send it and confirm the store

```bash
# for each candidate param — send it → check the stored copy
for p in 'utm_source' 'fbclid' 'id' 'debug' 'preview' 'theme' 'lang'; do
  curl "$BASE/page?cb=<unique>&$p=<marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$p UNKEYED"
done
```

## 6. The keyed param — a per-value entry

```text
a keyed param keys the cache entry per-value — YOUR param's effect
is in YOUR copy only — a keyed param isn't poisonable.
the default: $request_uri includes the query — the params ARE keyed.
an UNKEYED param is the exception — a stripped param or a
normalization that drops it.
```

## 7. The unkeyed param — a poisonable input

```text
an unkeyed param the app reflects but the cache ignores — the stored
copy carries YOUR param's effect under the shared URL — every
requester's copy serves it.
a param stripped from the key ($uri without the query) is unkeyed.
```

## 8. The param-stripping config — where the strip happens

```nginx
# a config that strips the query — an unkeyed param
proxy_cache_key $scheme$proxy_host$uri;   # $uri drops the query → the params unkeyed
# or a map that drops a param — a stripped utm
map $args $cache_args { default $args; ~utm_ ""; }
proxy_cache_key $scheme$proxy_host$uri$cache_args;
```

## 9. The functional-param surface — the app's reflection

```bash
# the app's reflected params — the unkeyed-input surface
grep -rnoiE 'request.GET|request.params|request.args|params\[|query\[|reflection|echo' <src> | head -15
```

## 10. The path surface — the normalization boundary

```bash
# the app's path handling — the normalization boundary
grep -rnoiE 'normalize|redirect|rewrite|path|decode|urldecode|canonical|route' <src> | head -10
```

## 11. The param-to-effect map — which param produces which effect

```text
?utm_source=<v>         → a tracking-param copy (a keyed-vs-unkeyed check)
?debug=<v>              → a debug page (a keyed-vs-unkeyed check)
?theme=<v>              → a themed page (a per-theme copy)
?lang=<v>               → a localized page (a per-language copy)
?id=<v>                 → an object page (usually keyed)
/static/../admin        → a route confusion (a normalization boundary)
/Page                   → a case confusion (a normalization boundary)
```

## 12. The param's falsifier — a keyed param

```text
a keyed param → a per-value entry → YOUR param's effect is in YOUR
copy only → a different class.
```
