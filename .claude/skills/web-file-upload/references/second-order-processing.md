# Second-Order Processing — the file that's never served but always read

## The shape — the exploit lives in what consumes the upload

```
upload → stored → later processed by:
  thumbnailer / image resizer
  importer / parser (csv, docx, zip, yaml, xml)
  renderer / converter (PDF, preview, ffmpeg, gs, wkhtmltopdf)
  indexer / scanner / virus scan
  mailer / notifier / report builder
```

The upload response is irrelevant — the payoff is in the consumer's
output or side effects.

## The consumer inventory — where to look

| Consumer | File types | Impact paths |
|---|---|---|
| image resize/thumbnail | png/jpg/svg/mvg | ImageTragick, ghostscript, pixel-survival |
| document preview | docx/pdf/odt | XXE in parts, gs/latex RCE, HTML injection into the render |
| data import | csv/json/xml/yaml | formula injection, XXE, typed-unmarshal |
| archive extract | zip/tar/rar/phar | zip-slip, symlink, phar deser |
| virus scan | any | argv via filename, clamav quarantine race |
| indexing/search | text/pdf/doc | extraction artifacts leaking content |
| pdf/doc generation | html/md/tex | injected markup in generated output |
| email/ticket | eml/msg/ics | HTML in rendered view |
| analytics/ML | npy/pkl/csv | pickle/yaml deser — `web-deserialization` |

## Proving the consumer exists — black-box signals

- upload response says "processing"/"queued"/"scheduled" — async worker
- a `/status/<id>` or webhook endpoint changes state over time
- a thumbnail/preview appears later with different bytes
- an import log/result endpoint
- the response is instant but a *later* GET shows derived data
- a bot/worker fetches a URL you embedded in the file (oob hit)

## The "the output is the exfil channel" pattern

The payload's effect surfaces in a *generated artifact*:

- XXE in docx → parsed text in a preview/extract → flag in the text
- gs `\write`/`%pipe%` → file written then fetched separately
- latex `\input` → flag inside the produced PDF → `pdf_text.py --find-flag`
- HLS concat → file bytes inside the transcoded media
- formula injection → rendered cell values in a re-exported csv

Read the artifact back through whatever endpoint serves it — the upload
endpoint's 200 means nothing; the derived artifact's bytes are the proof.

## The marker loop — tracking upload → consumer → artifact

```bash
M="MK_$RANDOM"
# upload a file carrying the marker in a field the consumer will echo
# e.g., docx dc:title, csv cell, svg <title>, pdf metadata
# then poll the consumer-visible endpoint for the marker:
python3 tools/web/http_probe.py --challenge "$C" --class web-file-upload \
  --url "$BASE/api/documents/$ID" \
  --evidence-regex "$M" --evidence-kind surface \
  --on-match inconclusive --on-miss inconclusive
```

Marker present in the derived output → the consumer pipeline is mapped;
marker absent after N polls → consumer doesn't echo that field — move the
marker to a different field.

## Delayed triggers — when the consumer runs on a schedule

- cron/worker every N minutes — upload, wait, re-check
- import runs on admin review — needs a privileged trigger
- scan runs on first download — trigger a read

## Serialization inside processing — the deser overlap

Importers that accept `.pkl`/`.npy`/`.joblib`/`.pt`/`.h5`/`.yaml`/`.mar`/`.sav`
hand the bytes to `pickle`/`yaml.load`/`marshal` → `web-deserialization`
skill for the payloads. The upload angle is just delivery.

## Falsifiers

- no consumer exists — the upload is store-and-serve only
- the consumer's output surface never reflects injected content (markered
  every field, still nothing)
- the consumer is byte-safe for the type you can upload

## Output to record

- the consumer identified + its trigger (timer/manual/download)
- the field where injected content surfaces
- the verbatim derived-artifact excerpt carrying the proof
