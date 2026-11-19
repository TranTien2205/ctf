# Delivery mechanics — how the second request lands inside the window

A race is won or lost at the network layer, not in the payload. Three delivery
mechanics, in order of reliability: last-byte interleave, single-packet burst,
and connection-spread burst.

---

## 1. Last-byte interleave — hold A open, drop B inside the window

The reliable form: send request A with its final byte withheld, so the server
has already begun processing — but block the commit — then send B complete,
then release A's last byte. A's processing is in-flight while B lands.

With raw sockets:

```python
import socket, ssl

def stalled(host, port, req_head, last_byte):
    s = ssl.create_default_context().wrap_socket(
        socket.create_connection((host, port)), server_hostname=host)
    s.sendall(req_head)                 # everything except the last body byte
    return s

# A: POST /profile {"email":"a@x"}   -- withheld last byte keeps A in-flight
# B: POST /profile {"email":"b@y"}   -- complete, lands inside A's window
sa = stalled(HOST, 443, A_head, b'')
sb = socket.create_connection((HOST, 443))
sb = ssl.create_default_context().wrap_socket(sb, server_hostname=HOST)
sb.sendall(B_full)                      # B commits first
sa.sendall(A_tail)                      # now release A
```

The stall point is the last body byte — everything before it is parsed and the
handler has started. This is the mechanics that produced the ApexSurvive
crossed-token outcome; a blind parallel burst on that target serialized instead.

## 2. Single-packet burst — the HTTP/2 and HTTP/1.1 forms

When the server accepts multiple requests in one TCP write, all of them enter
the accept queue in the same instant — the tightest possible start barrier.

HTTP/2: send all the HEADERS frames plus every DATA frame except each stream's
last, then flush all final DATA frames in one write. Burp's "single packet
attack" and `race_probe.py`'s barrier do this.

HTTP/1.1: N connections, each primed with its request minus the last byte; a
single barrier releases all last bytes at once:

```bash
python3 tools/web/race_probe.py --url "$BASE/api/vote" \
  --method POST --body '{"choice":1}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 5 \
  --barrier-timeout 5 --challenge <name>
```

`--barrier-timeout` is the max seconds the tool waits for all connections to be
primed before releasing. If it times out, the run is `inconclusive`, not a
negative — some connections never got in flight.

## 3. Connection-spread burst — why one connection lies

Parallel requests over one keep-alive connection may serialize at the client or
the server: HTTP/1.1 pipelines are answered in order, and many frameworks hold a
per-connection lock. The burst looks concurrent on the wire and is serial in
the handler.

Rules:

- One request per connection. `race_probe.py --concurrency 20` opens 20
  connections; never assume a multiplexed client gave you 20 workers.
- Check `max_in_flight` in the report. If it is below the requested concurrency,
  the requests did not all overlap — the result is `inconclusive`.
- Server worker count is a ceiling: a gunicorn/uwsgi pool of 4 workers cannot
  run 20 handlers at once. Match `--concurrency` to what the target can
  actually execute in parallel, not to a big number.

## 4. Choosing the mechanic

| Situation | Mechanic |
|---|---|
| window is ms-scale, read+write in different functions | last-byte interleave |
| single-use code, vote, limit — wide-enough window | single-packet burst via race_probe |
| target behind HTTP/2 | single-packet burst (HEADERS+DATA split) |
| two *different* requests must cross (ApexSurvive A/B) | `--url-b` interleave, or manual stall |
| burst shows `max_in_flight` below requested | fewer connections, or interleave |
| first attempts don't land | re-roll the timing; do NOT escalate count into a flood |

## 5. Re-roll, don't flood

A flood hides attribution: if 500 requests produce two successes you cannot
say which pair crossed, and a result you cannot attribute is not evidence. The
loop is:

```text
baseline (serial, --baseline-count 5, --count 0)
  → overlapping run (--concurrency N --count N)
  → read max_in_flight + status/body split vs baseline
  → if inconclusive: adjust concurrency or switch to interleave, re-roll
  → if serial-impossible outcome: attribute the pair, then confirm by repeating
```

`--reset-url`/`--reset-method`/`--reset-body` restore the object between rolls —
redeem a fresh code, reset the balance — so each roll starts from the same S.

## 6. Write-ack gate and blast radius

`race_probe.py` refuses a write-shaped run without `--write-ack`. That is the
blast-radius control: a race on a shared object corrupts it for every player.
Race an object you own — your own redeem code, your own balance, an account you
registered. The SSOS card's note applies here too: some targets are consumed on
first use (the flag is submitted once at startup); a consumed instance is
permanent, so confirm the object is fresh and yours before firing.

## 7. The timing-oracle variant

When the write path itself is safe, a pathological input can still win by
*stalling the check*: on PhantomFeed, `email=a@` + 26 chars + `!` against a
catastrophic regex made the verification window measurably wider than a normal
email. Measure the response-time delta between a normal and a pathological
input — the delta is itself the signal that a widening primitive exists.
