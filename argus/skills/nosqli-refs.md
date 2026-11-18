# NoSQL injection — depth reference

Load when `probe_nosqli` confirmed the request value stays an object and
reaches a query. Keep first probes read-only and scoped to a record you
created or can identify.

## Operator table

| Operator | Effect | Safe first use |
|---|---|---|
| `$ne`, `$gt` | alter equality/comparison filters | query only your own record |
| `$regex` | prefix/boolean oracle | against a known field on your record |
| `$where` | server-side JS predicate where enabled | confirm support read-only |
| `$exists` | field-shape probing | read-only |
| `$rename`, `$set`-adjacent | write-shaped | never fire on a shared collection — see blast radius |

## Authentication filters

Compare a normal scalar `{"user":"x","pass":"y"}` against an object-valued
`{"user":"x","pass":{"$ne":1}}` on a disposable account — the *resulting
identity* is the proof, not the 200. Verify the bypass on a protected
read-only endpoint before reporting auth bypass; a session that exists is
not proof it belongs to the right user.

## Blind extraction (regex oracle)

When the response differs only in content: `{"field":{"$regex":"^a"}}`
prefix-oracle per character, binary-search the charset. Sequential requests
if timing is the signal; establish jitter first.

## Aggregation pipelines — the bigger surface

An endpoint accepting an *array* body likely feeds `aggregate()`, not
`find()` — a much larger stage surface:

```json
[{"$limit":1},{"$unionWith":"users"},{"$match":{"username":{"$exists":true}}}]
```

`$unionWith` concatenates a *different collection* into pipeline output.
Siblings on the same input path: `$lookup` (cross-collection join), `$facet`,
`$function` (server-side JS). Write-shaped stages (`$merge`, `$out`) are
blast-radius territory — do not fire on a shared collection.

Falsifier: the array is rejected or validated element-by-element against an
allowed-stage list.

## Driver caveats

- ODM strict mode (Mongoose `strictQuery`, Rails `mongoid`) may strip
  operators before the query — falsified for that input path, note it.
- Some frameworks stringify nested values: `{"a":"{\"$ne\":1}"}` arrives as
  a string, not an object.
- `$where` support varies by version; confirm via error shape, not
  assumption.

## Blast radius

Never combine an unbounded operator filter with update fields on a shared
collection (`{"$gt":""}` + `$set` touches *every* document). Pin reads and
writes to objects created for the test; clean up disposable records where
deletion is supported.

## Severity guide

- Cross-collection read (`$unionWith`/`$lookup`) or auth bypass proven on a
  protected endpoint: high
- Operator injection confirmed, extraction path shown: medium-high
- Object reaches query but no oracle established: note, not a finding
