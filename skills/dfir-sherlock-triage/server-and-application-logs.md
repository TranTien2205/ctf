# Server and application logs

The family that needs no parser. An IIS, Apache, nginx, proxy or database log is
line-oriented text with a declared field order - ASCII unless UTF-8 logging was
turned on - so every question it answers is answered by field-order arithmetic:
pick the column, group, count, sort. Every command in this file uses only `awk`,
`sort`, `uniq`, `sed` and `python3`, all present. Nothing here waits on
`toolchain.md`.

The two things that lose the answer are both structural, not analytical: reading
a column by a hardcoded index when the file declared a different order, and
merging a local-offset web log against a UTC event log without normalising.
Both are handled below with measured commands.

What is measured here versus cited: every command in the fenced blocks was run on
this box against a fixture built for it, and the numbers quoted are what came
back. Every field name, status code, default path and format string is cited
inline to the vendor's own documentation. No Sherlock in this tree has been
solved with this file yet, so do not present any of it as local case experience.

## 1. IIS, W3C extended format

### Where it is and what it is called

- Per-site access logs: `C:\inetpub\logs\LogFiles\W3SVC<siteID>\`, where
  `<siteID>` is the site's numeric id and the Default Web Site is `W3SVC1`. The
  configurable default directory is `%SystemDrive%\inetpub\logs\LogFiles`
  (Microsoft Learn, "Configure Logging in IIS", Directory step). The `W3SVC<id>`
  level is not a convention, it is HTTP.sys: "For the W3C Extended, NCSA Common,
  and IIS log file formats, HTTP.sys generates the subdirectory
  C:\LogFiles\W3SVC#, where # is the site ID" (Microsoft Learn, "Log File
  Formats in IIS", Log File Locations and ACLs). Centralized binary logging
  drops one level, to `C:\LogFiles\W3SVC`, and is not text - it needs a parser.
- File name `u_ex<yymmdd>.log` for daily rollover, `u_ex<yymmddhh>.log` for
  hourly; `u_ex130319.log` is Microsoft's own example of the name. That the
  `u_` prefix specifically marks UTF-8 logging, with an ANSI-era file named
  `ex<yymmdd>.log`, is repeated everywhere but is UNVERIFIED against a Microsoft
  page here, so do not state it as the reason in an answer - the Microsoft page
  says only that UTF-8 logging can be enabled for the W3C, IIS and NCSA text
  formats and is unsupported for FTP logs. The date in the NAME follows the "Use
  local time for file naming and rollover" checkbox, and when that box is clear
  the name is UTC; "regardless of this setting, timestamps in the actual log
  file will use the time format for the log format that you select" (Microsoft
  Learn, "Configure Logging in IIS", rollover step). So the file name and the
  rows inside it can be on two different clocks.
- HTTP.sys kernel-mode error log: `%SystemRoot%\System32\LogFiles\HTTPErr\`,
  file `httperr<n>.log`. The directory is documented - "For HTTP.sys error
  logging, HTTP.sys generates the subdirectory C:\WINDOWS\System32\LogFiles\
  HTTPErr" (Microsoft Learn, "Log File Formats in IIS") - but the case varies on
  disk and some collections rename it, so match the `httperr` file name rather
  than the directory when you search the bundle.

A directory of `.log` files under a `W3SVC*` parent is the recognition signal.
`tools/forensics/artifact_inventory.py --path <dir> --challenge <c>` records the
inventory; the file names alone tell you the date range before anything is read.

### The three headers, and the rule that follows from the fourth

```
#Software: Microsoft Internet Information Services 10.0
#Version: 1.0
#Date: 2024-03-06 06:30:00
#Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) cs(Referer) sc-status sc-substatus sc-win32-status sc-bytes cs-bytes time-taken
```

`#Date` is when the FIRST entry was written, which is when the file was created -
not midnight, and not the first event of interest (Microsoft Learn, "W3C
Logging"). A file whose `#Date` is 06:30 has nothing before 06:30 in it, so a
"first request" answer read from the top of one file is only the first request of
that file.

**`#Fields` declares the field order per file, and it can change inside one
directory.** An administrator who adds `cs(Referer)` mid-incident shifts every
later column by one. A `sc-status` read as `$12` because that is where it was in
yesterday's file is then a wrong answer with no error message. Read `#Fields` in
every file and build the index map from it. Also: a re-emitted `#Fields` line can
appear part-way down a single file after an IIS configuration change, so parse it
wherever it occurs, not only at the top.

Measured on this box - the awk that builds the map and then names columns by name:

```bash
awk '
/^#Fields:/ { for (i = 2; i <= NF; i++) { idx[$i] = i - 1 }; nf = NF - 1; next }
/^#/        { next }
{ print $(idx["date"]), $(idx["time"]), $(idx["c-ip"]), $(idx["cs-method"]),
        $(idx["cs-uri-stem"]), $(idx["sc-status"]) "." $(idx["sc-substatus"]),
        $(idx["time-taken"]) }' u_ex240306.log
```

On the fixture that produced this file that printed:

```
2024-03-06 06:31:02 10.1.1.7 GET /admin/ 401.2 15
2024-03-06 06:31:44 10.1.1.7 POST /uploads/logo.aspx 200.0 2109
```

`idx[]` is rebuilt every time a `#Fields` line is seen, which is exactly the
behaviour that survives a mid-directory change. Note `nf` is captured too: a
truncated final line with fewer fields than `nf` is a torn write, and it is worth
counting those rather than letting awk print empty strings.

The python equivalent, when the next step is a merge or a dataframe - `rows` goes
straight into `pandas.DataFrame(rows)`, and every column is then named:

```python
def read_w3c(path):
    fields, rows = None, []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#Fields:"):
                fields = line.split(":", 1)[1].split()
                continue
            if line.startswith("#") or not line.strip():
                continue
            if fields is None:
                raise ValueError("%s: data before any #Fields line" % path)
            parts = line.split(" ")
            if len(parts) != len(fields):
                rows.append({"_torn": line, "_expected": len(fields),
                             "_got": len(parts)})
                continue
            rows.append(dict(zip(fields, parts)))
    return fields, rows
```

Split on a single space, not on whitespace: IIS separates fields with one space
character and replaces any nonprintable character INSIDE a field with a plus sign
`+` (0x002B) to preserve the format (Microsoft Learn, "W3C Logging"). That is why
an IIS user agent reads `Mozilla/5.0+(Windows+NT+10.0)` and why a request smuggled
with a carriage return still leaves one parseable line. It also means a `+` in a
value is ambiguous: it may be a real plus or a substituted control character, and
that ambiguity is itself the finding when the question asks what was injected.

An empty field is a single hyphen `-`, and a field enabled but not selected for
that request is also `-` (Microsoft Learn, "W3C Logging"). Treat `-` as null, not
as a value; a `cs-username` of `-` is anonymous, not a user called "-".

### The fields that answer questions

Field meanings below are quoted from Microsoft Learn ("W3C Logging", HTTP Server
API field table) and the IIS logging page's W3C Logging Fields list.

| Field | What it is | The question it answers |
|---|---|---|
| `date` | date the activity occurred | day of the intrusion |
| `time` | time in **UTC** | ordering, and the join key to EVTX |
| `s-ip` | server address the entry was generated on | which host, in a multi-homed set |
| `cs-method` | the requested verb | `POST` to a static-looking path |
| `cs-uri-stem` | target of the verb | the webshell path, the uploaded file |
| `cs-uri-query` | the query string, dynamic pages only | the injected value, url-encoded |
| `s-port` | configured server port | which binding, 80 vs 443 vs 8172 |
| `cs-username` | the AUTHENTICATED user; anonymous is `-` | which account was used |
| `c-ip` | the client address | the attacker address |
| `cs(User-Agent)` | client browser type, spaces as `+` | tool fingerprint |
| `cs(Referer)` | the site the user last visited | absence of one on a deep path |
| `sc-status` | HTTP status code | success after a scan |
| `sc-substatus` | the substatus error code | WHY a 401 or 404 happened |
| `sc-win32-status` | the Windows status code | the OS-level reason |
| `sc-bytes` | bytes sent by the server | size of the exfiltrated response |
| `cs-bytes` | bytes received and processed | size of the uploaded body |
| `time-taken` | length of the action, in **milliseconds** | command execution, not file serving |
| `cs-version` | HTTP protocol version the client used | a raw-socket client on HTTP/1.0 |
| `cs-host` | the Host header, if any | virtual host, or an IP-literal Host |
| `s-sitename` | service name and instance number | which site in a centralised log |
| `s-computername` | the server that generated the entry | which node behind a balancer |
| `cs(Cookie)` | the content of the cookie sent or received, if any | off by default; when a bundle HAS it, a webshell's auth cookie or a stolen session id is in this column verbatim |
| `streamid` | the Stream Id | HTTP/2 only: several requests share one connection, so `c-ip` plus `streamid` separates them |

Two field names are spelled differently by Microsoft and by the log file, and a
hardcoded key misses one of them:

- **Referer.** BOTH Microsoft pages spell it `cs(Referrer)`, with two r's - the
  HTTP Server API field table and the IIS "W3C Logging Fields" selector list.
  Real IIS `#Fields` lines commonly emit `cs(Referer)` with one r, matching the
  HTTP header, but that one-r spelling is UNVERIFIED against a Microsoft page
  here. Read the file's own `#Fields` line; never assume either.
- **User agent.** The HTTP Server API table spells it `cs(User-Agent)`; the IIS
  selector list spells it `cs(UserAgent)` with no hyphen. Same rule.

This is exactly why the awk above builds `idx[]` from the header rather than
naming a column by a remembered string.

Two fields IIS does NOT have, and the absence changes what you can answer: there
is no request body, and there is no response header. A webshell's command lives
in `cs-uri-query` only if it was sent in the query string. A `POST` body is not
in this log at all, so the answer to "what command was run" comes from the
correlated Sysmon 1 record, not from here. Say that explicitly rather than
guessing at the body.

### sc-status with sc-substatus, the pairs worth knowing

The log carries status and substatus as two separate columns - `sc-status` and
`sc-substatus` - and the familiar `401.2` notation is the detailed-error form
shown to the browser, not a string in the file. For the 401 block Microsoft is
blunter than that: "The following specific HTTP status codes are displayed in
the client browser but aren't displayed in the IIS log." Read that as a warning
about the dotted string, not about the number: a real row still carries
`sc-status 401` and `sc-substatus 2` in two columns. Meanings from Microsoft
Learn, "HTTP Status Code Overview" (IIS):

| Pair | Documented meaning | Reading it in an intrusion |
|---|---|---|
| `401.1` | Logon failed - probably an invalid user name or password | credential guessing against an authenticated path |
| `401.2` | Logon failed due to server configuration | the client offered an auth method the server does not allow |
| `401.3` | Unauthorized due to ACL on resource | NTFS permissions denied it; the login itself worked |
| `401.4` | Authorization failed by filter | an ISAPI filter refused it |
| `401.5` | Authorization failed by ISAPI/CGI application | the app refused it |
| `401.501` / `401.502` | Access denied: concurrent request rate limit reached / maximum request rate limit reached | **Dynamic IP Restriction** fired - a scan hit a rate limit, so the scan was faster than the site's own traffic |
| `401.503` / `401.504` | Access denied: IP address denied / host name denied | **IP Restriction**, not the dynamic one: the address or name was already on a static deny list before this request |
| `403.3` | Write access forbidden | a `PUT` or WebDAV write was refused - an upload attempt that did NOT land |
| `403.14` | Directory listing denied, no default document | someone asked for a directory, not a page |
| `403.21` | Forbidden: source access denied | a WebDAV request for a resource's SOURCE |
| `404.0` | Not found - the file is moved or does not exist | ordinary content scanning |
| `404.2` | ISAPI or CGI restriction | a handler exists but is not allowed |
| `404.6` | Verb denied | an unconfigured or invalid verb - `PUT`, `MOVE`, `PROPFIND`, or a nonsense verb from a raw-socket client |
| `404.3` | MIME type restriction | the extension has no MIME mapping - a dropped file the server will not serve |
| `404.4` | No handler configured | the extension has no handler - an uploaded `.aspx` in a folder without one |
| `404.5` | Denied by request filtering configuration | the URL contains a blocked character sequence |
| `404.7` | File extension denied | request filtering blocked the extension |
| `404.11` | Request contains double escape sequence | a `%252e` style traversal attempt - a near-certain finding |
| `404.12` | Request contains high-bit characters | non-ASCII in the URL, filtered |
| `404.13` | Content length too large | an upload over the configured limit |
| `404.15` | Query string too long | an oversized payload in the query |
| `404.18` | Query string sequence denied | a blocked query sequence |
| `404.19` | Denied by filtering rule | a Request Filtering rule fired |
| `404.17` | Dynamic content mapped to the static file handler | the server handed a script to the static handler instead of executing it - an uploaded `.aspx`/`.asp` in a directory whose handler mapping does not cover it |
| `500.0` | Module or ISAPI error occurred | the request reached code and the code threw; pair it with the `time-taken` on the same row before calling it execution |
| `500.19` | Configuration data is invalid - a problem in `applicationHost.config` or `web.config` | a dropped or tampered `web.config`; correlate the timestamp to `$MFT` and Sysmon 11 |
| `500.100` | Internal ASP error | an ASP payload that threw |
| `503.0` | Application pool unavailable - the pool is stopped or disabled | the pool crashed, or was stopped as part of the intrusion. Microsoft's own next step: "The event log may give information about why the application pool is stopped or disabled" - that is the System log, WAS and IIS-W3SVC-WP sources, via `windows-event-logs.md` |

`sc-win32-status` is the Windows error behind the HTTP answer, so a `401.1` with
a Win32 code distinguishes a wrong password from a disabled account. Resolve one
with `net helpmsg <n>` on Windows; there is no offline resolver on this box, so
record the raw number in the ledger rather than a guessed name.

`time-taken` is milliseconds, and its definition is precise: the timer starts
when HTTP.sys receives the FIRST BYTE, before the request is parsed, and stops at
the last send completion. It does not include network time, and the very first
request to a site reads slightly high because HTTP.sys opens the log file on it
(Microsoft Learn, "W3C Logging", closing paragraph). Two consequences:

- A large `time-taken` on a static file with a small `sc-bytes` is a slow CLIENT,
  not a slow server - that is a trickle upload or a slow-read client, not
  execution.
- A large `time-taken` on a script extension with a normal `sc-bytes` is work
  happening server-side: a command running, a database query, an outbound fetch.
  That is the webshell signal in section 4.

### The format trap before any of this

IIS can log in four formats and only one of them is what section 1 describes
(Microsoft Learn, "Configure Logging in IIS", Format list):

| Format | Separator | Timestamp timezone |
|---|---|---|
| W3C | spaces, customizable fields | **UTC** |
| IIS | **commas**, fixed fields | **local time** |
| NCSA | spaces, fixed fields | **local time with a UTC offset** |
| Custom | a custom module | unknown, read the module |

A comma-separated IIS-format log timestamped in local time, merged against a UTC
Security.evtx timeline as if it were W3C, puts every web request an offset away
from the event that caused it. Look at the first data line before writing any
filter: a `#Fields` header means W3C, commas with no header mean IIS format.

HTTPERR is a fifth shape. It has the same W3C field discipline but **no column
headings at all**, and the order is fixed (Microsoft Learn, "Format of the HTTP
Server API Error Logs"): Date, Time, Client IP, Client Port, Server IP, Server
Port, Protocol Version, Verb, CookedURL+Query, Protocol Status, SiteId,
Reason Phrase. Date and Time are UTC; spaces, tabs and unprintable control
characters inside a field become `+`; SiteId is always `-` in this version.
`Reason Phrase` is never empty, and the documented examples are `ConnLimit`,
`Hostname`, `Version_N/S` and `Timer_MinBytesPerSecond`. That last one is HTTP.sys
dropping a client for sending below the minimum throughput, which is what a
slow-drip connection looks like from the kernel's side - it is not an application
error, so do not report it as one.

## 2. Apache httpd and nginx

### The format strings, exactly

```
LogFormat "%h %l %u %t \"%r\" %>s %b" common
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"" combined
```

Both quoted verbatim from the Apache httpd 2.4 "Log Files" documentation. Token
meanings from the same page: `%h` remote host, `%l` the identd logical username
(almost always `-`, and the doc calls the value highly unreliable), `%u` the
HTTP-authenticated userid, `%t` the receive time, `%r` the request line in double
quotes, `%>s` the final status, `%b` the response size excluding headers or `-`
for none. `%B` logs `0` instead of `-`. A site running `combined` appends the
`Referer` and `User-Agent` request headers, each in double quotes.

nginx, from the nginx `ngx_http_log_module` reference. The default directive is
`access_log logs/access.log combined;` and the predefined `combined` format is,
from `src/http/modules/ngx_http_log_module.c` line 230 in the upstream source:

```
$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
```

So nginx `combined` and Apache `combined` produce the same column positions -
one regex reads both - with one difference that matters for byte-count questions:
nginx `$body_bytes_sent` excludes headers, while `$bytes_sent` (used in the docs'
own `compression` example) includes them. If the bundle's `nginx.conf` is present,
read the `log_format` line rather than assuming `combined`.

### The timestamp carries a local offset

Apache `%t` is documented as `[day/month/year:hour:minute:second zone]` with
`zone = ('+' | '-') 4*digit` - so `[06/Mar/2024:06:31:02 +0200]` is 04:31:02 UTC.
nginx is worse for being silent: `$time_local` is "local time in the Common Log
Format" and `$time_iso8601` is "local time in the ISO 8601 standard format"
(nginx log module reference). Both are LOCAL. Normalise before merging, always.

Measured, on a fixture whose Apache line and IIS line describe the same request:
`tools/forensics/timeline_merge.py` read the Apache `06/Mar/2024:06:31:02 +0200`
stamp through its `"%d/%b/%Y:%H:%M:%S %z"` format (the entry is in
`STRPTIME_FORMATS`, `tools/forensics/timeline_merge.py` line 77) and placed it at
`"first":"2024-03-06T04:31:02+00:00"`, while the IIS row for the same event sat
at `"first":"2024-03-06T06:31:02+00:00"`. Two hours apart on one axis, stated in
the output rather than hidden.

Where that statement appears matters, because it is printed in two shapes and
only one of them contains the key you would grep for. Per source, inside
`sources[]`, it is `"assumptions":{"offset_to_utc":2}`. At the top level it is a
LIST that spells the key out in prose and drops it:
`"assumptions":[{"assumption":"a timestamp carrying an explicit offset was
converted to UTC","rows":4,"sources":["httpd","iis"]}]`. Grep the per-source
object for `offset_to_utc`; grep the top level for `"rows"`.

### The split that survives a user agent with spaces

Splitting a combined line on whitespace breaks on the first space inside the
quoted request line or user agent. This regex was run on the fixture and matched:

```python
import re

CLF = re.compile(
    r'^(?P<c_ip>\S+) (?P<ident>\S+) (?P<user>\S+) \[(?P<t>[^\]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>\d{3}|-) (?P<bytes>\S+)'
    r'(?: "(?P<referer>(?:[^"\\]|\\.)*)" "(?P<agent>(?:[^"\\]|\\.)*)")?\s*$')
```

Four deliberate choices, each from a way the naive version fails:

- `\[(?P<t>[^\]]+)\]` for the time, because the value contains a space before the
  offset and colons inside it.
- `"[^"]*"` for the request line, so `GET /a b HTTP/1.1` stays one field.
- `(?:[^"\\]|\\.)*` for referer and agent, because nginx escapes an embedded
  double quote as `\"` under `escape=default`, and a plain `[^"]*` would stop
  there and desynchronise the rest of the line.
- The whole referer/agent group optional, so the same regex reads a `common` log
  and a `combined` log without a second pattern. A line that does not match is
  counted and printed, never dropped - an unparsed line in a web log is usually
  either a different `LogFormat` in the same file or an injected newline.

nginx's `escape=default` escapes `"`, `\`, and every character below 32 or above
126 as `\xXX` (nginx log module reference). So a control character in an injected
URL appears as a literal `\x0a` in the file, and searching for the raw byte finds
nothing. Search for the escape sequence. `escape=json` instead escapes to
`\n`, `\r`, `\t`, `\b`, `\f` or `\u00XX`, and `escape=none` disables escaping
entirely - which is the case where a newline in a request really does split one
request across two log lines.

### The error logs

Apache, quoted from the httpd 2.4 documentation's own example:

```
[Fri Sep 09 10:42:29.902022 2011] [core:error] [pid 35708:tid 4328636416] [client 72.15.99.187] AH00124: Request exceeded the limit of 10 internal redirects due to probable configuration error
```

Order: bracketed timestamp, `module:severity`, `pid:tid`, `client <address>`,
then an `AHnnnnn` message id and the text. The timestamp has no offset at all -
it is server local time in a different format from the access log's `%t`, so the
two files in one bundle need two parsers.

One trap worth the line: in httpd 2.4, "File does not exist" messages for 404
responses were downgraded from `error` to `info`, and with the default
`LogLevel warn` they do NOT appear in the error log (httpd 2.4 "Log Files"). An
error log with no 404 noise is therefore not evidence that no scanning happened.
The access log is the only place to count it.

nginx error log lines carry the client, the request and the upstream as named
key-value tails - `client: <ip>, server: <name>, request: "<line>", host:
"<header>"` - which makes them greppable by key. The exact set of trailing keys
is version- and module-dependent and is UNVERIFIED here; read one line from the
bundle in full before writing a pattern across the file.

## 3. The pivot, from one suspicious request to the answer

A numbered procedure. Each step is a command, and each command's output is the
input to the next. `WEB=u_ex240306.log` for an IIS file; the Apache equivalent
uses the TSV produced by the regex above.

**1. Build the index map once and emit a TSV.** Everything downstream then reads
by column name, and the file becomes mergeable. Measured on this box:

```bash
awk '
/^#Fields:/ { for (i = 2; i <= NF; i++) { n[i-1] = $i }; nf = NF - 1
              printf "ts"; for (k = 1; k <= nf; k++) printf "\t%s", n[k]
              printf "\n"; next }
/^#/ { next }
{ printf "%sT%sZ", $1, $2
  for (k = 1; k <= nf; k++) printf "\t%s", $k
  printf "\n" }' "$WEB" > web.tsv
```

The synthesized first column matters: IIS puts `date` and `time` in two separate
fields, and `tools/forensics/timeline_merge.py` wants ONE time column, so the
`ts` column is built as `<date>T<time>Z`. The `Z` is legitimate - W3C `time` in
IIS is UTC by definition - and the merge reports the row under
`offset_to_utc`, which is the auditable statement that the assumption was made.

**2. Group by client address and count.** The attacker is rarely the busiest
client, so read the tail of the distribution as well as the head.

```bash
awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}{print $h["c-ip"]}' web.tsv \
  | sort | uniq -c | sort -rn | head -30
```

**3. Bracket that client's activity.** First and last request from one address
gives the session window that every later question is scoped to.

```bash
IP=10.1.1.7
awk -F'\t' -v ip="$IP" 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}
  $h["c-ip"]==ip {print $1, $h["cs-method"], $h["cs-uri-stem"],
                        $h["sc-status"] "." $h["sc-substatus"]}' web.tsv \
  | sort | sed -n '1p;$p'
```

**4. Find the first success after a run of failures.** This is the single highest
value query in the whole family: a scan is a run of 404 or 401, and the request
that ends the run is the one that worked. Track the failure streak explicitly
rather than eyeballing it.

```bash
awk -F'\t' -v ip="$IP" '
NR==1 { for (i=1;i<=NF;i++) h[$i]=i; next }
$h["c-ip"] != ip { next }
{ s = $h["sc-status"] }
s == 404 || s == 401 || s == 403 { fails++; next }
s >= 200 && s < 300 {
    if (fails >= 3)
        printf "first 2xx after %d failures: %s %s %s\n",
               fails, $1, $h["cs-method"], $h["cs-uri-stem"]
    fails = 0 }' web.tsv
```

Raise the `fails >= 3` threshold on a noisy public site; a busy site produces
404 runs from broken links. The signal is the CONJUNCTION - a failure run, then
a 2xx, from one address, on a path that appears nowhere else in the file.

**5. Pull the query string and decode it.** `cs-uri-query` is url-encoded on the
wire and the answer is almost always the decoded form.

```bash
awk -F'\t' -v ip="$IP" 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}
  $h["c-ip"]==ip && $h["cs-uri-query"]!="-" {print $1 "\t" $h["cs-uri-stem"] "\t" $h["cs-uri-query"]}' \
  web.tsv | python3 -c '
import sys, urllib.parse
for line in sys.stdin:
    ts, stem, q = line.rstrip("\n").split("\t")
    print(ts, stem, urllib.parse.unquote_plus(q))'
```

`unquote_plus`, not `unquote`: a query string encodes a space as `+`, and IIS
independently substitutes `+` for control characters, so a decoded value
containing an unexpected space is worth a second look at the raw field. Decode
twice and compare when `sc-substatus` was `11` - `404.11` means the server itself
saw a double escape sequence.

**6. Merge the web log against the EVTX timeline on one UTC axis.** This is the
step that converts a request into an executed command. The exact invocation, run
here:

```bash
python3 tools/forensics/timeline_merge.py \
  --source web.tsv:ts:iis \
  --source events.tsv:TimeCreated:evtx \
  --contains 'logo.aspx' \
  --challenge <sherlock>-qN --compact
```

`--source PATH:TIMECOL[:LABEL]`; the format is taken from the extension, and
`FORMAT_BY_EXTENSION` knows only `.csv`, `.tsv`, `.tab`, `.jsonl`, `.ndjson` and
`.jsonlines`. A file still called `u_ex240306.log` therefore does not merge at
all - the tool exits with "cannot tell the format of ... from its extension;
pass --format csv|tsv|jsonl after that --source". Either write `web.tsv` as in
step 1, or add `--format tsv` after that one `--source`.

On the two-source fixture, the run reported `rows_read 2, parsed 2, unparsed 0`
per source and `"rows_total":4` over one window. Three verdict facts, each
measured here rather than assumed:

- With NO `--contains`, `verdict_downgrades` holds two strings, the first being
  `"no --contains was given, so this run is a view only and cannot propose a
  confirmation at all"`. A view is all you get.
- With `--contains 'logo.aspx'` and nothing else, `verdict_downgrades` is EMPTY
  and the verdict is still `inconclusive` - because `--on-match` defaults to
  `inconclusive`. An empty downgrade list is not a confirmation.
- To propose one: `--on-match confirms --evidence-kind class --class <bug class>
  --hypothesis-id <id>`. The excerpt it then quotes is the merged record
  verbatim, never anything retyped, and `tools/hooks.py post-probe` remains the
  only write path for the verdict.

**7. Name what ran, from the event side of the merge.** With the merged window in
hand, query the process-creation channel inside it. `evtx_query.py` takes the
JSONL a dumper produced (see `windows-event-logs.md` for the dump, and
`toolchain.md` if no dumper is installed yet):

```bash
python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 1 \
  --field-contains ParentImage=w3wp.exe \
  --since '2024-03-06T06:31:00Z' --until '2024-03-06T06:35:00Z' \
  --order asc --answer CommandLine --challenge <sherlock>-qN
```

`ParentImage` containing `w3wp.exe` is the join that closes the loop: the IIS
worker process spawning a shell is the execution the web log could only imply.
For a classic ASP or an `.asp` handler the parent may be `inetinfo.exe`; for
PHP-FPM behind nginx it is `php-fpm`; for Tomcat it is `java.exe`. Read the
actual `ParentImage` in one record before filtering on a guessed one. `--answer
FIELD` prints the `hooks.py pre-flag` argv so the answer is never hand-copied.

**8. Identify the uploaded file.** The upload is the `cs-uri-stem` of a request
whose `cs-bytes` is large and whose `sc-status` is 2xx, or the `cs-uri-stem` of
the first request that ever hit a path the rest of the file has never seen:

```bash
awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}
  {c[$h["cs-uri-stem"]]++; if(!(($h["cs-uri-stem"]) in first)) first[$h["cs-uri-stem"]]=$1}
  END{for (u in c) if (c[u] <= 5) print c[u], first[u], u}' web.tsv | sort -k2
```

Then confirm it on disk, not in the log: `$MFT` or `$J` carries the creation of
that path (`filesystem-timeline.md`), and Sysmon 11 carries the file-create event
with the creating process. A path that exists only in the web log and nowhere on
the filesystem was requested, not created.

## 4. What a webshell looks like in these logs, specifically

No single row proves one. Each line below is a column-level anomaly; a webshell
is the intersection of three or more of them on one `cs-uri-stem`.

- **`cs-method` is `POST` on an extension that should be static.** A `POST` to
  `.jpg`, `.txt`, `.gif`, `.css` or `.log` is not a normal browser action. On
  IIS these often also carry `sc-substatus` 3 or 4 (`404.3` MIME restriction,
  `404.4` no handler) when the dropped extension has no handler configured - a
  404 that proves the file IS there and could not be executed.
- **A long `cs-uri-query` on a path with `cs(Referer)` of `-`.** A browser that
  reaches a deep parameterised URL arrived from somewhere. A client that posts a
  200-character query to one path with no referer, repeatedly, did not.
- **One `c-ip` hitting one uncommon `cs-uri-stem` with 2xx, over and over.**
  Count `c-ip` and `cs-uri-stem` together: a legitimate page has many clients; a
  webshell has one client and one path. Two commands:

```bash
awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}
  {n[$h["cs-uri-stem"]]++}
  END{for (k in n) print n[k], k}' web.tsv | sort -rn | head -40

awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}
  {print $h["cs-uri-stem"] "\t" $h["c-ip"]}' web.tsv \
  | sort -u | cut -f1 | uniq -c | sort -n | head -20
```

  The second prints each path with its DISTINCT client count, ascending. A path
  with many requests and exactly one distinct client is the shape.
- **A `time-taken` distribution unlike the rest of the site.** Static content
  reads in single or low double digit milliseconds. A path whose requests are
  consistently in the hundreds or thousands of milliseconds, with modest
  `sc-bytes`, is spending that time doing work - which for a static-looking
  extension is the finding. Compute it per path rather than eyeballing:

```bash
awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;next}
  {k=$h["cs-uri-stem"]; t=$h["time-taken"]+0; n[k]++; s[k]+=t; if(t>m[k])m[k]=t}
  END{for (k in n) printf "%8.1f %8d %6d  %s\n", s[k]/n[k], m[k], n[k], k}' \
  web.tsv | sort -rn | head -25
```

  Read mean, max and count together: one slow request out of ten thousand is a
  timeout, while a mean of 2000 ms over forty requests is execution.
- **`cs-username` populated on a path that should be anonymous**, or the same
  `c-ip` appearing first with 401s and then with a populated `cs-username` -
  credentials were obtained between the two.
- **`cs(User-Agent)` that is a library, not a browser.** `python-requests/x.y.z`,
  `curl/x.y.z`, `Go-http-client/1.1`, an empty `-`, or a browser string with the
  wrong token order. Quote the exact string as the answer; do not paraphrase it.
- **A `500.19` before the shell works.** Configuration data invalid means a
  `web.config` was written or broken, which is a dropped file with a timestamp -
  correlate it to `$MFT` and to Sysmon 11.

Every one of these is a hypothesis for `tools/hooks.py post-probe`, not a finding.
The finding is the merged record from step 6 or the Sysmon 1 `CommandLine` from
step 7, quoted verbatim.

## 5. Other application logs a bundle ships

One row each: where it is, and the one field that answers.

| Log | Path | The field that answers, and the citation |
|---|---|---|
| MSSQL error log | Windows: `<drive>:\Program Files\Microsoft SQL Server\MSSQL.<n>\MSSQL\LOG\ERRORLOG`; Linux: `/var/opt/mssql/log`. The current file has NO extension; `ERRORLOG.1` is the most recent archive, and about six are kept (Microsoft Learn, "Viewing the SQL Server Error Log") | The two-line failed-login pair: `Error: 18456, Severity: 14, State: 8.` then `Login failed for user '<user_name>'. [CLIENT: <ip address>]`. **The State is the answer**: 2 and 5 user id not valid, 6 Windows name used with SQL auth, 7 login disabled AND password wrong, 8 password incorrect, 11 and 12 login valid but server access failed, 18 password must be changed, 38 and 46 database not found, 58 SQL auth attempted against a Windows-auth-only server, 122-124 empty user name or password, 126 database requested by user does not exist (Microsoft Learn, MSSQLSERVER_18456). Microsoft's own reason for why the state matters: "To increase security, the error message that is returned to the client deliberately hides the nature of the authentication error. However, in the SQL Server error log, a corresponding error contains an error state that maps to an authentication failure condition." State 1 is documented as "Error information isn't available" - so a password-spray question is answered by counting State 8 rows, and it can only be answered from this file |
| MSSQL, feature enablement | same file | A `Configuration option '<name>' changed from <a> to <b>.` line names the option and both values. Grep the option name the question asks about rather than reading the file; the line is the evidence and the timestamp is the answer |
| MySQL error log | `slow_query_log_file` and the error log both default into the data directory | Field order is `time thread [label] [err_code] [subsystem] msg`, documented example `2020-08-06T14:25:03.109022Z 5 [Note] [MY-010051] [Server] Event Scheduler: ...` (MySQL 8.4 reference, error log format). `MY-010926` is the `Access denied for user` message and `MY-010914` the aborted connection - both from secondary sources only, UNVERIFIED against the MySQL manual here, so confirm against the bundle's own lines. Access denied is logged at `[Note]` level, so it is absent unless `log_error_verbosity` is 3 |
| MySQL slow query log | default name `<host_name>-slow.log` in the data directory (MySQL 8.4 reference, slow query log) | Each entry is preceded by a `SET timestamp=...` and a `#` header carrying `Query_time`, `Lock_time`, `Rows_sent`, `Rows_examined`. `Rows_examined` far exceeding `Rows_sent` on a `SELECT` with a string literal is the shape of an injected boolean or a dump. `log_timestamps` decides the timezone: "Default Value UTC, Valid Values UTC SYSTEM" (MySQL 8.4 reference, server system variables). Two consequences the same paragraph states: it covers the error log, the general query log and the slow query log **written to files**, and it does NOT affect the same messages written to the `mysql.general_log` and `mysql.slow_log` TABLES - those stay in the local system time zone. So a bundle that ships a table dump instead of a file needs `CONVERT_TZ()`, not the variable |
| Exchange message tracking | `%ExchangeInstallPath%TransportRoles\Logs\MessageTracking`, files `MSGTRK<Service>yyyyMMdd-nnnn.log`, where the service suffix is empty for Transport, `MA` for moderation, `MD` for mailbox delivery and `MS` for mailbox submission. CSV with `#Software`, `#Version`, `#Log-Type`, `#Date`, `#Fields` headers; `#Date` and `date-time` are UTC ISO 8601 (Microsoft Learn, "Message tracking") | `event-id` is the verb and the answer to "what happened to the message": `RECEIVE`, `SEND`, `DELIVER`, `FAIL`, `DSN`, `EXPAND`, `TRANSFER`, `REDIRECT`, `DROP`, `THROTTLE`, `CLIENTSUBMISSION`, `SUBMIT`, `AGENTINFO`. Then `sender-address`, `recipient-address` (semicolon separated), `recipient-status`, `message-subject`, `client-ip`, `original-client-ip`, `total-bytes`, `recipient-count`, `message-id`, `network-message-id`, `directionality` (`Incoming`, `Originating`, `Undefined`), `source` (`SMTP`, `STOREDRIVER`, `AGENT`, `MAILBOXRULE`, `ROUTING`, `DSN`, ...). **`network-message-id` is the join key**: it persists across every copy a message forks into, so it follows one mail through bifurcation and group expansion where `internal-message-id` does not. A `MAILBOXRULE` source on an outbound message means an inbox rule generated it - that is auto-forwarding, and for a "Message generated by inbox rules" the `reference` field "contains the Internal-Message-Id value of the inbound message that caused the inbox rule to generate the outbound message", which is the join back to the mail that triggered it. For a spoofed-sender question read `return-path` (the envelope `MAIL FROM`, "never empty", null sender written `<>`) against `sender-address` (the `Sender:` header, or `From:` when `Sender:` is absent) - they disagree exactly when the envelope and the header disagree |
| Tomcat access log | `<CATALINA_BASE>/logs/`. The valve's own defaults are `prefix="access_log"` and an empty `suffix`, but the `conf/server.xml` shipped with Tomcat configures `prefix="localhost_access_log" suffix=".txt" pattern="%h %l %u %t &quot;%r&quot; %s %b"`, which is why the file on disk is `localhost_access_log.<yyyy-MM-dd>.txt` - `fileDateFormat` defaults to `.yyyy-MM-dd`, and the same page states that its date format is always local time, so the date in the file NAME is local even when the rows inside are not (Tomcat 10.1 valve reference; apache/tomcat `10.1.x` `conf/server.xml`) | The shipped pattern is Common, so there is NO user agent and NO referer unless someone set `pattern="combined"`. **`%D` is a version trap**: the Tomcat 9 reference documents it as milliseconds and says "In httpd %D is microseconds. Behaviour will be aligned to httpd in Tomcat 10 onwards"; the Tomcat 10.1 reference documents it as microseconds. Check the Tomcat version before treating `%D` as a duration. `%F` is milliseconds to commit the response, `%I` is the request thread name (which joins a log line to a `catalina.out` stack trace), `%b` is bytes or `-` if zero, `%B` is bytes as a number. The valve escapes `"` as `\"`, `\` as `\\`, uses C escapes for `\f \n \r \t`, and encodes any other control character or code point above 127 as a Java `\uXXXX` - so an injected non-ASCII payload is in the file as `\uXXXX`, not as the byte |
| Tomcat `catalina.out` | `<CATALINA_BASE>/logs/catalina.out` | Unrotated stdout and stderr of the JVM. `%I` in the access log is documented as "Current request thread name (can compare later with stacktraces)", so when the pattern carries it the join is literal - take the thread name off the access-log row and run `grep -n -A40 "$THREAD" catalina.out` to get the stack trace for that exact request. The frame naming the deployed webapp package is the answer to "which application"; a `catalina.out` that stops mid-line is a killed JVM, and its last timestamp is the answer to when |
| Squid access log | upstream default `daemon:/usr/local/squid/var/logs/access.log squid`; distro packages relocate it, so read the `access_log` line from the config rather than assuming (squid `access_log` configuration reference) | The default `squid` format is `%ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt` (squid `logformat` reference). **Field 1 is epoch seconds with milliseconds, not a date** - that is the single most common misread of a Squid log. Then response time in ms, client address, `<squid status>/<HTTP status>` as one slash-joined field such as `TCP_MISS/200`, reply size, method, the full URL including host, the username, `<hierarchy status>/<server address>`, and the content type. Squid also predefines `common` and `combined`, whose lines look like Apache's but carry an extra `%Ss:%Sh` at the end: `logformat combined %>a - %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st "%{Referer}>h" "%{User-Agent}>h" %Ss:%Sh`. Measured here: the section 2 regex, which anchors on `\s*$`, does NOT partially match such a line - it fails outright and lands in the unparsed count. That is the good failure, provided you actually count unparsed lines instead of discarding them |
| ProxySG / Edge SWG main HTTP access log | ELFF text, one `#Fields` header like IIS | Field order of the reserved main HTTP format is `date time time-taken c-ip cs-username cs-auth-group s-supplier-name s-supplier-ip s-supplier-country s-supplier-failures x-exception-id sc-filter-result cs-categories cs(Referer) sc-status s-action cs-method rs(Content-Type) cs-uri-scheme cs-host cs-uri-port cs-uri-path cs-uri-query cs-uri-extension cs(User-Agent) s-ip sc-bytes cs-bytes x-virus-id ...` (Broadcom KB 168187). Note the two proxy-only fields: **`s-action`** is what the proxy DID (served, denied, tunnelled) and **`sc-filter-result`** plus **`cs-categories`** is why - a request to an uncategorised or newly registered host that the proxy still allowed is the exfiltration channel. The HTTPS main format omits `cs(Referer)`, `cs-uri-path` and `cs-uri-query` by design, so a URL path question cannot be answered from an SSL log unless interception was on |
| Windows Event Forwarding | Collected events land in the `ForwardedEvents` log on the collector, or in whatever `<LogFile>` the subscription XML names (Microsoft Learn, "Setting up a Source Initiated Subscription") | The forwarder's own state is on the SOURCE host in `Microsoft-Windows-Eventlog-ForwardingPlugin/Operational`: event **104** "The forwarder has successfully connected to the subscription manager at address <FQDN>" and event **100** "The subscription <name> is created successfully". The Group Policy that points a host at a collector is Computer Configuration\Administrative Templates\Windows Components\Event Forwarding, policy "Configure the server address, refresh interval, and issuer certificate authority of a target Subscription Manager", written as `Server=HTTPS://<FQDN>:5986/wsman/SubscriptionManager/WEC,Refresh=<seconds>,IssuerCA=<thumbprint>`. The registry key that policy writes is UNVERIFIED here - the Microsoft page names the policy, not the key. Two consequences for an investigation: a `ForwardedEvents` log holds records whose `Computer` field is the SOURCE host, so never read the collector's name as the affected host; and a source that stopped forwarding leaves a gap in `ForwardedEvents` and a reason in the ForwardingPlugin channel on the source |

## 6. Not covered here, and where it is

- **The EVTX side of every pivot** - dumping, event-ID tables, Sysmon field names,
  the cleared-log checklist: `windows-event-logs.md`.
- **Proving a file on disk** - `$MFT`, `$J`, `$Recycle.Bin`, `Zone.Identifier`,
  the merged filesystem timeline: `filesystem-timeline.md`.
- **Registry-backed execution evidence** - Amcache, Prefetch, ShimCache, the
  hives and their transaction logs: `registry-and-execution.md`.
- **The capture, not the log** - `tshark`, conversations, object export,
  CloudTrail JSON, Linux `auth.log` and `wtmp`: `network-and-cloud.md`.
- **The dropped file itself** - analysing a webshell's code, a PE, a packed
  script: `memory-and-malware.md` for the triage, `../ctf-malware/SKILL.md` for
  the depth.
- **Answer format, timezone and precision** - read before submitting:
  `answer-discipline.md`.
- **A parser that is not installed** - `toolchain.md` carries the install ranks
  and what each one buys.
- **Exploiting a web application rather than reading its logs** - that is a
  different task and a different router: `../web-triage/SKILL.md`.

## Falsifier

This file is the wrong one when the web log has already given up the request and
the remaining question is about the HOST - what the request caused to run, what
it wrote, what survived a reboot. A web log records requests; it does not record
processes, files or registry values. The moment the answer needs a command line,
a file hash, a service or a run key, the pivot has left this file: go to
`windows-event-logs.md` for execution, `filesystem-timeline.md` for what landed
on disk, `registry-and-execution.md` for what persisted.

It is also the wrong file when the "log" in the bundle is a SIEM export rather
than a server's own log - a Splunk or Elastic CSV, a Sentinel export, an EDR
alert table. Those carry a vendor's normalised field names, not IIS's or
Apache's, and the `#Fields` and `LogFormat` reasoning above does not apply.
Read the export's own header row, treat the normalised fields as a second
opinion, and join back to the original artifact before answering.
