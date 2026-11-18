# Second-order smuggling — the stored/delayed desync

## The shape — the smuggle lands on a DELAYED request

A classic desync poisons the IMMEDIATE next request — second-order
smuggle stores the poison for a LATER trigger:

- a stored value that becomes part of a later request's framing
- an async job that constructs a request from a stored payload
- a cached entry that feeds a later fetch

## The stored-body — the smuggle inside a stored param

```text
POST /comment HTTP/1.1
Content-Length: 200

text=A%0d%0a%0d%0aPOST%20/admin%20...
```

The comment's `text` stores the CRLF-fold — a later request that
interpolates `text` into a fetch → the fold lands then — a stored-CRLF.

## The stored-header — the stored `User-Agent`/`Referer`

```text
User-Agent: x%0d%0aX-Injected:%201
```

The UA stores — a later log/notify request interpolates it → the fold
lands on the internal request.

## The async-job smuggle — the job that builds a request

A webhook/callback/async-job that constructs a request from stored
params — the smuggle stored → the job's request carries the fold —
`webhook-deferred.md`-style.

## The template-stored — the stored SSTI-adjacent

A stored value that lands inside a template — the template's output
becomes part of a request — the fold inside — `../web-ssti/`.

## The cache-delay — the smuggle's cached response

The smuggle's response caches → the poison lands on every subsequent
visitor — `cache-poison-via-smuggle.md` — a delayed-queue-poison.

## The queue-drain — the smuggle that lands hours later

On a slow-draining queue the smuggle's prefix sits in front of the
next request — hours later — the poison is delayed until the queue
drains.

## The detection — the delayed readback

```text
store the smuggle → trigger the async job → read the job's output
```

The job's output carries the smuggle's effect — the delayed readback —
`response-poisoning.md`.

## The common second-order sinks — the checklist

- a stored comment/name/bio interpolated into a later request
- a stored `User-Agent`/`Referer` in a log-request
- a webhook/callback URL interpolated at job-time
- a template-rendered value in a request's framing
- a cached entry keyed on the smuggle's path
