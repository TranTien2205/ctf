# Pod Diagnostics — HackTheBox (web)

Flag: recorded in `challenges/pod_diagnostics/state.json` via `tools/hooks.py pre-flag`
(live response, the chunked `/stats` cache channel, decoded locally).
Assistance: self-solved from the handout; no writeup search.

**Not the intended ending.** The flag text names class pollution, and
`report.py:20` does hold that bug, but this solve never exercised it. The
terminal step here was reading `/flag` through the renderer, which is a
shortcut, not the designed path. See "What was left unexercised".

## Layout

nginx:80 in front of three services — Flask/gunicorn on 3000, a stats service on
3001, a puppeteer PDF service on 3002. `conf/supervisord.conf` gives no `user=`
to any program and `[supervisord] user=root`, so **every service, including
Chrome, runs as root**. `/flag` is `chmod 400` root-owned and there is a setuid
`/readflag`, which turns out to be unnecessary precisely because the renderer is
already root.

`entrypoint.sh` writes `ENGINEER_USERNAME=engineer` and a random 32-character
`ENGINEER_PASSWORD` into `/app/services/web/.env`.

## 1. The cache key is one query argument

`conf/nginx.conf`:

```
location = /stats {
    proxy_cache stat_cache;
    proxy_cache_key "$arg_period";
    proxy_cache_valid 200 15s;
    proxy_pass http://127.0.0.1:3001;
}
```

`$arg_period` is the **first** `period` argument and nothing else. Express turns
a repeated `period` into an array, which fails
`validPeriods.hasOwnProperty(period)` and lands in the error branch, where
`stats/index.js:21` interpolates it raw:

```js
error: `<strong>${period} is invalid.</strong> Please specify one of the following values: ...`
```

`static/js/stats.js:39` assigns that field to `innerHTML`. So a request with
`period` given twice is stored under the key of the first value and carries the
second into the DOM of everyone who later asks for it.

The index page's dropdown defaults to its first option, so the page always
fetches `period=1m`.

**The entry has to be absent for the poisoning request to reach upstream.**
The first attempt was served from the existing `1m` entry — identical `takenAt`
proved it was a hit, not a poisoning. Waiting out the 15s validity and then
sending the request works.

## 2. The renderer drinks it

`GET /generate-report` (no auth) makes Flask call
`http://127.0.0.1:3002/generate?url=http://localhost/`, and `pdf/pdf.js` opens
that with puppeteer. The page loads `stats.js`, which fetches
`/stats?period=1m`, hits the poisoned entry, and writes the payload into
`innerHTML`. `innerHTML` does not run `<script>`, so the payload is an event
handler.

`page.goto` has `timeout: 10_000`; a run with one nested render took 9.0–9.7s,
so there is very little slack. `waitUntil: "networkidle0"` works in our favour:
puppeteer waits for the payload's own requests before printing.

## 3. Reading the flag

`pdf/index.js` sets `Access-Control-Allow-Origin: *`, so script on
`http://localhost` may call the PDF service directly and read the response —
including with a `file://` URL. Chrome is root, so
`generate?url=file:///flag` returned **200 and a 10194-byte PDF**. Status alone
is the oracle: an unreadable path makes `page.goto` throw and the service
answers 500.

## 4. Getting bytes back without a listener

The same cache is the exfiltration channel: a request to
`/stats?period=<key>&period=<data>` stores `<data>` under `<key>`, and
`/stats?period=<key>` reads it back. Base64url keeps the payload URL-safe, and
4500-character chunks stay inside nginx's 8k request-line buffer. Four chunks
carried all 13592 characters; the reassembled file matched the 10194 bytes the
probe had reported.

**Do not read an exfiltration key before the payload writes it.** A read of an
unwritten key caches the "is invalid" body under that key for 15s, during which
the payload's write is a cache hit and is never stored. Because
`/generate-report` blocks until the PDF is finished, and `networkidle0` waits for
the payload's writes, every key is already populated when that request returns —
so read only then.

## 5. Chrome PDFs do not contain their text

The PDF is not searchable: Chrome subsets the font and writes glyph ids, so
`b"flag" in pdf` is false. But the same file carries the `ToUnicode` CMap that
maps them back. `pdftext.py` inflates every stream, builds the code→character
table from `beginbfchar`/`beginbfrange`, and maps the hex strings in the content
stream. Validated offline first, against a local Chrome render of a known
marker, before any of it was pointed at the target:

```
glyph table entries: 45
recovered: 'HTB{REDACTED}9/23/26, 1:32 PM...'
```

and then on the recovered file:

```
glyph table entries: 23
recovered: 'HTB{REDACTED}'
```

## What was left unexercised

`report.py:20`:

```py
def merge(source, destination):
    for key, value in source.items():
        if hasattr(destination, "get"): ...
        elif hasattr(destination, key) and type(value) == dict:
            merge(value, getattr(destination, key))
        else:
            setattr(destination, key, value)
```

`Report.update` calls it on the raw POST body, so `POST /report` reaches an
unrestricted recursive `setattr` — walkable through `__class__` and `__init__` to
`__globals__`, which is a dict and therefore assignable. That is Python class
pollution against a root gunicorn, and the flag text says it is the intended
route. It needs the engineer password, which the renderer could have read out of
`/app/services/web/.env` by exactly the mechanism used for `/flag` in step 3.
This solve stopped at the flag instead, so nothing here claims that pollution
worked — it was read, not run.

`Report.render()` is also worth noting: it builds a `jinja2.Template` directly,
so autoescape is off, and `index.html:60` prints it through `| safe`. A stored
report title is therefore raw HTML in the page the renderer prints. Also not
exercised, for the same reason.

## Traps

* The poisoning request must arrive while the entry is absent, or it is served
  from cache and nothing is poisoned. Compare `takenAt` to tell a hit apart.
* A longer window is not available: validity is 15s and `inactive=10s`.
* `innerHTML` does not execute `<script>`.
* The outer `page.goto` timeout is 10s and a nested render eats almost all of it.
* Reading an exfiltration key too early blocks the write for 15s.
* A Chrome PDF has no plain text in it; use the CMap the file already carries.

## Cleanup

Nothing persistent was written — no files, no database rows, no accounts. The
only state touched was the nginx cache, and every entry has a 15s validity.
Verified: 20s after the run, `GET /stats?period=1m` returned a normal
`"success":true` body.
