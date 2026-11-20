# JSON logs — the structured shape

One JSON object per line — fields named, not positional.
`python3 -c` per line or jq if present; grep the key values.

## The approach

    python3 -c "import json,sys
    for l in open('app.log'):
        try: d=json.loads(l); print(d.get('level'),d.get('msg'))
        except: pass"

Extract a named field per line, then distribute. A jq one-liner
`jq -r .level app.log | sort|uniq -c|sort -rn` does the same when
jq is present. The named fields make it precise — no column
guessing.
