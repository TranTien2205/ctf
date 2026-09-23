# Expense Tracker — SOLVED (self-solved)

- Platform: picoCTF. Flask / Werkzeug 3.0.6, Python 3.8, SQLite.
- Date: 2026-09-23
- Target supplied: `http://crystal-peak.picoctf.net:<port>/` (black-box, instance per player)
- Flag: redacted; read from the generated CSV downloaded over the live target
- Cost: 4 probes, ~4 minutes once the shape was named.

## Chain

1. Register and log in. Signup needs three fields — `username`, `email`,
   `password`; omitting `email` returns a bare `400 Bad Request`, which reads
   like a broken request rather than a missing field.
2. Authenticated surface: `/dashboard`, `/expenses`, `/inbox`, `/logout`,
   `POST /generate_report`, `GET /download_report/<id>`.
3. `POST /generate_report` answers
   *"Report generation requested successfully! Check your inbox after 10 seconds!!!"*
   — the work happens in a **background worker**, not in the request. Ten seconds
   later `/inbox` holds a row pointing at `./reports/report_<USERNAME>_<epoch>.csv`.
   The stored username is interpolated into the job: that is the second-order
   surface, visible before any payload is sent.
4. Register a second account whose username ends in a single quote (`soQ2'`).
   Signup and login both succeed — the INSERT is parameterised and safe. The job
   then fails, and `/inbox` shows the reason in plain text:

   ```
   Report generation failed. Cause unrecognized token: "'soQ2''"
   ```

   `unrecognized token` is SQLite, and the doubled quote shows the stored
   username being concatenated inside a single-quoted literal by the worker.
   The error is rendered in the inbox, so this is **error-based, not blind**.
5. The report CSV has three columns — `description,amount,date` — so the column
   count for a UNION is known without probing for it. Register a username
   carrying the payload:

   ```
   u1' UNION SELECT sql,1,1 FROM sqlite_master--
   ```

   The CSV comes back holding the whole schema.
6. Tables: `users, sqlite_sequence, expenses, reports, inbox, aDNyM19uMF9mMTRn`.
   The last name is base64 for `h3r3_n0_f14g` ("here no flag") and carries
   `name TEXT PRIMARY KEY, value TEXT NOT NULL`.
7. `u3' UNION SELECT group_concat(name||' => '||value,' ~~ '),1,1 FROM aDNyM19uMF9mMTRn--`
   returns `flag => picoCTF{...}` in the CSV.

## Also found, not needed for the flag

`GET /download_report/<id>` takes a sequential id and enforces no ownership
check. As user `probe2` holding report id 3, `/download_report/1` returned
another account's CSV. A straightforward IDOR sitting beside the intended bug.

## Reusable lessons

- **"Check back in N seconds" is the tell for second order.** The moment a
  response defers work to a worker and a stored value appears in the artifact
  path, the sink is in another code path and another moment. Look there before
  fuzzing the request that stored the value.
- **The registration username is the carrier.** It is stored early, it is long
  lived, and it is read by code that never expects an attacker to have chosen it.
  It is also uniqueness-checked, so every payload needs a distinct prefix.
- **Two accounts is the whole detection step**: one plain, one with a single
  quote. Run the job for each and compare. One request pair separates
  "parameterised everywhere" from "concatenated somewhere later".
- **Read the artifact's own column count.** The CSV header already said three
  columns, so `ORDER BY` probing to find the column count was unnecessary — and
  would have cost one 10-second job cycle per guess.
- **A table named "no flag here" is where the flag was.** Enumerate it anyway;
  the name is attacker-facing text and costs nothing to check.
- The username also lands in the report filename, so a payload containing a path
  separator risks breaking file creation rather than the query. Spaces, quotes
  and `--` were all tolerated here.
