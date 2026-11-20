# One-page command sheet

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## The capture pass

```bash
capinfos -a -e -c -z capture.pcapng
tshark -r capture.pcapng -q -z io,phs -z endpoints,ip
tshark -r capture.pcapng -q -z conv,tcp -z conv,udp
tshark -r capture.pcapng -q -z dns,tree -z http_req,tree
python3 tools/forensics/pcap_triage.py --input capture.pcapng --challenge <n>
```

## The extraction pass

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y \
  -e frame.time_epoch -e ip.src -e ip.dst -e tcp.dstport -e udp.dstport \
  -e http.host -e http.request.full_uri -e dns.qry.name -e dns.qry.name.len \
  -e dns.qry.type -e tls.handshake.extensions_server_name -e frame.len > net.csv
```

## The DNS tunnel pass

```bash
tshark -r capture.pcapng -Y 'dns.flags.response==0' -T fields -e dns.qry.name > qnames.txt
python3 tools/forensics/dns_exfil.py --names qnames.txt
```

## The beacon pass

```bash
tshark -r capture.pcapng -q -z io,stat,60,"SUM(frame.len)frame.len and ip.src==H"
tshark -r capture.pcapng -Y 'tcp.stream==N' -T fields -e frame.time_delta
```

## The host-side pass

```bash
python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 3 \
  --field-contains DestinationIp=. --challenge <n> \
  --class dfir-network-exfil-trace --hypothesis-id h1 --evidence-kind class
python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 22 \
  --field-contains QueryName=. --challenge <n>
python3 tools/forensics/evtx_query.py --input security.jsonl --event-id 5156 \
  --field-contains Direction=. --challenge <n>
```

## The merge

```bash
python3 tools/forensics/timeline_merge.py \
  --source net.csv:frame.time_epoch:net \
  --source sysmon.jsonl:Event.System.TimeCreated.SystemTime:sysmon \
  --challenge <n> --gap 600
```

## The export pass

```bash
mkdir -p ex
for p in http ftp-data imf smb tftp dicom; do tshark -r capture.pcapng -Q --export-objects $p,ex; done
ls -l ex/
```

Every command above is verified against the tool's own `--help` or the
measured tshark 4.0.7 build on this box. Do not add flags that were not
checked.
