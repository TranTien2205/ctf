# Parser differential reference map

This directory belongs to the canonical `web-parser-differential` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| A path, route or host value is parsed twice | `path-normalization.md` |
| A proxy adds a trust header the backend believes | `proxy-header-abuse.md` |
| The front and back ends may disagree on the HTTP version or the vhost | `protocol-and-vhost.md` |
| A structured value (cookie, email header, token) is decoded differently at two layers | `structured-field-differentials.md` |
| The flag is in a header or path the client cannot set directly | `proxy-header-abuse.md`, then `path-normalization.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the differential needs a concrete request pair, a
named proxy behaviour, or a falsifier wording.

Every technique in this directory was distilled from a confirmed or proposed
field note in `../field-notes.md`; the probe pairs below are the ones that
actually worked on a live target.
