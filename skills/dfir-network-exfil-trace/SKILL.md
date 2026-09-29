---
name: dfir-network-exfil-trace
description: >
  Action-oriented depth skill for Network and exfiltration trace. Use after the router or
  tools/classify.py names this class; start with the first probe and record the expected
  signal. Do not use it as proof of a finding. Confusable classes: dfir-execution-trace,
  dfir-cloud-audit-trace.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, network, pcap, exfiltration, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Network and exfiltration trace

**Catalogue class.** This toolkit has never solved one. What follows is standard published knowledge, not local
experience - treat it as a starting point and record what actually happens in `field-notes.md`.

Answers "what left the host, to where, how much, over what channel". Not "what ran" (dfir-execution-trace owns Sysmon 1 / 4688 `CommandLine`),
not "which control-plane API call" (dfir-cloud-audit-trace owns CloudTrail `eventName`, `userIdentity.arn`).

## First probe
```bash
capinfos -a -e -c -z capture.pcapng
tshark -r capture.pcapng -q -z io,phs -z endpoints,ip
```

`endpoints,ip` prints `Packets | Bytes | Tx Packets | Tx Bytes | Rx Packets | Rx Bytes` per host, so "how many bytes left this host" is one row,
never a hand sum. Measured here (tshark 4.0.7) on a 48-packet scapy fixture - 20 TCP frames of 400-byte payload out, 20 ACKs back, 8 DNS TXT
queries: `10.10.10.5  48  11776  28  9896  20  1880`. `Tx Bytes` 9896 is the answer to "how much left this host"; `Bytes` 11776 is both
directions and is not.

**Falsifier** - the observation that closes this class: `io,phs` lists nothing above `tcp`/`udp`/`tls`, every `endpoints,ip` row has `Tx Bytes` in
the low kilobytes with no external peer dominating, and no host-side counter exists either - no `SRUDB.dat`, no `pfirewall.log`, and
`evtx_query.py`'s `summary.by_event_id_all_records` shows no Sysmon 3, no Sysmon 22, no 5156.

## Recognise
| In the bundle | What this class reads out of it |
|---|---|
| `*.pcap`, `*.pcapng` | the tap set below; the only family with byte counts per direction |
| `sysmon.jsonl`, Sysmon EVTX | event 3 `DestinationIp` / `Initiated`, event 22 `QueryName` / `QueryResults` |
| `Security.evtx`, WFP auditing on | 5156 `Application` + `DestAddress` + `DestPort` + `Direction` |
| `sru/SRUDB.dat` | per-application `BytesSent` / `BytesRecvd` - the host-side volume oracle |
| `Downloader/qmgr.db` | a transfer job's `RemoteName` and `LocalName` |
| `Firewall/pfirewall.log` | `src-ip dst-ip dst-port size path` per packet, W3C text |

## Confirm
1. Prove the protocol exists with `io,phs` before writing any display filter, then rank peers with `-z conv,tcp` and `-z conv,udp` and name the one external address carrying the bulk.
2. Read the direction, not the total. `conv,tcp` prints the `<-` byte column **before** `->`. Measured row from the same fixture:
   `10.10.10.5:50000 <-> 185.199.0.7:443   20 1,880 bytes   20 9,080 bytes   40 10 kB   0.000000000   1140.1000`. The first pair (1,880) is
   B-to-A, the second (9,080) is A-to-B, and it agrees with `endpoints,ip` `Tx Bytes` 9896 minus the 816 bytes of DNS. So "sent by A" is the
   **second** pair, and the trailing two columns are relative start and duration in seconds.
3. Quote the record: a `-T fields` row or a `follow,tcp` chunk. `--verdict confirms` needs a verbatim excerpt, never a retyped number.

