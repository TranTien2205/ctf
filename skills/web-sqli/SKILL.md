---
name: web-sqli
description: Find, confirm and minimally prove SQL injection — the quote differential, the boolean pair, the control, sqlmap in detect/enumerate/extract, second-order and blind cases. Use when a parameter may reach a SQL query, when a 500 appears on a quote, or when sqlmap reports nothing but the signal looks real.
classes: sqli
---

# SQL injection

Proof requirement: **the DBMS fingerprint plus at least one row from a named
table.** Five rows is a proof. A full dump is an incident, and the broker caps
extraction at twenty rows for that reason.

## The three measurements that decide it

In this order, because each is cheaper than the next:

1. **Quote differential.** `http.differential` baseline `id=1` vs variant `id=1'`,
   `repeat=2`. A status change is a real difference. A length change under 24
   bytes with similarity above 0.98 is noise — the tool will say so, and a page
   with a CSRF token or a timestamp differs from itself on every request.
2. **Boolean pair.** `id=1 AND 1=1` vs `id=1 AND 1=2`. This is the one a WAF
   cannot fake by echoing: the two payloads are equally suspicious, so a filter
   treats them the same and the *application* does not.
3. **The control.** `id=<a value that certainly exists>` and
   `id=<a value that certainly does not>`. Now you know what "found", "not
   found" and "broken" each look like. Without this, a 500 on a quote is just a
   500.

## What a signal is not

- A 500 on `'`. Plenty of code crashes on a quote without reaching SQL.
- A timeout. That is evidence about processing time and nothing else.
- `sqlmap` saying `might be injectable`. Read it as a hint to look again.
- An error containing the word SQL. Error text is written by whoever wrote the
  error handler.

## sqlmap, in three modes and in this order

```
exploit.sqlmap mode=detect   target="http://t/item?id=1" param=id level=1 risk=1
exploit.sqlmap mode=enumerate target="http://t/item?id=1" param=id
exploit.sqlmap mode=extract  target="http://t/item?id=1" param=id table=users rows=5
```

Raise `level` and `risk` only after `detect` finds nothing *and* your own
differential said there was something. Level 5 risk 3 on a parameter with no
signal is how an engagement spends an hour and a thousand requests on a
parameter that was never injectable.

`--os-shell`, `--file-write`, `--sql-query` and friends are not reachable through
the broker. If you want to show code execution from a SQL injection, that is the
`rce` class and its own proof: `proof.exec_marker`, one benign command, nonce.

## Blind, and why the nonce matters anyway

A boolean-blind injection still ends in an extraction: `sqlmap mode=extract`
reads the table one bit at a time and the evidence is the same shape. For a
time-based case, measure with `repeat=3` and compare against a `sleep 0`
equivalent — one slow response is a slow endpoint, three paired ones are a
mechanism.

## Second-order: the sink is not where you typed

The input is stored on one request and used on another. Three things make it
findable:

- the differential is on the **second** page, not the one you submitted to
- a nonce in the stored value tells you which record you are looking at, and
  whether the page you are reading is yours at all
- the write path matters: read who stores it before concluding the parameter is
  clean. An input that fails every probe at the point of entry is not closed
  until you have found where the value is read back.

## The extraction that proves without over-collecting

Target the smallest table that establishes read access to data the caller should
not have: a users table's `id, username` is enough, and leaves the password
column out of your evidence file. Name the table in the evidence. The ledger
stores at most five rows per record and refuses `extraction stayed minimal`
otherwise, which keeps a proof from becoming a breach of its own.
