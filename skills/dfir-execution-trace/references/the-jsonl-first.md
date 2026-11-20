# Convert once, filter many

`evtx_query.py --input FILE.evtx` decodes BinXML directly now;
`.jsonl`/`.json`/`.xml` accepted. Convert once to JSONL, then filter
many times — `--field-contains`/`--since`/`--answer` per question.

## Once

Convert once, filter many.

## The shapes

.evtx/.jsonl/.json/.xml all accepted.