## tshark taps, measured on this box
| Tap | Answers |
|---|---|
| `-z io,phs` | which protocols are present at all, frames and bytes per layer |
| `-z conv,tcp`, `-z conv,udp` | per-peer frames and bytes, `<-` then `->`, relative start, duration |
| `-z endpoints,ip` | per-host `Tx Bytes` / `Rx Bytes` - the direct "how much left" answer |
| `-z dns,tree` | one tree with `rcode`, `opcodes`, `Query/Response`, `Query Type` (leaf `TXT (Text strings)`), `Class`, `Payload size`, `Query Stats -> Qname Len` Count/Average/Min/Max, `Label Stats -> 1st/2nd/3rd/4th Level or more`, `Response Stats -> no. of answers`, `Service Stats -> request-response time (msec)` and `no. of retransmissions`. Leaf names measured on this box |
| `-z http,tree`, `-z http_req,tree`, `-z http_srv,tree` | status codes, requested URIs, per-server request counts |
| `-z follow,tcp,ascii,<stream-index>` | one reassembled stream. Syntax is `prot,mode,filter[,range]` and the filter is a stream index or `ip0:port0,ip1:port1` (tshark(1) man page on this box) |
| `-z io,stat,<secs>,<filter>` | volume per interval - the beacon rate without pandas |
| `-z credentials` | cleartext credentials the dissectors recognised |

`--export-objects <proto>,<destdir>` takes exactly six protocols in this build (measured with `tshark --export-objects help,.`): `dicom`,
`ftp-data`, `http`, `imf`, `smb`, `tftp`. `imf` is mail bodies, `ftp-data` is the file that went over FTP; add `-Q` to mute the packet summary. With
a keylog file, decryption is one preference: `-o tls.keylog_file:sslkeys.log` (line 5387 of `tshark -G currentprefs` here; `ssh.keylog_file` 5019
and `wg.keylog_file` 5630 also exist).

## The extraction primitive
```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y \
  -e frame.time_epoch -e ip.src -e ip.dst -e tcp.dstport -e udp.dstport \
  -e http.host -e http.request.full_uri -e dns.qry.name -e dns.qry.name.len \
  -e dns.qry.type -e tls.handshake.extensions_server_name -e frame.len > net.csv
```

All twelve names were checked against `tshark -G fields` here (each one printed by `tshark -G fields | awk -F'\t' '$1=="F"{print $3}'`). `tls.handshake.extensions_server_name` is the SNI, the only destination name
available when the session is encrypted and no keylog shipped; `frame.len` is on-the-wire length, so a sum over it exceeds the payload. Merge
with the host timelines through
`python3 tools/forensics/timeline_merge.py --source net.csv:frame.time_epoch:net --source sysmon.jsonl:Event.System.TimeCreated.SystemTime:sysmon --challenge <name> --gap 600`:
it accepts `.csv .tsv .tab .jsonl .ndjson .jsonlines` plus a per-source `--filetime`, normalises every clock to UTC, counts unparsed rows
instead of dropping them, and reports the largest gaps (18/18 offline cases, `python3 tools/forensics/selftest.py`).

## Beaconing arithmetic
```python
import pandas
net = pandas.read_csv("net.csv")
net["ts"] = pandas.to_datetime(net["frame.time_epoch"], unit="s", utc=True)
net.sort_values("ts", inplace=True)
key = ["ip.src", "ip.dst", "tcp.dstport"]
net["delta"] = net.groupby(key)["ts"].diff().dt.total_seconds()
print(net.dropna(subset=["delta"]).groupby(key)["delta"].agg(n="count", median="median",
    mad=lambda s: (s - s.median()).abs().median(), cv=lambda s: s.std() / s.mean()).sort_values("cv"))
```

Run here against a synthetic 30 s beacon with +/-3 s jitter mixed into random browsing: the beacon row came out `n=39 median=30.14 mad=1.36
cv=0.054`, the browsing row `n=11 median=395.21 mad=104.64 cv=0.546`. A jittered beacon still sits an order of magnitude below normal traffic on
`cv`, and `mad/median` (4.5 percent here) is the jitter figure a question asks for. `utc=True` is not optional: a mixed-offset column degrades to
object dtype and sorts as text.

Same answer straight from the capture: `-z io,stat,60,"SUM(frame.len)frame.len and ip.src==10.10.10.5"` gave `1362, 908, 908, 908, ...` bytes
per minute here. **The field must appear inside the filter string as well as inside `SUM()`** - tshark(1) says so, and the shorter
`SUM(frame.len)ip.src==10.10.10.5` silently returns 0 in every interval. Measured.

