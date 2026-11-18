# Second-order SSRF — the stored, transformed, and re-fetched url

The url is written, stored, transformed, then fetched in a
different context — the input-check ran at WRITE-time, the fetch
happens later under different rules. The gap between write-check
and fetch-parse is the whole attack.

---

## 1. The second-order shapes — where the url sleeps

```text
- profile-fields — avatar-url, homepage-url, website — stored in
  the user-record — fetched on display/export/sync
- webhook/callback configs — stored — fired on events
- feed/rss-sources — stored — the feed-reader polls them
- import-jobs — a stored job-spec with a url — runs on schedule
- bookmark/read-later — the stored-item — rendered later
- config-entries — a stored setting naming a url — api_url,
  webhook_url — used on the next operation
- document-contents — a url inside a stored doc — the doc-renderer
  fetches it when displayed
- the template-field — a stored template containing a url — the
  render-fetch
```

## 2. The check-vs-fetch gap — the differential

```text
write-time:  the url-input is validated → stored
fetch-time:  the stored-value is re-parsed and fetched

the gap: the STORE may transform the value —
  - normalization — the url re-serialized — "http://internal" might
    survive or be canonicalized differently
  - field-split — stored as host/port/scheme — reassembled at
    fetch — the parts-injection — the host-field carries extra
  - encoding — stored encoded — decoded at fetch — double-decode
  - the fetcher differs — the WRITE-context's parser ≠ the
    FETCH-context's fetcher — the two-parser game on a delay
```

## 3. The stored-then-reparsed differential

```text
the check runs on the input; the fetch re-parses the stored-string:
  write "http://example.com@internal/" → validator sees host=
    example.com → stores the STRING
  fetcher parses the stored-string → its parser may split the @
    differently → fetches internal
the write-time-check is one parser; the fetch-time-parse is
another — the stored-string is the carrier
```

## 4. The partial-storage — the parts-injection

```text
the url is stored as FIELDS — host, port, path — the reassembly:
  store: url=http://internal:6379/_PING →
         host=internal, port=6379, path=/_PING
  fetch: http://{host}:{port}{path}
         → http://internal:6379/_PING — works
  inject the PARTS: host=internal, port=6379, path=
         — the port-field carrying "6379/x" — "internal:6379/x" —
         the port-isn't-integer — the port-field as a url-segment
```

## 5. The display-time fetch — the reader-context

```text
the url is stored, then ANOTHER user/system views it — the
view-context fetches it — the fetch is in the VIEWER's context —
  - an admin-view → the admin's session on the fetch — the
    read-as-admin
  - a render-worker → the worker's reach
  - a report-generator → the report-fetch
the stored-url + the display-fetch = the second-order-channel —
the check ran on you at write — the fetch runs as the admin at
view — the admin's fetch-privileges are the target
```

## 6. The transform-chain — the data-flow

```text
url → store → transform → fetch — the transform is the key:
  - a template-render on the stored-value — the stored-string
    goes through a template → the ssti-boundary — the url-field
    as template-input — different class
  - an xml/json re-serialization — the stored-value re-encoded —
    entity-expansion, json-escapes
  - a redirect-resolution — the app resolves the url's redirects
    at write-time — stores the FINAL url — the re-check on the
    final — or the original is stored and the fetch re-follows
```

## 7. The "the url was already checked" assumption

```text
the trust-model: "the url was validated when stored — the stored-
value is safe to fetch" — the check ran ONCE at write — the
re-fetch re-uses the stored-value blindly — the stored-value is
the attacker-controlled-input that passed once — the write-time
context is gone at fetch-time — the fetcher's environment may
differ — different dns, different proxy, different position
```

## 8. The provenance — tracking the url's journey

```text
the url-input's lifecycle:
  input → validate → store → retrieve → transform → fetch
each arrow is a check-point or a transform — the differential
lives between any two — the questions:
  - does validation run once or per-fetch?
  - does the store normalize the string?
  - does the fetcher use the stored string or a re-composed one?
  - is the fetch-context the same process/host as the input-
    context?
```

## 9. The stored-shape chains — the concrete chains

```text
chain-A: profile-url → stored → admin-view → admin's-fetch —
  the admin-viewer fetches your-url as the admin — the admin's
  session/context — the "fetch as admin" — reaches what admin-
  context reaches — the flag-route the admin-only can see
chain-B: feed-url → stored → cron-fetch → stored-result → the
  results-page — the deferred-fetch — the response-surfaces
  later — the stored-response is the channel
chain-C: webhook → stored → event-fires → the worker-fetches —
  the worker-context — the deferred — the results go to a queue/
  status-page
chain-D: config-url → stored → the NEXT operation uses it — the
  config-driven-fetch — the "change the api-url the app calls" —
  the app calls YOUR url — or the internal-api — the config-write
  is the persistence
```

## 10. The write-check + read-check split

```text
the write-check is strict; the fetch is unguarded → the bypass is
at write — pass the check once, the fetch is free
the write-check is loose; the fetch is strict → the stored-value
can't reach — the write passes garbage — the fetch rejects
the asymmetric-checks — the write allows what the fetch refuses —
the stored-value that satisfies BOTH — the intersection — the
write-check's leniency vs the fetch-check's strictness
```

## 11. The enum-of-stored-urls — the existing-records

```text
other-users' stored-urls — the profile/feed/webhook of OTHERS —
  the enum — idor-adjacent — the stored-urls are fetchable via
  the admin-view or the record-list — the existing-stored-urls
  are intel — where do other-urls point?
```

## 12. The second-order + the first-order split

```text
the stored-url + an immediate-fetch + a deferred-fetch — the
SAME url goes to two fetches — the input-check passes one —
the second-fetch under different rules — the two-fetch differential
— the write-fires-an-immediate-preview + a later-batch — the
immediate-fetch is the check — the batch is the real-fetch —
the batch-context differs
```

## 13. The persistence — the url that stays

```text
the stored-url persists — every view fires it — a permanent
fetch-channel — the stored-ssrf is a recurring-probe — the canary
fires on every event — the per-event hits map the schedule
```

## 14. The falsifier — when second-order isn't ssrf

```text
- the stored-value is never fetched — the field displays raw —
  not a fetch — xss-surface not ssrf
- the stored-value IS fetched but re-validated each fetch — the
  per-fetch check — no gap — the fetch-time check controls —
  the differential dies
- the store-sanitizes — the stored-value is canonicalized — the
  re-serialized form is safe — the transform cleaned it
```
