# Request smuggling reference map

This directory belongs to the canonical `web-request-smuggling` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| Front and back may disagree on where a body ends | `cl-te-desync.md` |
| A websocket or protocol upgrade sits in the path | `upgrade-smuggling.md` |
| A value lands in a response or request header, raw | `crlf-injection.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the desync needs a concrete byte sequence or a
confirmation wording.

Every technique here was distilled from a field note in `../field-notes.md`;
the request shapes below are the ones that actually worked on a live target.