## DNS tunnelling and encoded-payload tells
| Tell | Filter or command |
|---|---|
| over-long query names | `-Y 'dns.qry.name.len > 50'`; `-z dns,tree` prints `Qname Len` Min/Average/Max in one pass (fixture 38/38/38) |
| unusual record types | `-Y 'dns.qry.type in {10,16}'` - 16 is TXT, 10 is NULL; verified returning 16 here |
| deep labels under one parent | `-z dns,tree`, `Label Stats` -> `4th Level or more` count |
| query rate | `-z io,stat,1,"COUNT(dns.qry.name)dns.qry.name"`; fixture peaked at 3 in one second |
| one server taking everything | `-z conv,udp`, or `-e dns.qry.name` piped to `awk -F. '{print $(NF-1)"."$NF}' \| sort \| uniq -c` |
| high-entropy first label | `python3 -c 'import sys,math,collections;s=sys.argv[1];c=collections.Counter(s);n=len(s);print(round(-sum(v/n*math.log2(v/n) for v in c.values()),2))' <label>`. **Measured here at DNS-label length (32-48 chars), entropy alone does not separate the two cases**: prose 3.83, base32 4.37, base64 4.41, **hex 3.72 - below prose**. Use it only against base32/base64, and for a hex tunnel match the alphabet instead: `-Y 'dns.qry.name matches "^[0-9a-f]{16,}[.]"'`. Use `[.]`, not `\.` - tshark 4.0.7 rejects the latter with `\. is not a valid character escape sequence`. It over-matches any all-hex word (`deadbeef`, `facade`), so pair it with a length floor |

Payload reassembly already exists with working code - do not restate it: `skills/ctf-forensics/network-advanced.md:423-457` (label decode, 9-byte
per-chunk header, retransmission de-duplication) and `:111-181` (data in the last byte of each query name).

## Host side, when there is no capture
| Artifact | Exact location | Field that answers |
|---|---|---|
| Sysmon 3 | `Microsoft-Windows-Sysmon/Operational` | `DestinationIp`, `DestinationPort`, `DestinationHostname`, `DestinationPortName`, `Initiated`, `Protocol`; join to the process by `ProcessGuid` |
| Sysmon 22 | same channel | `QueryName`, `QueryStatus` (0 is success), `QueryResults`, `ProcessGuid` |
| WFP audit | `Security`, event 5156 | `Application`, `Direction`, `SourceAddress`, `SourcePort`, `DestAddress`, `DestPort`, `Protocol`, `FilterRTID`, `LayerName` |
| SRUM | `C:\Windows\System32\sru\SRUDB.dat` | table `{973F5D5C-1D90-4944-BE8E-24B94231A174}` "Network Data Usage Monitor", nine columns in order: `AutoIncId`, `TimeStamp` (OLE Automation date, not FILETIME), `AppId`, `UserId`, `InterfaceLuid`, `L2ProfileId`, `L2ProfileFlags`, `BytesSent`, `BytesRecvd` |
| transfer queue | `C:\ProgramData\Microsoft\Network\Downloader\qmgr.db` (`qmgr0.dat` / `qmgr1.dat` pre-Windows 10) | `RemoteName` (the URL), `LocalName` (where it landed) |
| firewall log | `%systemroot%\system32\LogFiles\Firewall\pfirewall.log` | `src-ip dst-ip src-port dst-port size path` |
| DNS client | `Microsoft-Windows-DNS-Client/Operational` | 3006 query issued: `QueryName, QueryType, QueryOptions, ServerList, IsNetworkQuery, NetworkQueryIndex, InterfaceIndex, IsAsyncQuery`. 3008 query completed: `QueryName, QueryType, QueryOptions, QueryStatus, QueryResults` - 3008 is the one carrying the resolved address |

