# Internal networks — writes the bot reaches that you can't

The bot's browser resolves hosts inside the challenge's network —
service names, loopback, RFC1918 — that your external position can't
reach. The write's host is the targeting question.

---

## 1. The internal-host surface

```text
- 127.0.0.1 / localhost / ::1 — the bot's own host
- a docker-compose service name — app:, web:, backend:, api:, db:,
  redis:, worker:, nginx:
- an internal DNS — service.internal, host.docker.internal,
  <name>.local
- an RFC1918 — 10.x.x.x, 172.16-31.x.x, 192.168.x.x
- the challenge's own public URL — same as yours
```

```bash
# the names from the deployment config
grep -rnoE 'http://[a-z_-]+(:[0-9]+)?|hostname:|container_name:|services:|networks:|links:|depends_on' \
  <src> --include='*.yml' --include='*.yaml' --include='Dockerfile*' | head -40
grep -rnoE '127\.0\.0\.1|localhost|internal|private|host\.docker|\.local|\.internal' <src> | head -20
```

## 2. The internal-write shape — the loopback adjacency

```html
<!-- the form targets an internal name the bot resolves -->
<form action="http://app:8080/internal-write" method=POST>
<input name=a value=1></form>
<script>document.forms[0].submit()</script>
<!-- the bot's browser resolves 'app' to the internal service —
     your external request to 'app' fails DNS, the bot's hits it -->
```

## 3. The "the internal service has weaker auth" pattern

```text
an internal service/route that assumes 'only localhost can reach
me' → weaker or NO auth:
- an /internal/ endpoint with no token
- a debug/admin route bound to 127.0.0.1
- a management API on a private port
the bot's browser IS the local client — the weak-auth surface opens.
```

## 4. The port-scanning adjacency — the bot's internal surface

```text
the bot can reach internal ports your external request can't —
a form POST to http://127.0.0.1:<port>/<path> hits whatever's on
that port on the bot's host. enumerate the internal ports:
- a status/health port
- an admin port
- a metrics port
- a second service on another port
```

```html
<!-- probe internal ports via the bot's form -->
<form action="http://127.0.0.1:9090/metrics" method=GET></form>
```

## 5. The "the write's host is what matters" — the targeting

```text
the CSRF's form action names a host the VIEWER resolves:
- 127.0.0.1 → the viewer's own host
- app:8080 → the docker service
- target.com → the public host
- attacker.com → your host (for a beacon back)
the host is chosen by which service the WRITE needs, not where
the page is served.
```

## 6. The PNA/loopback constraints on internal targets

```text
- a fetch to 127.0.0.1/RFC1918 → PNA preflight (Chrome) → use a form
  nav (not PNA-gated the same way)
- an https page → http internal → mixed content → use http/data: page
- a private-network request from a public page → PNA or mixed-content
```

## 7. The internal-write readback — the state on an internal service

```text
the write lands on an internal service — the readback is where the
state surfaces:
- the internal service's output reachable via a public route
- a list/stats endpoint that includes the internal write's record
- the flag moved to a public-readable place
```

## 8. The falsifier

```text
- the write's host isn't on the bot's network → unreachable
- the bot's DNS doesn't resolve the internal name → dead
- PNA/mixed-content blocks every delivery → a form nav from an http/
  data page is the remaining shape; if that fails, dead
```

## 9. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "internal-net: form -> http://app:8080/write, bot resolves internal name"
```
