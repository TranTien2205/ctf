# Tap: --export-objects <proto>,<dir>

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

Reassembled files the protocol carried, written to a directory. In this
build (measured with `tshark --export-objects help,.`) exactly six protocols
are supported: `dicom`, `ftp-data`, `http`, `imf`, `smb`, `tftp`.

## Commands

```bash
mkdir -p ex && tshark -r capture.pcapng -Q --export-objects http,ex
tshark -r capture.pcapng -Q --export-objects ftp-data,ex
tshark -r capture.pcapng -Q --export-objects smb,ex
```

`imf` is mail bodies, `ftp-data` is the file that went over FTP. `-Q` mutes
the packet summary so the run is quiet in logs.

## Reading

Filenames come from the protocol metadata — a name is a claim inside the
capture, not evidence of a real path. Hash and carve the object itself; the
"what left" answer is the file bytes, not the name.

## Evidence rule

List the exported files with sizes (`ls -l ex/`) and quote that listing; then
let the file's own analysis (type, hashes) carry the "what" answer.

## Trap

Objects only export when the stream reassembles — dropped or truncated
segments silently skip files. Compare export count against `files.log`-style
expectations (or `http` object count vs `http_req` URI count).

## Pivot

Exported binary -> `forensics-pcap-carve`; exported document with metadata ->
`osint-media-metadata` style reading.
