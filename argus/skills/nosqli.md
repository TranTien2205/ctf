# NoSQL injection

**When:** a JSON body value is accepted as an object-shaped filter. Express +
MongoDB is the classic: `req.body` passed straight into `findOne`/`find`.
Signals: 24-hex ids (`ObjectId`), JSON APIs, `$`-operator behavior.

## Detection

Send the same request with the value replaced by an object:

```json
{"user": "admin", "pass": {"$ne": null}}
{"user": "admin", "pass": {"$gt": ""}}
{"user": {"$regex": "^admin"}, "pass": {"$ne": null}}
```

- Login returns a session/different status vs a wrong password = auth bypass.
- `{"$regex": "^a"}` on a username field leaks valid names a char at a time.
- `"id[$ne]=x"` works the same in urlencoded bodies (Express parses it into
  `{id: {$ne: "x"}}`).

## Read-only discipline

- Pin tests to objects YOU created or your own account: `{"_id": "<your id>",
  "$gt": ""}` never reads other tenants' data for a demo.
- `$where` and `$function` execute JavaScript server-side - one benign probe
  (`{"$where": "return true"}` vs `return false`) proves the sink; do NOT
  run extraction loops against a shared instance.

## Falsifier

The object-shaped value is rejected or stringified (400/error about type),
and scalar true/false equivalents show no difference.

## Severity guide

Auth bypass via `$ne`: high. Data read beyond your own objects: high.
`$where` code execution confirmed: critical. Operator accepted but confined
to your own document: medium (broken object-level authorization is the real
finding - see `idor`).
