# EICAR & AV Differentials — fingerprinting the scanner

## The EICAR string — the universal AV canary

```
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

A 68-byte test string every AV flags — safe, non-executable, designed for
this exact use. Upload a file containing it and watch:

| Result | Meaning |
|---|---|
| `200` file stored | no AV scanning at upload |
| `403`/`400` "virus"/"malware" | AV present — the rejection IS the scanner signature |
| `200` but file deleted on fetch | post-scan quarantine — race window possible |
| `200` file served clean | AV present but allowed it (rare) or scanned and mis-classified |

## What an AV check changes for exploitability

- `<?php`/`eval`/`system` patterns get caught — obfuscate (webshell
  variants — `webshell-advanced.md`)
- polyglots and non-shell payloads survive — the AV sees "a png with odd
  bytes", not a shell
- race the scan: file written → fetch before quarantine —
  `race-and-temp-files.md`

## The timing oracle — scan adds latency

A `.php` upload taking 800ms where `.txt` took 50ms suggests a scan ran —
differential timing reveals the AV even when it accepts the file.

## Bypass shapes that fool scanners — not just extension

- polyglot: real PNG structure + appended shell — the AV sees a valid png
  (header+IDAT+IEND) — most scanners don't check trailing bytes
- webshell written to look like an image file's EXIF/comment
- archive inside archive — depth limits
- charset tricks — `<?php` utf-16 encoded — scanner sees odd bytes, PHP
  reads the decoded form if the handler decodes
- shell inside IDAT — a png whose image data is `<?php` — only works if
  the server serves it as php (polyglot naming)

## The "AV but consumer-side" subtlety

The upload AV scans; the SINK (pdf reader, image processor) doesn't run
through AV — a payload inside a crafted pdf/docx targets the consumer,
not the scanner — `document-attacks.md`/`imagemagick-deep.md`.

## GTUBE/CSIRT test patterns — for other scanners

- `GTUBE` — the spam-filter canary (like EICAR for SMTP/anti-spam)
- `AMTSO` feature-check files for DLP/sandboxing

## When the AV rejects everything — the honest stop

If `.php`+.exe+EICAR all reject and the app gives no oracle to work
around — the upload surface is a dead end unless the consumer-side sink
exists. `falsifier`: every payload class is rejected AND no
parser/consumer path exists.

## Falsifiers

- EICAR uploads fine and serves back — no AV (the scanner itself is not
  the exploit, but this tells you shells survive)
- EICAR rejected AND every bypass tried rejects AND no consumer sink

## Output to record

- EICAR upload result verbatim (the status + any AV banner) + whether
  scan timing shows on benign uploads
