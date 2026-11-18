# PHAR Format Deep — the stub, manifest, and metadata anatomy

## Why phar matters — the unserialize sink is the metadata

`phar://` access on ANY file whose stub/manifest parses triggers PHP
`unserialize` on the manifest's metadata field — no `.phar` extension
required, and the file can be a polyglot (JPEG+phar). Any file-op API on a
path you control reaches it: `file_exists`, `is_file`, `fopen`,
`file_get_contents`, `getimagesize`, `exif_read_data`, `md5_file`,
`filemtime`, `copy`, `rename`, `include`, `require`.

## The phar structure

```
[stub: PHP code ending in __HALT_COMPILER(); ?>
[manifest: manifest-len | n-files | flags | alias-len | alias |
          metadata-len | serialized-metadata]
[file entries: name-len | name | usize | ts | csize | crc | flags |
              metadata-len | metadata | content]
[signature (optional)]
```

The metadata field is `serialize()`d PHP — ANY object the app's autoloader
can reach becomes a POP chain entry point → `../web-deserialization` skill
for the chain catalog.

## The stub — what makes it parse as phar

```php
<?php __HALT_COMPILER(); ?>
```

Must end the stub. Before it, arbitrary PHP/text — including `GIF89a` —
the file is simultaneously a gif-sniff-pass and a phar. The classic
JPEG-phar: stub first, then the manifest, then the file entries that ARE
jpeg bytes; `getimagesize` reads the manifest region looking for SOI —
crafted so it ALSO reads as jpeg.

`tools/web/archive_gen.py phar` builds this without PHP on the box:

```bash
# canary — stdClass metadata, proves the unserialize fired (error/side-effect):
python3 tools/web/archive_gen.py phar --out x.phar --marker

# real metadata — your POP gadget's serialize string:
python3 tools/web/archive_gen.py phar --out x.phar \
  --metadata 'O:8:"Exploit":1:{s:4:"prop";s:8:"payload";}'

# --content supplies the stub text; --alias sets the phar alias
```

## The `phar://` URL forms

```
phar://uploads/x.phar/inner.php       — include the inner file
phar://uploads/x.jpg/test             — phar stored under .jpg name
phar://x.phar/x                        — absolute path
phar:///abs/path/x.phar/inner
```

The wrapper keys on content — ext is irrelevant. `phar://` reads the
manifest from any position the stub parse allows.

## Which file-ops trigger unserialize — the honest list

| API | Triggers metadata unserialize? |
|---|---|
| `file_exists`/`is_file`/`is_dir` | yes (manifest parse) |
| `fopen`/`file_get_contents`/`readfile` | yes |
| `include`/`require` | yes |
| `getimagesize` | yes — path into the wrapper |
| `exif_read_data`/`exif_thumbnail` | yes — classic trigger (imagetok!) |
| `md5_file`/`sha1_file`/`filesize`/`filemtime`/`filectime`/`fileperms`/`fileinode`/`fileowner`/`filegroup`/`filetype`/`stat` | yes — stat family |
| `copy`/`rename`/`unlink`/`chmod`/`touch` | yes |
| `mime_content_type` | yes — finfo wrapper |

`htb-imagetok`: `exif_read_data`/`getimagesize` on an uploaded "image" is
the phar trigger — the upload IS the phar.

## The two wins — include vs deserialize

- `include 'phar://x.phar/inner.php'` — the inner file executes — needs
  `phar://` in the include path AND the file to exist
- metadata unserialize — any file-op triggers it — needs a POP chain for
  the app's classpath

## Defenses — and their state

- `phar.readonly=1` (default) — blocks phar *creation*, NOT phar:// access
- `open_basedir` — path containment, blocks traversal to the phar
- disabled `phar` extension — kills the wrapper entirely (check `phpinfo`)
- `allow_url_include`/`allow_url_fopen` — `phar://` is a stream wrapper —
  `allow_url_fopen=0` does NOT disable `phar://` on local paths
- `stream_wrapper_unregister('phar')` in app — kills it locally

## Signature section — does it matter

Phar signatures (md5/sha/openssl) validate on `phar::loadPhar`/`->getSignature`
calls — most `phar://` unserialize paths don't check it.
`archive_gen.py` emits without signature — sufficient for the sink.

## The polyglot layering for image-passing validators

`phar` stub can contain a full GIF/JPEG before `__HALT_COMPILER`:

```
GIF89a [gif image bytes] <?php __HALT_COMPILER(); ?> [manifest] [entries]
```

Wait — the stub must be parseable — actually the stub IS free PHP text
before `__HALT_COMPILER`: `GIF89a...<?php __HALT_COMPILER();?>` works —
`getimagesize` sees the GIF header, `phar://` sees the stub+manifest.

## `phar://` vs `phar:` — wrapper name

`phar://` is canonical; `phar:` unqualified is not a wrapper call in most
contexts. Also `compress.zlib://phar://` chains? The wrapper nesting —
`phar://` inside `compress` — mostly dead; plain `phar://` is the target.

## Falsifiers

- `phar` extension disabled or `stream_wrapper_unregister('phar')` in the
  app's bootstrap
- no request-controlled path ever reaches a file-op API
- metadata unserialize works but no POP chain exists for the classpath
  (different problem — `web-deserialization` says when to give up)

## Output to record

- the file-op endpoint + the `phar://` path that triggered unserialize
- the metadata class + chain used
- the verbatim side-effect/output proving the chain fired