- **Sysmon 3 field order** is `RuleName, UtcTime, ProcessGuid, ProcessId, Image, User, Protocol, Initiated, SourceIsIpv6, SourceIp, SourceHostname, SourcePort, SourcePortName, DestinationIsIpv6, DestinationIp, DestinationHostname, DestinationPort, DestinationPortName` (OSSEM EventId-3). `Initiated` true means the local process opened it. The event is **disabled by default** (Microsoft Learn, Sysmon), so absence is a configuration fact, not innocence. Event 22 is `RuleName, UtcTime, ProcessGuid, ProcessId, QueryName, QueryStatus, QueryResults, Image, User`, and that telemetry only exists on Windows 8.1 and later.
- **5156** needs the *Audit Filtering Platform Connection* subcategory enabled (Microsoft Learn, 5156). `Application` is a device path such as `\device\harddiskvolume2\documents\listener.exe`, not `C:\...`, so match the basename. `Protocol` is numeric: 1 ICMP, 6 TCP, 17 UDP, 47 GRE, 50 ESP, 51 AH. `Direction` is a message-table token - `%%14592` in Microsoft's own inbound sample XML; `%%14593` for outbound is UNVERIFIED here, so decode it against the local provider before quoting it.
- **SRUM** needs an ESE reader and neither `esedbexport` nor python `libesedb` is on this box today (install route: `skills/dfir-sherlock-triage/toolchain.md`). Usage is `esedbexport [-c codepage] [-l logfile] [-m mode] [-t target] [-T table_name] [-hvV] source`, writing a `<basename>.export/` directory of TSV tables. `AppId` and `UserId` are index values into `SruDbIdMapTable`, so a raw numeric `AppId` is never the answer. `{DD6636C4-8929-4683-974E-22C046A43763}` is the companion "Network Connectivity Usage Monitor" table (libyal esedb-kb, SRUM).
- **pfirewall.log** logs nothing until *Log dropped packets* or *Log successful connections* is on, and the documented recommendation splits it into `pfirewall_Domain.log`, `pfirewall_Private.log`, `pfirewall_Public.log` (Microsoft Learn, Configure Windows Firewall logging) - check all four names. Index from the file's own `#Fields:` line; the documented set is `date time action protocol src-ip dst-ip src-port dst-port size tcpflags tcpsyn tcpack tcpwin icmptype icmpcode info path`, `-` marks an empty field, and `size` is bytes, so summing `size` per `dst-ip` gives volume. The **default maximum is 4,096 KB and old
entries are deleted once it is reached**, so a missing early record may be rotation rather than absence - check whether the file starts with a
`#Version`/`#Fields` header block or mid-line. Enabled on a live host with
`netsh advfirewall set allprofiles logging allowedconnections enable` (same Learn page).
- **The transfer service** also writes `Microsoft-Windows-Bits-Client/Operational`: 3 job created, 59 BITS started transferring a file for the job, 60 BITS stopped transferring (the status code carries the outcome), 4 job
completed with user, job name, job id, owner and file count. Upload and download produce the same 3-59-60-4 sequence, so direction comes from
`RemoteName` versus `LocalName`, not from the event ids. The per-event field lists are UNVERIFIED here - read them off the local provider
manifest before quoting one as an answer.

Day zero, with no EVTX parser installed, the queryable route is the JSONL one, and `--answer FIELD` pulls that field from the first match and
prints the `tools/hooks.py pre-flag` argv so the value is never retyped:

```bash
python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 3 \
  --field-contains DestinationIp=. --challenge <name> \
  --class dfir-network-exfil-trace --hypothesis-id h1 \
  --evidence-kind class --answer DestinationIp
```

## Zeek and Suricata bundles
Zeek TSV carries its own header, so never assume column order: `head -8 conn.log` prints `#separator`, `#fields`, `#types`, and `zeek-cut` reads
that header. Columns, in `Conn::Info` declaration order (docs.zeek.org, `base/protocols/conn/main.zeek`), are `ts uid id.orig_h id.orig_p id.resp_h id.resp_p
proto service duration orig_bytes resp_bytes conn_state local_orig local_resp missed_bytes history orig_pkts orig_ip_bytes resp_pkts
resp_ip_bytes tunnel_parents`. **`local_orig`, `local_resp` and `missed_bytes` sit between `conn_state` and `history`** - a hardcoded
`cut -f13` aimed at `history` lands on `local_orig` instead. `missed_bytes > 0` means the sensor dropped payload, so `orig_bytes` under-counts
and a volume answer taken from it is wrong. `orig_bytes` is application-layer payload while `orig_ip_bytes` sums the IP
`total_length` field, so the two differ by header overhead and a question about "data" means the former. In `history`, uppercase letters are
originator events and lowercase are responder. `dns.log`, `http.log`, `ssl.log`, `files.log` and `notice.log` all pivot off `uid`.

