---
name: web-authz
description: Prove IDOR and broken access control with two identities and an entitlement control — cross-reads, the 404-versus-403 distinction, and tenancy. Use when an object id, a user parameter, a tenant header or a path segment names whose data is returned.
classes: idor
---

# Authorization: IDOR, BOLA, tenancy

Proof requirement: **actor A reading actor B's subject, with the control showing
A is not entitled to it.** The identities in the evidence must differ, the record
must name both the actor and the subject it reached, and the outcomes must
differ.

## You need two accounts, and there is no way around it

Not two ids — two **identities**. With one account, `id=2` returning data proves
only that `id=2` exists. The comparison that carries the claim is:

| request | expected | what it fixes |
|---|---|---|
| A reads A's object | 200 | the endpoint works and A is entitled to something |
| A reads B's object | **200 = the finding** | the authorization gap |
| unauthenticated reads B's object | 401/403 | that authentication is required at all |
| A reads an object that does not exist | 404 | that 200 is not the generic answer |

The third and fourth rows are the control. Record them with
`ledger.add_evidence kind=control is_control=true`.

If the client gave you one account, ask for a second before probing. An
engagement that reports IDOR off one account reports a guess.

## Recording it so the matrix can grade it

`http.probe` takes `actor`. The cross-read record also needs
`accessed_subject` — whose data came back — and that usually cannot be inferred
from the response, so add it:

```
ledger.add_evidence kind=probe vuln_class=idor hypothesis_id=hy-...
  record={"actor":"alice","accessed_subject":"admin",
          "response":{"status":200,"body_span":"<the record that proves whose it is>"},
          "summary":"alice received the note owned by admin"}
```

The `body_span` must contain the thing that identifies the owner. "It returned
200" is not evidence of whose data it was.

## Where the identifier hides

Beyond `?id=`:

- a path segment: `/api/v2/accounts/4711/statements`
- a JSON body field, including one nested three levels down
- a header: `X-Tenant-Id`, `X-Account`, `X-Impersonate`
- a cookie that is a primary key rather than a session
- a GraphQL `node(id:)` or a batched query with several ids
- a **filename** in an export or upload path
- an id that is a UUID — unguessable is not the same as authorized, and UUIDs
  leak constantly through list endpoints, notification emails and shared links

## Shapes that look like IDOR and are not

- **404 everywhere.** If the object does not exist for anyone, nothing was read.
- **A shared resource.** Some objects are intentionally public; check the product
  before claiming it.
- **A 200 with an empty body.** The authorization check ran, the response shape
  did not change. Match on content, not on status.
- **Your own object with a different id.** Two accounts in the same tenant with a
  shared workspace is a configuration, not a flaw.

## Function-level, not just object-level

The same discipline applies to actions: can A perform B's privileged operation?
That is a state change, so the proof is the `csrf`/business-logic shape — read
before, act, read after, and the acting identity must be one that should not have
been able to. Three records, and the "after" read is the one that proves it.
