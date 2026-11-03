---
name: web-nosqli
description: Prove NoSQL injection with documents from a named collection — operator injection in JSON bodies and in query strings, the authentication-bypass shape and its control, bounded blind extraction, server-side JavaScript as a separate class, and the 500 that fools everyone here. Use when a parameter reaches a document store, an ODM or an aggregation pipeline.
classes: nosqli
---

# NoSQL injection

Proof requirement (`./bin/argus proof nosqli`): **at least one document from a
named collection that the query should not have reached.** Two checks, and the
load-bearing one is the name. The verifier reads `extracted.table` (SQL-shaped,
since `sqli` shares it) plus `extracted.rows` or `extracted.row_count`.
Evidence that says "more records came back" without naming where from grades
`unproven` and is not recorded, which is how this class usually fails.

**No engine fingerprint is required here, and `sqli` requires one.** The reason is
written beside it in `argus/ledger/proof.py`: a document store often reports no
version anywhere, so requiring a banner would refuse proofs that are complete. For
`sqli` the fingerprint separates "a database answered" from "a page echoed text";
here the named collection does that. If you do learn the engine — a driver in an
error, a 24-hex `_id` — record it: it belongs in the report, just not in the
grade.

## Two surfaces, two payload shapes

| surface | what you send | why it differs |
|---|---|---|
| a JSON body | `{"user":"admin","pass":{"$ne":""}}` | you replace a scalar with an object: the bug is a query built from parsed JSON with no type check. Send it with `headers={"content-type":"application/json"}` — a raw body goes out form-encoded, and a JSON route then parses nothing |
| a query string | `?pass[$ne]=`, `?pass[$regex]=^a`, `?user[$gt]=` | you cannot send an object, so the framework's parameter parser builds one for you — Express's `qs`, PHP and Rails all do |
| a form body | `pass[$ne]=` | the same parser, often on a different route than the JSON API |

If `pass[$ne]=` changes the answer and a literal `pass=$ne` does not, the parser
is as much the finding as the query. The operators, and what each one asks:

| operator | the question |
|---|---|
| `$ne`, `$gt` — or `$in`, `$nin` when those two are filtered | does a comparison become an operator: the cheapest discriminating probe |
| `$exists` | which fields exist: how you learn the schema well enough to name a collection |
| `$regex` | can I ask one question per character — the blind extraction primitive |
| `$where`, `$expr`, `$function`, `mapReduce` | is server-side JavaScript enabled, which is a different class |

## The authentication bypass is two classes from one pair of requests

`{"user":"admin","pass":{"$ne":""}}` returning a session is `nosqli` — the query
reached the admin document — and also `auth-bypass`, whose requirement is
stricter: a credential accepted, a deliberately invalid one **rejected**, and
privileged content returned. Take that control in the same breath:

```
ledger.add_evidence kind=probe vuln_class=auth-bypass hypothesis_id=hy-...
  record={"token_accepted":true,"privileged_marker":"<what only admin sees>",
          "payload":"{\"user\":\"admin\",\"pass\":{\"$ne\":\"\"}}"}
ledger.add_evidence kind=control vuln_class=auth-bypass hypothesis_id=hy-...
  record={"is_control":true,"token_accepted":false,"payload":"pass=argus<nonce>"}
```

Without the control you have not ruled out an account with no password set, a
much smaller finding. Open both hypotheses: one request pair, two requirements.

## Blind extraction, bounded to the proof

When the answer is only yes or no, `$regex` is the oracle:
`{"pass":{"$regex":"^a"}}` narrows a character at a time, and
`http.differential repeat=2` keeps a length change under the noise floor from
being read as a bit. Anchor with `^`, escape what you recovered, or it lies.

Then stop at the proof. One document from a named collection is the requirement; a
hash recovered character by character is not more proof, it is more collected data
you have to justify. Above five rows in one record `extraction stayed minimal`
fails: still `proven`, but the failed check prints under the finding in the report.

An injected aggregation pipeline is the same proof with more reach: a `$lookup`
joins a collection the endpoint was never meant to touch, `$group` or `$project`
return fields the route filtered out. The collection you name is the severity.

## Server-side JavaScript is the rce class, with the rce proof

`$where`, `$expr`, `$function`, `$accumulator` and `mapReduce` evaluate JavaScript
in the engine, which is not code execution by itself: that JavaScript usually has
no process and no filesystem, so you may hold evaluation, not a shell. Report —

- a command's output with the nonce, through `proof.exec_marker` → `rce`
- a nonce-derived arithmetic result the engine computed, through
  `proof.template_eval expression_template={a}*{b}` → the `ssti` shape, honest
- documents reached by a `$where` that should not have matched → `nosqli`

— and never a long sleep inside `$where`: it runs once per document, so the cost
is the collection size times the delay. `dos` is refused here for the same reason.

## A 500 from a malformed operator is the most common false signal here

`{"$nonsense":1}` throws in the driver, in the ODM, in a validation layer or in
the route handler, and from outside all four look identical. So every operator
probe carries two companions: a **valid** operator that should change nothing —
`{"$eq":"<the value the baseline sent>"}`, which must answer exactly like the
baseline — and a plain scalar, so you know what a wrong value looks like. Three
requests, and now a status change means something. The pair a filter cannot fake
is the boolean one, as in `sqli`: `{"$ne":""}` against `{"$ne":"<the real
value>"}` are equally suspicious, and only the application knows the difference.

## What does not count

- A 500 on `{"$ne":""}`, or a login that succeeds with it and no rejection
  control: the account may have had no password. More documents than the
  baseline, with no collection named.
- A JSON object accepted where a string was expected: type confusion is the
  precondition. `$where` with a sleep in it: processing time, and nothing else.
- A `scan.nuclei` template match: every result it returns says candidate.
- `exploit.sqlmap`: a SQL tool with no mode for a document store, so pointing it
  at one spends probe budget to learn nothing.
