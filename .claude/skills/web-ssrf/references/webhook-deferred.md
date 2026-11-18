# Deferred fetch — webhooks, schedulers, and the async surface

The url is stored and fetched later — by a queue-worker, a bot,
a scheduler, a renderer — not synchronously in the request. The
channel is different; the fetch-context is different; the reach
is different.

---

## 1. The deferred-shapes — the storage shapes

```text
- webhook-registration — "call this url when X" — the trigger-
  fetch — the webhook-fires later — on an event or a schedule
- the "check later" — "we'll check your link" — the queue
- feed/rss-import — the feed-url — refreshed periodically
- avatar/profile-url — stored, fetched on display — every-view
  fetches — or cached-once
- report-bot — "a moderator reviews" — headless-browser visit —
  browser-context — different class boundary — web-xss bot-visit
- the "preview" — render-then-show — the render-worker
- scheduled-jobs — cron/queue — the url is a job-arg
- the verify-step — "we'll verify your domain" — the verification-
  fetch — the domain-verification service
```

## 2. The channel — where the result lands

```text
the fetch's RESULT goes somewhere:
  - a status-page — "your webhook returned 200" — the response-
    STATUS is the channel — not the body — the status-oracle
  - a history-page — "last 10 calls" — the response-list — the
    body may be stored — the stored-response — the read-channel
  - a notification — "we called your endpoint" — the fire-and-
    forget — no read-back — pure-blind
  - a queue — the result in a message-queue you read
  - the page-content — the rendered-result — the bot's-render
    stored as a screenshot
```

The deferred-result channel is the diagnostic — where does the
fetch's output SURFACE? — map it before probing — the status-
page is often the only channel — a status-only oracle.

## 3. The timing — when it fires

```text
- immediate — synchronous — the response in the request — not
  deferred at all
- seconds — a fast-queue — the worker polls quickly
- minutes — a cron/scheduled — the per-tick — the tick-window
- on-event — the webhook-fires when the event happens — trigger
  the event to trigger the fetch — the event-trigger is a probe
- nightly — a batch — the canary fires in hours — the patience-
  constraint — the contest-clock matters — a nightly-fetch may
  not fire in contest-time — is there a manual-trigger?
```

The canary-tag + the listener-log — the fire-TIME tells you the
schedule — a hit at :00 vs :37 tells you cron-ish vs event-driven.

## 4. The fetch-context — who fetches

```text
the deferred-fetch's context differs from the web-request's:
  - a WORKER — a different host — the callback's source-ip is the
    worker's — the worker's reachable-set is different — different
    internal-view — the worker may reach MORE or LESS
  - a BOT — a headless-browser — browser-context — the bot's
    session/cookies — the bot-reach — the xss-adjacent class
  - a RENDERER — wkhtml/chromium-pdf — render-context — the
    rendered-output IS the channel — screenshot-shape
  - a QUEUE-CONSUMER — the job-handler — the job's permissions
```

The source-ip tells you which — the callback shows the egress-ip —
the worker's position on the network.

## 5. The reach — what the worker can see

```text
the worker's network-position differs from the web's:
  - the web-box reaches the public-internet + the internal-net
  - the worker-box may be internal-only — the egress-shape differs
  - the worker may have DIFFERENT credentials — a worker-role —
    the worker's iam/SA — a different permission-set — the
    worker's metadata may differ from the web's
  - the worker may run with more privilege — a job-runner — the
    worker's own admin-routes
```

The deferred-fetch can reach a DIFFERENT internal-network — the
worker's own loopback/siblings — the sweep must consider the
worker's position not the web's.

## 6. The trigger-control — firing the fetch

```text
the deferred-fetch fires on its trigger — control the trigger:
  - the webhook-fires on the event — generate the event — the
    event-source is often reachable — a comment/post/action
  - the scheduled-job — wait — or find the manual-trigger —
    "run now" / "test" buttons
  - the feed-refresh — the refresh-interval — or a "refresh now"
  - the bot-visit — the report-button — the bot fires on the
    report — the report IS the trigger
  - the verify — the "verify-now" button
```

