# IDOR / broken object-level authorization (BOLA)

**When:** an object identifier appears in a request and the server does not
check that the caller owns it. Params: `/users/123`, `?doc_id=`, `account`,
`order`, `invoice`, `file`, numeric ids, uuids, hashes of ids.

## The only honest test

You need TWO identities (or one identity plus an unauthenticated request):

1. As identity A, fetch your own object; note the response.
2. As identity B (or logged out), request A's object id.
   - Same data returned = IDOR confirmed. Quote the foreign object's fields.
   - 401/403/empty = the check exists at this endpoint; move to the next.
3. Matched pair matters: also fetch B's OWN id as B to prove the endpoint
   works at all - otherwise a hardcoded 404 looks like security.

## Where it hides

- Predictable ids: sequential integers - do NOT enumerate real users beyond
  one adjacent id needed for the pair.
- Indirect references: `?export=me` vs `?export=<other-username>`
- Object ids inside JWT claims the server trusts
- Batch endpoints: `{"ids": [<mine>, <theirs>]}`
- Write-side BOLA: PUT/PATCH on someone else's object - more severe than read
- GraphQL node ids: base64 `Type:123`

## Encoded/guid ids

UUIDs are not a defense when they leak elsewhere: check list endpoints,
search results, error messages, referers, and shared links for other users'
ids. One foreign uuid is all you need - never dump lists.

## Falsifier

Every cross-identity request to the endpoint class returns 401/403 or the
caller's own data, across at least read + write variants.

## Severity guide

Read PII/financial objects of others: high. Write/modify others' objects:
high-critical. Non-sensitive objects (public product data) via id: low-info.
Missing auth entirely on a sensitive endpoint is `auth-session`/logic, not IDOR.
