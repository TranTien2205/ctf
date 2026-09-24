# NoSQL operator injection

Use after `../SKILL.md` confirms that the request value remains an
object and reaches a query. Keep the first probes read-only and scoped to an
object you created.

## Common operators

| Operator | Typical use | Safe first use |
|---|---|---|
| `$ne`, `$gt` | alter equality/comparison filters | query only your own record |
| `$regex` | prefix/boolean oracle | test against a known field on your record |
| `$where` | JavaScript predicate in drivers that permit it | confirm support without writes |
| `$rename` | move a field, sometimes across validated paths | use only in a disposable record |

## Authentication filters

For JSON login filters, compare a normal scalar value with an object-valued
operator on a disposable account. Record the exact query shape and response.
Do not infer authentication bypass from a successful form response; prove the
resulting identity on a protected read-only endpoint.

## Blind extraction

If the application exposes a stable true/false response, use a bounded prefix
oracle and binary search the character set. Keep requests sequential if the
signal is timing-based. Establish baseline jitter before setting a threshold.

## Driver caveats

- ODM strict mode may strip or reject operators before they reach the database.
- Some frameworks stringify nested values; if so, the object never reaches the
  query and this class is falsified for that input path.
- `$where` support and execution semantics vary by database and version; confirm
  from the observed error/result rather than assuming support.

## Blast radius

Never combine an unbounded filter with update fields on a shared collection.
Pin reads and writes to an object created for the test; use disposable records
and clean them up where deletion is supported.
