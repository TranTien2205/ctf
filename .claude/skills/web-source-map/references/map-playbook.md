# Map playbook — the `.map` recovery runbook

## Step 1: find the map

```bash
# route 1: the sourceMappingURL comment in the bundle tail
curl -s "$B" | tail -c 400 | grep -oE 'sourceMappingURL=[^ ]+'
# route 2: the sibling <bundle>.js.map
curl -s -o m.json -w '%{http_code} %{content_type}\n' "$B.map"
# route 3: the SourceMap/X-SourceMap header
curl -sI "$B" | grep -iE 'sourcemap'
# route 4: an inline data: map
curl -s "$B" | grep -oE 'sourceMappingURL=data:[^ ]+' | tail -1
```

## Step 2: confirm it is a map

```bash
head -c 20 m.json   # '{"version":3' -> a real map; '<!DOCTYPE'/'<html' -> a catch-all
```

A `200 application/json` starting `{"version":3` is a map; a `200
text/html` is the SPA catch-all, not a map.

## Step 3: reconstruct with `bundle_miner`

```bash
python3 tools/web/bundle_miner.py --map m.json --out recovered/ \
  --source-scheme normalise --skip-node-modules
```

`normalise` strips `webpack://`/`../` so `webpack://app/./src/x.js`
becomes `src/x.js`; a `sources` path escaping `--out` is rejected.

## Step 4: or decode by hand

```python
import json
m = json.load(open('m.json'))
sc = m.get('sourcesContent') or [None]*len(m['sources'])
for src, content in zip(m['sources'], sc):
    if content:
        print('===', src); print(content[:1500])
```

## Step 5: read the recovered source

```bash
ls recovered/                                        # the file tree
grep -rniE 'TODO|FIXME|HACK|secret|password|key|flag|admin|internal|debug' recovered/
grep -rniE 'eval|innerHTML|deserialize|pickle|exec|spawn|child_process|readFile|render_template|__proto__' recovered/
grep -rnoE '(flag|ctf)\{[^}]*\}|const\s+FLAG' recovered/
```

## Step 6: the `sourcesContent`-absent path

`sources` present, no content → file names only:

```bash
python3 -c "import json;print('\n'.join(json.load(open('m.json'))['sources']))" | sort -u
# probe the hosted paths
for p in src/config/x.js src/api/y.js; do curl -s -o /dev/null -w '%{http_code} ' "$BASE/$p"; echo "$p"; done
```

## Step 7: the adjacent probe

A `.map` presence signals a lax deployment:

```bash
for p in /.git/HEAD /.env /backup.zip /src/ /static/maps/; do
  printf '%-16s ' "$p"; curl -s -o /dev/null -w '%{http_code}\n' "$BASE$p"
done
```

## The untrusted-source rule

Read recovered source; never execute it. A `sources` path that
traverses is rejected; a recovered "source" may be planted.
