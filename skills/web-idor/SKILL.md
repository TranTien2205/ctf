---
name: web-idor
description: >
  Insecure direct object reference. Use when object identifiers appear in a path,
  query, body, token or hidden field and ownership may not be enforced. Routes to
  references/ for enumeration and identifier-analysis depth.
tags: [web, idor, access-control, authorization, broken-auth]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "no privilege difference between identities"
    - "identifier sweep past 200 with no pattern and no new signal"
evidence_level: catalogue
---

# IDOR — Depth Skill

**Catalogue class.** This toolkit has never solved one; the content below is
standard published knowledge, not local experience.


## Recognise

Identifiers that address a resource: a numeric path segment, an identifier in a
query string, a filename that encodes a record number, a field in a JSON body, a
hidden form field, or a claim inside a token. Suspect IDOR whenever a resource
belongs to an identity but the handler looks it up by identifier alone.

## Confirm — two identities are required

1. As identity A, create a resource and record its identifier.
2. As identity B, or with no session, request A's identifier.
3. Reading or writing it proves the finding. One account cannot prove it.

**Falsifier:** the handler scopes the lookup to the authenticated owner, and
identity B cannot read or modify identity A's object through the tested route.

## Operational probe

Use two sessions and keep the object read-only:

```bash
# identity A creates an object and records the observed id
curl -i -b a.cookies "$BASE/api/items"
# identity B requests the exact id, without changing the object
curl -i -b b.cookies "$BASE/api/items/<id-from-A>"
```

For sequential ids, test one adjacent id, not a sweep. For opaque ids, use an
id returned by the application for identity A. Record status, response length,
and an ownership marker from both sessions. Confirmation requires B to read or
modify A's object and the response to contain attributable object data. A 200
empty wrapper, a public object, or a guessed id is not confirmation.

For an update endpoint, first send the same request to A's own object and then
repeat it against B's object only if the first request is reversible. Do not
modify another player's data as the first probe.

Sequential identifiers: step by one. Opaque identifiers: collect the ones the
application hands out; time-ordered formats are predictable —
`references/uuid-analysis.md`.

## Vectors worth trying

- API and GraphQL: request another identity's record directly, including through
  a nested query.
- File paths: a download parameter naming another record, optionally combined
  with traversal.
- Token claims: change the subject or role field and see whether the signature is
  actually checked — then go to `../web-auth-session/`.
- Mass assignment: add an owner or role field to an update body.
- Filter bypass: change the method, change the content type, or try the
  alternative routing headers the framework honours.

## Route to depth

If the identifier shape is unclear, open `references/README.md` first. Choose
one named reference; do not load the whole directory.

| Shape | File |
|---|---|
| Sequential identifiers | `references/sequential-enumeration.md` |
| Opaque or time-ordered identifiers | `references/uuid-analysis.md` |
| API endpoints | `references/api-idor.md` |
| File-based references | `references/file-idor.md` |
| Bulk sweeps | `references/enumeration.md` |

## Discipline

- Two identities or it is not proven.
- No privilege difference between roles usually means this is not the bug —
  change layer rather than sweeping more identifiers. See
  `../LOOP_DISCIPLINE.md`.
- On a shared instance, read another identity's record; do not modify it.
- A token claim or numeric id is only an identifier signal; ownership must be
  tested with a second identity.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