## 7. The stored-shape — how the url is stored

```text
the storage-shape decides what the fetcher sees:
  - stored RAW → the fetcher parses at fetch-time — the url-tricks
    survive — the check ran at WRITE-time — the fetch-time re-parse
    may differ — the stored-string is the fetch-input
  - stored PARSED → the fields extracted at write — the host/scheme
    split — the parts are stored — the parts-injection
  - stored VALIDATED → the check ran at write — the stored-value
    was approved — the fetch uses the approved-value — unless the
    re-parse differs — the write-time-check + fetch-time-parse
    differential — the stored-string passed the check — the
    fetcher re-parses — the differential-window
  - stored ENCODED → the stored-value is encoded — decoded at
    fetch — the double-decode
```

## 8. The event-driven shape — the webhook-inventory

```text
map the webhook's triggers — which events fire it:
  - on-create, on-update, on-delete — the CRUD-events
  - on-comment, on-like, on-share — the social-events
  - on-login, on-register — the auth-events
  - on-order, on-payment — the commerce-events
  - on-build, on-deploy, on-commit — the ci-events
each event is a fetch-opportunity — the event-payload may carry
  extra-data — the fetch-context per-event differs
```

## 9. The webhook-body — what the fetch carries

```text
the webhook-fetch may carry a BODY the app composes — the
  callback's body shows the app's data — the internal-structure —
  the event-payload — sometimes secrets/tokens — the callback's
  body is intel
the webhook may carry HEADERS — auth-tokens — the callback's
  headers — the app's outbound-headers — a signing-secret —
  the webhook-signature the app sends — verify or forge
```

## 10. The chain — deferred-ssrf to flag

```text
1. the url is stored — fetched by a worker
2. the worker's fetch goes to YOUR listener — the canary proves it
3. register url=http://internal-flag-route → the worker fetches it
   — the RESPONSE goes to the results-channel — the status-page
   or the history — the flag-content lands there
4. OR the worker fetches file:///flag → the file-content lands in
   the stored-result — the deferred-file-read
5. OR the worker is a browser — the bot-visit — the xss-adjacent
   class — the html+js payload — the bot-exfil — different class
```

## 11. The pat-request — the persistence

```text
the stored-url is fetched REPEATEDLY — every view/refresh — the
fetch-fires-per-event — the canary-fires-many-times — each hit is
a probe — the url is "live" — change what it points to? — no —
the stored-url is fixed — but the RESPONSE-SHAPE may vary — the
stored-response is updated per-fetch — the latest-response page
```

## 12. The race-against-schedule — the contest-clock

```text
a nightly-batch won't fire in a 4-hour contest — the deferred-
fetch needs a TRIGGER you control — if the only trigger is a
schedule beyond the contest → the deferred-shape is the wrong
path → pivot to a synchronous-surface or a manual-trigger —
check for "test"/"preview"/"run-now" controls — the dry-run
endpoints
```

## 13. The bot-visit boundary — the class-split

```text
the deferred-fetch is a BROWSER when:
  - the callback's UA is a real-browser — "Mozilla/5.0 Headless"
  - the page runs JS — your html's scripts execute
  - cookies/session ride along — the bot's auth
then the class is bot-visit → web-xss references — the payload
is an html-page — the fetch is a browser-navigation — the exfil
is the bot's-context — NOT the server-fetch — classify right
```

## 14. The deferred-sweep — the bounded probes

```text
- register the canary-url → the hit → the fetch confirmed +
  the schedule + the source-ip + the worker-context
- register url=http://127.0.0.1:1/ → does the worker reach
  loopback? — the WORKER's loopback — different host — the
  refused-error in the results-channel — or silence
- register url=http://internal-route → the result — the flag-page
  the results-channel holds the response — read it
- the deferred-fetch is one mechanism-class — 5-probe budget —
  the queue-worker is the fetcher — the fetcher's own scheme-cap
```
