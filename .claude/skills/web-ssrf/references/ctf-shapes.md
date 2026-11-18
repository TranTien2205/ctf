# CTF shapes — how SSRF challenges are actually packaged

The recurring challenge-archetypes — what the surface looks like,
what the flag-location is, which chain it wants.

---

## 1. The "fetch-this-url" shape — the plainest form

```text
surface:   a form/endpoint that takes url= and displays the fetched
           page — "preview", "screenshot", "link-check", "webhook-
           test", "import-from-url", "url-health-check"
flag:      on an internal route — /flag on loopback — or in the
           metadata — or a file
chain:     url=http://127.0.0.1:<app-port>/flag — the loopback-admin
           — or url=file:///flag — the read
signals:   the response contains the fetched-page — full echo —
           the richest channel — every internal-page readable
```

## 2. The "avatar/image-import" shape — the media-fetcher

```text
surface:   "import avatar by URL", "upload from URL", "fetch profile
           picture", "import image" — the server downloads the image
flag:      usually in an internal-page — the image-endpoint echoes
           the fetched-BYTES — but the fetcher may VALIDATE the
           content is an image → content-type-check → magic-bytes
           → a polyglot-target: serve a real-image from your host —
           the fetched-bytes display back — but the flag isn't an
           image → the check must be beaten — magic-byte-then-html
           polyglot — or the flag ends up in an image-parsable path
signals:   avatar-endpoint, content-type sniffing, "only images
           allowed"
chain:     url=http://internal/flag + beat-the-image-check — or the
           image-endpoint leaks even non-image bytes
```

## 3. The "webhook/callback" shape — the deferred fetch

```text
surface:   "register a webhook", "callback-url", "notification-
           endpoint" — stored, fetched LATER by a worker
flag:      the worker hits your url → OOB-only — blind — the
           callback is the only channel — the flag must come from
           an internal-route THE WORKER can reach — webhook+ssrf
           = the deferred-fetch — the callback's own job is to be
           fetched — the flag is usually served FROM an internal
           endpoint to anything that asks — so: register your
           callback = the internal-flag-url? — no — the worker
           FETCHES your url — you register url=http://internal/flag
           and the worker fetches it but you don't see the response
           — UNLESS the webhook-response is stored/displayed back
           — the "webhook-test-response" page — or the worker's
           reply goes in a queue you read
signals:   webhook-registration, "we'll call your endpoint", async
           processing, a status-page that shows the last-call-result
```

## 4. The "report-bot" shape — the browser-visit

```text
surface:   "report this post to admin", "flag for review", "share
           with support" — a headless-browser visits your url — the
           browser carries ADMIN-cookies — the flag is behind the
           admin-session
chain:     NOT ssrf in the server-sense — it's a bot-visit — the
           payload is an html-page + js — XSS/adjacent — you serve
           a page that exfiltrates the bot's session or makes the
           bot fetch internal-routes — web-xss bot-visit references —
           the url-param is shared but the primitive is browser-side
signals:   "the admin will review", "a bot checks your link",
           report/flag buttons — headless-browser UA
```

## 5. The "screenshot/pdf-render" shape — the renderer

```text
surface:   "generate screenshot", "render page to pdf", "print-
           preview" — a headless-renderer visits — different from
           the report-bot — the OUTPUT (screenshot/pdf) is the
           read-channel — what's rendered comes back as image/pdf
flag:      rendered-content — url=http://internal/flag → the
           screenshot SHOWS the flag — the render-output is the
           exfil — or file:///etc/passwd → the passwd rendered as
           an image — read via pdf_text / image-ocr
signals:   pdf-output, screenshot-download, wkhtmltopdf/chromium-
           headless signs
```

## 6. The "xml-wsdl/soap" shape — the protocol-fetcher

```text
surface:   a SOAP-endpoint that takes a WSDL-url — the app parses
           the wsdl → fetches it → the wsdl's imports reach other
           urls — SOAP+SSRF
flag:      the wsdl-fetch echoes — or the wsdl itself references
           internal-endpoints — the chained-fetch — wsdl-imports
           are the follow-hop
signals:   wsdl-param, soap-endpoint, xml-response
chain:     url=http://internal/admin.wsdl → the wsdl-parse echoes
           the internal-response — or the wsdl-import chain
```

## 7. The "url-to-markdown/html" shape — the importer

```text
surface:   "import a page", "convert url to markdown", "bookmark-
           import", "read-later" — fetches + transforms + stores —
           the stored-content is the read
flag:      url=file:///etc/passwd → the passwd becomes a "bookmark"
           — stored and displayed — file-read-via-importer
signals:   import/bookmark/archive endpoints, the stored-content
           page
```

## 8. The "redirect-validation" shape — the whitelist

```text
surface:   the url-param with an explicit allowlist — "only
           api.example.com" — the validation is the puzzle
flag:      internal-route — the bypass is the point
chain:     the whole url-parsing.md file — @/#/?/encoding/parser-
           diff/redirect — the family that matches the check-type
signals:   "url must be ...", "only https allowed", "must end with
           .example.com" — the error-message names the check
```

## 9. The "blind-webhook" shape — pure-OOB

```text
surface:   "submit a url — we check it nightly" — no response —
           the fetch happens on a schedule
flag:      OOB-only — the canary proves it — then the internal-
           fetch needs an echo — the status-page of the webhook-
           results — or a second-channel — the worker's response
           shows up in your "webhook-history"
signals:   scheduled-jobs, "check later", a results-history page
```

## 10. The "internal-api" shape — the admin-on-loopback

