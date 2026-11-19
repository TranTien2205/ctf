# Preconditions — what must be true before each check fires

## For any WebSocket finding

- the target opens a `ws://`/`wss://` channel — an `Upgrade`/`101`
- the channel carries data or actions worth crossing (a flag/object/
  privileged action — else no impact)
- a session/credential exists to bind OR the channel is unauth

## For CSWSH specifically — all four

- [ ] the handshake accepts a foreign `Origin` — measured `101`, not assumed
- [ ] the socket binds to the session COOKIE (not a `?token=` the page
      cannot read)
- [ ] the victim's cookie is `SameSite=None`/`Lax` — it travels on the
      cross-site upgrade
- [ ] the channel reads victim data or accepts a privileged action

Miss any → the CSWSH fails; the surviving subset is a weaker finding.

## For a message-IDOR

- [ ] a frame field names an object (`id`/`room`/`user_id`/`channel`)
- [ ] the field's id-space covers other principals' objects
- [ ] no per-message ownership check — measured by a mutated-frame reply

## For an action-dispatch gap

- [ ] the schema has a `action`/`type`/`event`/`cmd` dispatch field
- [ ] a privileged action exists in the schema (the bundle names it)
- [ ] the dispatch does not re-check role/scope per message

## For an identity/role spoof

- [ ] the frame carries a `from`/`user_id`/`role`/`sender` field
- [ ] the server trusts the frame's identity, not the handshake's

## For an injection-in-frame

- [ ] a frame field reaches a sink (query/template/path/cmd/deser)
- [ ] the field is not escaped/validated at the frame layer
- [ ] the payload class is confirmed by its own oracle (arithmetic/
      error/timing/etc.)

## For a token-in-URL

- [ ] the ws URL carries `?token=`/`?jwt=`/`?key=`/`?auth=`/`?session=`
- [ ] the credential is sensitive (a session/JWT, not a public key)

## The tools-precondition

- `ws_probe.py` present — `python3 tools/web/ws_probe.py --selftest`
- `proto_decode.py` for binary frames
- `bundle_miner`/`web-source-map` for the endpoint+schema recovery

## The budget-precondition

5 probes or 15 active minutes per mechanism class; 25/45 per challenge.
The pass is ~15-30 probes — within budget; the coverage matrix decides
which cells to spend on.
