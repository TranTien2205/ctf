# SSRF — depth reference

Load once `probe_ssrf` confirmed the server fetches a controlled URL and you
need filter bypass, cloud-metadata targets, or internal pivoting. Every
fetched URL still goes through `http_request` — the scope guard applies to
the *first* request; what the server resolves after that is the bug.

## URL-parser bypass table (filters that check host)

| Technique | Payload |
|---|---|
| octal IP | `http://0177.0.0.1`, `http://0177.0.1` |
| hex IP | `http://0x7f.0.0.1`, `http://0x7f000001` |
| decimal IP | `http://2130706433` (127.0.0.1) |
| shortened | `http://127.1`, `http://0` |
| IPv6 | `http://[::1]`, `http://[::ffff:127.0.0.1]` |
| userinfo confusion | `http://allowed.com@127.0.0.1`, `http://127.0.0.1#allowed.com` |
| suffix confusion | `http://allowed.com.evil.com` vs checks that only `endswith`/`contains` |
| redirect | valid URL that 302s to `http://127.0.0.1` — validation runs pre-redirect |
| DNS rebinding | hostname alternating attacker↔127.0.0.1 between validate and fetch |

The redirect and rebinding rows bypass *validate-then-fetch* designs — the
check and the fetch resolve different addresses. Our own client re-checks the
peer IP at connect time precisely because this class exists.

## Cloud metadata (high-value first targets)

REACHING the metadata service is the whole finding. Stop there.

| Provider | Reachability probe | Notes |
|---|---|---|
| AWS IMDSv1 | `http://169.254.169.254/latest/meta-data/` | plain GET; a 200 listing instance keys is the proof |
| AWS IMDSv2 | same path, but needs `PUT /latest/api/token` with `X-aws-ec2-metadata-token-ttl-seconds` first — SSRF usually can't PUT; report IMDSv2-hardened honestly, which is a real and useful result |
| GCP | `http://metadata.google.internal/computeMetadata/v1/instance/` | needs header `Metadata-Flavor: Google` — only works if the SSRF lets you set headers |
| Azure | `http://169.254.169.254/metadata/instance?api-version=2021-02-01` | needs `Metadata: true` header |
| DigitalOcean | `http://169.254.169.254/metadata/v1/` | plain GET |

DO NOT follow the credential paths - `…/iam/security-credentials/<role>`,
`…/service-accounts/default/token`, or any sibling that returns a key, token
or password. That is credential dumping, which this package refuses, and it
adds NOTHING to the proof: a 200 from the metadata root already establishes
that the target fetched a URL it should not have and that the instance
metadata service is exposed through it. The severity of an exposed IMDS does
not depend on you holding the keys.

Record what proves reach - the status, the response's shape, the key NAMES a
metadata listing returns - and never a secret value. The same rule as
`id; echo <nonce>`: the proof is that the channel works, not what you could
take through it.

## Internal reach — how far, and then stop

Showing the SSRF reaches the target's own network is part of its impact.
ENUMERATING that network is lateral movement, which this package refuses, so
the two have to be kept apart deliberately.

What to establish: that an internal address answers DIFFERENTLY from one that
does not. Pick a port you expect closed and a port you expect open on
`127.0.0.1` or a private address, send the same request to both, and record
the difference - status, body length, or time to respond. A measured
difference between an open and a closed internal port is the finding: the
request left the target's own stack and the target's loopback is reachable
through it.

What NOT to do: list a service's contents (`/_cat/indices`, a Redis
`KEYS`-shaped URL, a database listing), authenticate to anything, or walk the
internal range for more hosts. That is the target's data and the target's
network, and none of it makes the SSRF more proven than the port difference
already did.
| 2375 | Docker API | `/containers/json` — unauthenticated RCE if open |
| 11211 | memcached | `stats` via gopher |

Open vs closed ports read differently: connection-refused errors are fast
and uniform; open services time out, banner, or return content. Sweep a
small known-port set before claiming "internal network reachable".

## Protocol smuggling (when scheme isn't restricted to http)

- `file:///etc/passwd`, `file:///c:/windows/win.ini` — local file read
- `gopher://127.0.0.1:6379/_INFO` — raw TCP into Redis/memcached/MySQL
- `dict://127.0.0.1:6379/info` — line-based services
- `ftp://`, `ldap://` — parser-confusion edge cases

## Blind SSRF (no response body returned)

Confirmation shifts to: timing differences (open vs filtered port),
error-message differences, or an OOB callback — point the URL at a listener
you control and cite the inbound hit via `note`. A logged DNS hit proves the
fetch happened even when the app shows nothing.

## Severity guide

- Cloud credentials or internal admin plane reached: critical
- Confirmed fetch of loopback/metadata URL, content returned: high
- Blind fetch confirmed only via OOB/timing: medium-high
- Filter exists but bypassed: report the bypass as the finding, not the filter
