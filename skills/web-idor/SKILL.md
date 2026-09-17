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
---

# IDOR — Depth Skill

## Recognise

Identifiers that address a resource: a numeric path segment, an identifier in a
query string, a filename that encodes a record number, a field in a JSON body, a
hidden form field, or a claim inside a token. Suspect IDOR whenever a resource
belongs to an identity but the handler looks it up by identifier alone.

## Confirm — two identities are required

1. As identity A, create a resource and record its identifier.
2. As identity B, or with no session, request A's identifier.
3. Reading or writing it proves the finding. One account cannot prove it.

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