```text
surface:   the app has an admin-route bound to 127.0.0.1 —
           "admin-panel only on localhost" — the check is the
           source-IP — the server-fetch comes FROM 127.0.0.1
flag:      the admin-route's data — /admin/flag — the loopback-
           bound admin is the classic — the SSRF IS the auth-bypass
chain:     url=http://127.0.0.1:app-port/admin — direct — no tricks
signals:   the public-route says "admin access from localhost only"
           or a 403 on /admin from outside
```

## 11. The "cloud-metadata" shape — the cloud-deploy

```text
surface:   any-fetch + the deploy is on a cloud — the flag is the
           user-data or the iam-creds
chain:     169.254.169.254 direct — or the v1beta1 trick for gcp —
           or the token-put for imdsv2 (usually unrunnable — the
           shape assumes v1 or a fetcher that PUTs)
signals:   aws/gcp/azure hostnames in source, "instance", "cloud",
           the deploy-context, Dockerfile with a cloud-runtime
```

## 12. The "redis/internal-service" shape — the gopher-target

```text
surface:   the flag is a redis-KEY — or the app-caches via redis —
           gopher→redis → the flag-key
chain:     gopher://127.0.0.1:6379/_GET%20flag — the direct key —
           or _KEYS_* inventory → _GET the found-key
signals:   redis in requirements.txt/compose — the app-name
           suggests a cache — the flag-name is a redis-key
```

## 13. The "second-order" shape — stored-url

```text
surface:   you store a url (profile-pic, webhook, feed) — later a
           job fetches it — the fetch's RESULT lands somewhere —
           the "rss-feed-reader" — your feed-url is fetched, the
           items are displayed — feed-contents = the read-channel
flag:      file:///flag → the file-content becomes a feed-item →
           displayed — the stored-then-rendered channel
signals:   feed/rss/import — the items-list — periodic-refresh
```

## 14. The "proxy-route" shape — the app's own proxy

```text
surface:   /proxy?u= — the app has a general-purpose proxy-route —
           "fetch through me" — by design it fetches anything — the
           filter is the puzzle
flag:      internal — the proxy reaches what you can't
signals:   a proxy/fetch/relay route in source — hop-count in
           response-headers
```

## 15. The "weather-app" shape — the CRLF

```text
surface:   url-param where %0d%0a reaches the wire → the request
           splits → desync — the verified-card chain
flag:      the desync'd response — the injected-request's answer
           lands in a different response
signals:   the url-echo shows your injected-headers reached the
           wire — the callback shows the split — crlf-injection.md
```

## 16. The "file-scheme-first" shape — the obvious-read

```text
surface:   url-param accepts file:// — the challenge is "read the
           right file" — the flag-path is the puzzle — or the
           file:// is PARTIALLY-blocked — "file:// only for /uploads"
flag:      a specific-path — find via /proc/self/maps, mountinfo,
           the app-source — the path-discovery is the challenge
signals:   "import a file", "load a document", path-params
```

## 17. The "egress-blocked" shape — the no-external shape

```text
surface:   external-egress is blocked — the fetcher can't reach
           the internet — but internal-fetch works — the callback
           NEVER fires — don't wait for it — the internal-only
           model — the proof is internal-content-echo not callback
signals:   timeouts on your-callback, internal-IPs respond — the
           egress-firewall shape — the canary-silence is EXPECTED —
           pivot to internal-content proof immediately
```

## 18. The "docker-socket" shape — the container-control

```text
surface:   the app can reach the docker-socket — /var/run/docker.sock
           mounted or 2375 exposed — the fetcher reaches it
chain:     http+unix://…/containers/json or tcp-2375 — the api →
           container-spawn → host-mount → flag — the escape-chain
signals:   docker.sock in mounts, container-context, the cgroup-
           markers show docker
```

## 19. The "two-app" shape — the sibling-service

```text
surface:   the flag lives on a DIFFERENT service — a second app on
           another port/host — the ssrf reaches the sibling — the
           sibling's /flag is loopback-only — your fetch comes from
           the right host
chain:     subnet-sweep → find the sibling → fetch its flag-route
signals:   compose-files with two services, the sibling-name in
           env-vars (SERVICE_B_HOST), the internal-dns name
```

## 20. The "no-fetch-response" shape — headless-blind

```text
surface:   the fetcher never echoes — not even errors — pure-blind
flag:      the chain must WRITE to something readable — gopher→
           redis→SET a key the WEB displays — or file-write to a
           served-dir — or a timing-oracle extraction — the hardest
           shape — the answer is always "write state, read via a
           different channel"
signals:   every response identical — no oracle at all → the
           escalation MUST go through a store
```

## The shape-to-chain table

| Surface | Flag-home | First move |
|---|---|---|
| url-echo fetcher | internal-route | `http://127.0.0.1:app/flag` |
| image-import | internal-route | url → flag + image-check-bypass |
| webhook-deferred | internal-route | canary + the results-page |
| report-bot | admin-session | html+js page — bot-exfil — NOT ssrf |
| screenshot/pdf | internal-route | url → flag → render-output |
| soap/wsdl | internal-wsdl | wsdl-import chain |
| importer/rss | file | `file:///flag` → stored-content |
| whitelist | internal | the matching url-parsing bypass |
| blind-nightly | internal | canary → internal-echo path |
| loopback-admin | admin-route | `http://127.0.0.1:port/admin` |
| cloud-deploy | metadata | `169.254.169.254/latest/user-data` |
| redis-cache | redis-key | `gopher://…:6379/_GET flag` |
| egress-blocked | internal | internal-echo — canary never fires |
| docker-socket | host-fs | unix/2375 → container-spawn |
| sibling-app | sibling-flag | subnet-sweep → sibling /flag |
| pure-blind | state-write | gopher→redis→webread |
