# Onboarding — the first read, the first pass

## The 5-minute mental model

```text
a WebSocket = an HTTP-upgrade handshake + a bidirectional frame stream.
  - the UPGRADE is the one-shot auth/Origin checkpoint
  - the FRAMES are the app's API — the per-message authz is routinely
    missing
the gaps:  handshake (Origin/auth/token/subproto) + messages (IDOR/
           dispatch/spoof/inject)
```

## The read order — the corpus start

```text
1. SKILL.md              the contract — the first probe + the falsifier
2. mechanism.md          the two surfaces + the four gaps
3. detection.md          how to know a ws surface exists
4. handshake-side.md     the upgrade checks
5. cswsh.md              the four-leg CSWSH chain
6. message-side.md       the frame checks
7. framing-protocols.md  the envelopes
8. workflow.md           the timed pass
9. the -deep / per-* / map / catalogue variants -> the depth
```

## The first commands — the pass

```bash
# the tool works
python3 tools/web/ws_probe.py --selftest
# the schema — the bundle is the ground truth
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
grep -riE 'wss?://|socket\.io|"(action|id|room|channel|role|token)"' /tmp/bundle
# the handshake cells
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'
# the first message cell
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"victim"}'
```

## The habits — the muscle-memory

- a `101` is never the finding — the cross-boundary frame is
- one field per connection — the reply must be attributable
- the envelope before the payload — the framing is a precondition
- the bundle is the schema — grep it before guessing
- the HTTP `403` does not close the WS cell — measure the frame
- a `uniform` reply closes a cell — a `weak-neg`/`gap` does not
- CSWSH needs all four legs — the `101` is leg-1 only

## The vocabulary — the first words

```text
an oracle      -> a boundary-crossing reply — the proof
a uniform      -> a measured rejection — a closed cell
a weak-neg     -> a guessed-name rejection — a re-probe
a gap          -> an unresponsive cell — not a verdict
surface        -> a 101/pong/ok — not a finding
a message-IDOR -> a per-frame object gap
a dispatch gap -> a privileged action, no role check
a spoof        -> a from/user_id the server trusts
a self-grant   -> a role/perm the frame binds
CSWSH          -> the four-leg cross-site hijack
```

## The boundary — when this class hands off

- a frame-field injection → the PAYLOAD's class (`web-sqli`/`web-ssti`/etc.)
- an HTTP object-gap → `web-idor`
- a token's forge → `web-auth-session`
- a one-shot forged request → `web-csrf`
- a `graphql-ws` subscription → `web-graphql`

## The onboarding-record

`onboarding: <the first pass>: <the first oracle>: <the lesson>` — the
first pass is the learning; the lesson is the discipline.
