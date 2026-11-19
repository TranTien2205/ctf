# Multi-step chains — the map as the first link

## The canonical chain

```
map the front-end -> name the hidden endpoint -> verify it live ->
route to its class -> exploit it -> the flag
```

The map is rarely the whole chain — it is the *discovery* link. The
rest of the chain is the routed class's own work.

## Chain: map → IDOR

`main.js` names `/api/user/{id}` → the endpoint responds → the `:id`
is enumerable → `web-idor` reads another user's object → the flag is
in their data. The map found the endpoint; IDOR exploited it.

## Chain: map → secret → authenticated reach

`config.js` carries `apiKey` → it authenticates → the key unlocks
`/api/admin` → `web-auth-session` uses the authenticated reach → the
flag is behind the gate. The map found the key; auth exploited it.

## Chain: map → flag gate → logic

`feature.admin` gates `/api/feature` → setting the flag reaches the
gated code → `web-logic-flaw`/`web-mass-assignment` works the gate →
the flag is in the gated response. The map found the gate.

## Chain: map → internal URL → SSRF

the bundle fetches `http://internal.svc/secret` → a server-side fetch
surface (`/proxy?url=`) reaches it → `web-ssrf` pulls the internal
data → the flag is internal. The map found the internal host.

## Chain: map → source → sink → exploit

`sourcesContent` shows a template render / a deserialize / an eval —
the real sink → route to its class → exploit the sink the source
revealed → the flag. The map recovered the spec; the source showed
the vuln.

## The map's place in every chain

The map is always link one — it replaces brute force with the client's
own route table. The chains differ only in which lead the map produced
and which class closes it.
