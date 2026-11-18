# Webhook-deferred — the async smuggle

## The shape — the smuggle inside a deferred request

A webhook/callback/async-job constructs a request LATER from stored
params — the smuggle stored → the deferred request carries the fold —
`second-order.md`.

## The stored-URL — `webhook_url` interpolated at job-time

```python
job.run(callback=f"http://{user_host}/cb")
```

The `user_host` stored raw — `%0d%0a` inside it folds when the job runs —
the deferred request carries the injected header/body — the fold lands
on the job's socket, not yours.

## The job-runner's internal network — the smuggle's target

The deferred request runs on the job-runner — often a DIFFERENT host
with internal-network access — the fold reaches an internal endpoint
your direct request couldn't — `internal-routes.md`.

## The readback — the job's output

```text
store the smuggle → trigger the job → the job's output/log carries the effect
```

The job's response isn't yours — read the job's log/output — the
deferred readback — `response-poisoning.md`.

## The queue-position — where in the job the fold lands

The stored param's position inside the deferred request determines
what the fold injects:

- inside the URL → header/body fold
- inside a header → header-fold only
- inside the body → body-fold or a stored-body

## The common sinks — the async builders

- `requests.get(f"http://{host}/cb")` — the webhook URL
- `celery.send_task(url=...)` — the task URL
- a `curl` subprocess with a stored URL
- a `urllib.request.urlopen` with a stored param

## The defensive — is the URL validated at job-time?

A stored URL validated at SAVE-time may pass — the job-time fetch may
not re-validate — the fold survives into the deferred request.

## The evidence — the job's output carries the fold

The job's log/output shows the injected header/body landed — the
deferred-request's response or error carries the fold's effect.
