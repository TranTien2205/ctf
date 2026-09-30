# Network and cloud

The two artifact families that are fully workable on this box with zero installs.
Every command below was run here; the tool versions are `tshark 4.0.7` and
`pandas 2.3.3`.

## Large-capture discipline

A Sherlock capture is routinely 130-500 MB. Never open one blind.

```bash
capinfos capture.pcapng                       # size, packet count, first/last time
tshark -r capture.pcapng -q -z io,phs         # which protocols are even present
```

`io,phs` is the protocol hierarchy. Read it before writing a display filter: it
answers "is there any DNS in here at all" in one pass, which stops a filter that
was never going to match.

## From capture to conversation

```bash
tshark -r capture.pcapng -q -z conv,tcp       # peers ranked by bytes
tshark -r capture.pcapng -q -z conv,udp
tshark -r capture.pcapng -q -z dns,tree       # query names, response codes
```

`conv,tcp` answers the exfiltration questions directly: the columns carry frames
and bytes per direction, so "how much was sent to the attacker" is read, not
estimated. Note the direction columns separately - a question asking what was sent
*out* is the A->B column, not the total.

## Extraction into pandas

The CSV extraction primitive. This is how a capture becomes a timeline that merges
with the EVTX timeline.

```bash
tshark -r capture.pcapng -T fields -E separator=, -E header=y \
  -e frame.number -e frame.time_epoch -e ip.src -e ip.dst \
  -e tcp.srcport -e tcp.dstport -e _ws.col.Protocol -e frame.len \
  > net.csv
```

```python
import pandas
net = pandas.read_csv("net.csv")
net["ts"] = pandas.to_datetime(net["frame.time_epoch"], unit="s", utc=True)
```

Always `utc=True`. A mixed-offset column silently degrades to object dtype and
sorts as text, which puts 09:00 before 10:00 but 10:00 before 9:00.

## Transferred files

```bash
tshark -Q --export-objects http,./objects -r capture.pcapng
tshark -Q --export-objects smb,./objects -r capture.pcapng
```

When the bundle supplies a TLS keylog file, decryption is a preference override,
not a separate step. The preference `tls.keylog_file` exists in this tshark build
(confirmed with `tshark -G currentprefs`):

```bash
tshark -r capture.pcapng -o tls.keylog_file:sslkeys.log -q -z conv,tcp
```

For a programmatic walk over a capture too large to hold, `scapy` is installed
(2.6.1); iterate with `PcapReader` rather than `rdpcap`, which loads everything.

## Suricata or Zeek output, when the bundle ships it

A bundle sometimes ships alert JSON or Zeek TSV logs instead of, or alongside, the
raw capture. Treat them as a second opinion, not as truth: an alert names a
signature, and the question usually wants the underlying field. Join alert
timestamps back to frame numbers in the capture and read the answer from the
packet.

## AWS CloudTrail

The confirmed cloud provider across sampled Sherlocks is AWS: a `CloudTrail/` tree
of gzipped JSON plus, often, an S3 bucket tree walked as an ordinary filesystem.
Azure, Entra and M365 bundles are UNVERIFIED here - no sampled bundle contained
one, so do not assume that branch exists.

```bash
find CloudTrail -name '*.json.gz' | wc -l
zcat CloudTrail/**/*.json.gz | jq -r '.Records[] | [
  .eventTime, .eventName, .eventSource, .sourceIPAddress,
  .userIdentity.arn, .userAgent, (.errorCode // "")
] | @tsv' > trail.tsv
```

Four fields answer most CloudTrail questions:

| Field | Question it answers |
|---|---|
| `eventName` | what API action was taken |
| `sourceIPAddress` | from where |
| `userIdentity.arn` | as whom (and `.type` distinguishes Root, IAMUser, AssumedRole) |
| `userAgent` | with what tool - a CLI string here is a strong signal |

Into pandas for ordering and counting:

```python
import pandas
trail = pandas.read_csv("trail.tsv", sep="\t", header=None, dtype=object,
    names=["eventTime","eventName","eventSource","sourceIP","arn","userAgent","errorCode"])
trail["ts"] = pandas.to_datetime(trail["eventTime"], utc=True)
trail.sort_values("ts", inplace=True)
```

`dtype=object` matters: without it, account ids and anything hex-looking are
coerced to float and the answer you copy out is wrong in its last digits.

Useful shapes:
- First successful action by a principal: filter `errorCode` empty, sort, take head.
- Reconnaissance before impact: `eventName` beginning `List`, `Get` or `Describe`,
  immediately preceding a `Create`, `Put` or `Delete`.
- Credential origin: `userIdentity.type == "AssumedRole"` names the role in `arn`;
  the session name after the last `/` is often the answer.

## Linux host artifacts

When the bundle carries a Linux triage collection (a Cat-Scale style tarball, or a
bare `/var/log` tree):

```bash
grep -aE "Accepted (password|publickey)" auth.log      # successful logins
grep -acE "Failed password" auth.log                    # brute-force volume
grep -aE "session opened for user" auth.log
```

`wtmp` and `btmp` are binary. Measured today, `last`, `lastb`, `lastlog` and
`utmpdump` are all **absent here**, so do not plan a minute-three command around
them: walk the struct instead. The record is **384 bytes**, so the record count is
the file size divided by 384 — an invariant, unlike any absolute size, because
`wtmp` grows with every login. The format string and the `ut_type` values are in
`../dfir-authentication-trace/SKILL.md`.

A brute-force question usually wants three values that all come from `auth.log`
anyway: the count of failures, the source address, and the timestamp of the first
success that follows them.

Persistence on the Linux side lives in `/etc/systemd/system/` and
`~/.config/systemd/user/` timers and services, `~/.ssh/authorized_keys`, crontabs
under `/var/spool/cron/`, and `/etc/ld.so.preload`. Compare file mtimes against
the intrusion window rather than reading every file.

## Falsifier

This file is the wrong one when the capture is only a carrier for something hidden
inside it - a file to extract, a covert channel to decode. That is
`../forensics-triage/SKILL.md`, not this.