Suricata `eve.json` is one object per line keyed by `event_type`; documented values include `alert`, `flow`, `dns`, `http`, `tls`, `fileinfo`,
`ftp`, `ftp_data`, `smb`, `ssh`, `anomaly` (Suricata eve-json-format). Volume lives in `event_type == "flow"`: `bytes_toserver`, `bytes_toclient`,
`pkts_toserver`, `pkts_toclient`, `start`, `end`, `age`. Rank it with `jq -r 'select(.event_type=="flow") | [.flow.start, .src_ip, .dest_ip, .dest_port, .flow.bytes_toserver, .flow.bytes_toclient] | @tsv' eve.json | sort -k5 -nr | head`.
An alert names a signature, not a byte count. Pivot on `flow_id`, which both the alert and the flow record carry:
`jq -r 'select(.event_type=="alert")|[.flow_id,.timestamp,.alert.signature]|@tsv' eve.json` then
`jq -r --arg f <flow_id> 'select(.event_type=="flow" and (.flow_id|tostring)==$f)|.flow' eve.json` for that flow's
`bytes_toserver`/`bytes_toclient`.

## Linux side
| Source | What to pull |
|---|---|
| `/var/log/syslog`, `/var/log/kern.log` | iptables `LOG` lines prefixed `IN= OUT= SRC= DST= LEN= PROTO= SPT= DPT=`; sum `LEN` per `DST` |
| journald | `journalctl --file <dir>/system.journal -o short-iso-precise -u ssh` keeps ISO-8601, so it merges without reparsing |
| triage collection text | captured `ss -tunap` or `netstat -anp` output: `Local Address:Port` / `Peer Address:Port` / process is a point-in-time socket table, not a history |
| `auth.log`, `wtmp`, `btmp` | already at `skills/dfir-sherlock-triage/network-and-cloud.md`, Linux host artifacts - do not duplicate |

## Traps
- A timeout, a truncated capture, or `capinfos` reporting fewer packets than the question implies, is a transport fact. Record `inconclusive`.
- `conv,tcp` prints `<-` before `->`. Reading the first byte column as "sent" inverts every exfiltration answer.
- Several `-z` taps combine in one pass but are **not** emitted in argument order: measured, `-z io,phs -z endpoints,ip` printed the endpoints table first. Parse by table title, never by position.
- `SUM(<field>)<filter>` returns 0 in every interval unless `<field>` is inside the filter string too.
- `frame.len` sums include headers; Zeek `orig_bytes` does not. Say which one produced the number.
- SNI and `http.host` are client claims - what the process asked for, not where the bytes went. `ip.dst` is the observation.
- `scapy` 2.6.1 is installed: walk a large capture with `PcapReader`, not `rdpcap`, which loads the whole file.

## Routing
Shares signals with `../dfir-execution-trace/` (the process behind the socket) and `../dfir-cloud-audit-trace/`
(an API call, not a byte count). Check those first. Depth, one named file at a time:

- `skills/dfir-sherlock-triage/network-and-cloud.md:124-146` - the Linux host artifacts block (`auth.log` greps, `last -f wtmp`, `last -f btmp`);
  the earlier part of the same file is the router's long form on large captures and CloudTrail
- `skills/ctf-forensics/network.md:197-236` - `follow,tcp` reverse-shell and credential tells
- `skills/ctf-forensics/network-advanced.md:26-63` - inter-packet timing as an encoding, with the interval-to-bit code
- `skills/ctf-forensics/linux-forensics.md:42-63` - a Linux chain ending in a TFTP transfer out

Names for a writeup, never for a verdict: T1041 exfiltration over the C2 channel, T1048 over an alternative protocol, T1567 over a web service,
T1071.004 application-layer protocol DNS, T1572 protocol tunnelling, T1030 data transfer size limits, T1029 scheduled transfer, T1197
transfer-service jobs (MITRE ATT&CK).

## Discipline
One question, one filter, one quoted record. Three attempts inside the same artifact family with no new record is the stop condition: change
artifact family, not filter syntax. Every verdict goes through `tools/hooks.py post-probe`, and a byte count summed in your head instead of printed
by a tool is not evidence.

## Field notes
`field-notes.md` in this directory grows every time a challenge of this class is solved. Entries marked
`proposed` are awaiting review; `confirmed` entries have been checked. See `../../LEARNING_LOOP.md`.
