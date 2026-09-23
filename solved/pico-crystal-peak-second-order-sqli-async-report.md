# crystal-peak (picoCTF) — SOLVED (hint-assisted)

- Platform: picoCTF. Flask/Werkzeug 3.0.6, Python 3.8.10, SQLite, pandas.
  `http://crystal-peak.picoctf.net:<port>/` — the instance is short-lived and was
  re-spun four times during this work.
- Date: 2026-09-23
- Flag: redacted; read from the CSV my own injected report produced.
- Assistance: the operator supplied the hint "what does order in SQL injection
  mean?", which is what redirected the search. Recorded here as assistance.

## The app

"Expense Tracker": `/signup`, `/login`, `/logout`, `/dashboard`, `/expenses`
(with `?page=`), `/inbox`, `/generate_report`, `/download_report/<int:id>`,
`/delete_expense/<int:id>`. Nothing else — confirmed by ffuf.

Generating a report is **asynchronous**: the POST returns immediately with
"Check your inbox after 10 seconds!!!", and about 12 seconds later a row appears
in `/inbox` pointing at `./reports/report_{username}_{int(time.time())}.csv`.

## The bug: second-order SQL injection through the username

The username is stored at signup and only reaches SQL later, inside the
background report job, where it is interpolated into the SELECT that builds the
CSV. A UNION in the username therefore injects into a query whose result **is**
the downloadable report.

```
username: v7' UNION SELECT name||'='||value,42,1 FROM aDNyM19uMF9mMTRn--
CSV:      description,amount,date
          flag=picoCTF{...},42,1
```

Three columns, because the report selects `description, amount, date`. The `42`
is a marker chosen so the row is provably from my own injection.

Enumerating first:

```
UNION SELECT name,type,1 FROM sqlite_master--
  -> users, expenses, reports, inbox, sqlite_sequence, aDNyM19uMF9mMTRn
```

`aDNyM19uMF9mMTRn` is base64 for **`h3r3_n0_f14g`** — "here no flag". It is a
joke: that table is exactly where the flag lives, in a `(name, value)` pair.

## Why this took so long to find

Every direct test of the username came back clean, because **the username never
touches SQL during the request that carries it**. Quotes in the username left
`/login`, `/expenses`, `/inbox` and `/dashboard` all answering 200. The injection
only fires later, in a job whose only visible output is a CSV I had to go and
download. Checking status codes was the wrong oracle; the report content was the
right one.

Ruled out along the way, each with evidence: pickle cookie (the session is a
plain Flask signed cookie holding `{"username": ...}`); SSTI (`{{7*7}}` stored
verbatim); SQLi in `page` (all malformed values fall back to page 1); SQLi in
`download_report` and `delete_expense` (both `<int:>`, 404 on anything else);
command injection through the username (`$(sleep 8)` landed literally in the
filename and cost no time); hidden parameters on `generate_report`; seeded
users or reports; exposed files.

## Two other real findings

- **IDOR on `/download_report/<id>`**: no ownership check at all. One account
  downloaded another's report and read its contents. This is what exposed
  another player's injection attempts on the shared instance, which is how the
  `sqlite_master` table name first became visible.
- **Path traversal through the username is blocked, but only by accident.** The
  path is `reports/report_{username}_{ts}.csv`, so the first path segment is
  always `report_<prefix>`. pandas rejects it with a message that is stored in
  the inbox and reflected verbatim:
  `Cannot save file into a non-existent directory: 'reports/report_../../../nonexistent'`.

## Reusable lessons

- **A clean direct test does not clear an input.** Second-order injection means
  the payload is stored now and executed later, by a different code path. Test
  every place a stored value is *consumed*, not just where it is submitted.
- **Pick the oracle the bug actually speaks through.** Here the SQL ran in a
  background job whose only channel was a downloadable CSV, so HTTP status codes
  and page lengths were structurally incapable of showing it.
- **Row order is invisible to a size-based fuzz.** An early hunt for an ORDER BY
  parameter used `ffuf -fs <baseline>`; a sort parameter changes order, not
  length, so that filter would have discarded a hit along with the noise. The
  replacement compared the sequence of marker rows instead.
- **Another player's artifacts on a shared instance are a lead, not evidence.**
  Their report was visible through the IDOR and revealed the table name, but the
  flag was only accepted here after reproducing it with an injection of my own
  carrying a distinguishing marker.
