# Framework Sinks — per-stack upload handling and its weak spots

## PHP — `$_FILES` and the famous traps

```php
$f = $_FILES['f'];
$f['name']     // client name — NEVER trust; traversal + double-ext live here
$f['type']     // client Content-Type — always spoofable
$f['tmp_name'] // server path — the real bytes
$f['size']
move_uploaded_file($f['tmp_name'], $dir . $f['name']);  // ← naive sink
```

Weak spots:

- `$f['type']`/`$_POST['type']` checked instead of `finfo_file($f['tmp_name'])`
- `pathinfo($f['name'], PATHINFO_EXTENSION)` on a double-ext name — reads last only
- `basename` absent → `move_uploaded_file` honors `../` in name
- `in_array($ext, $white)` case-sensitivity — `.PhP` vs `['php']` blacklist/whitelist
- `exif_imagetype`/`getimagesize` shallow-sniff bypassed by real-image+payload
- `mime_content_type`/`finfo` — stronger but still prefix-grade
- `is_uploaded_file`/`move_uploaded_file` vs `copy`/`rename` — the latter
  allow path tricks on `tmp_name`
- `preg_match('/\.(jpe?g|png|gif)$/i', $name)` — whitelist anchored `$` —
  defeated by `x.php%00.jpg` on old PHP, or by newline `x.php\n.jpg`? No —
  newline breaks it for both sides. `$` before final newline means
  `x.jpg\n` still matches while `basename` keeps `x.jpg\n` — try it.

### Laravel/Symfony specifics

- `$file->getMimeType()` (sniffed) vs `getClientMimeType()` (header) — a
  check on the client one is a header spoof away
- `storeAs($path, $name)` with `$name` from request → traversal
- `$request->file('f')->getClientOriginalName()` into a path → traversal
- Symfony `File::move($dir, $name)` — same

## Node.js — multer / busboy / formidable / express-fileupload

```js
upload.single('file')                    // multer
req.file.originalname                    // client name — same traps
req.file.mimetype                        // client header
```

Weak spots:

- `fileFilter` checks `mimetype` only — spoof
- `filename: (req,file,cb) => cb(null, file.originalname)` — custom name
  fn that keeps traversal
- `limits.fileSize` only — no content check at all
- `path.join(uploadDir, file.originalname)` — traversal
- no ext check because "Node doesn't execute by ext" — true, but the
  file lands somewhere a template/import/processor reads it
- `express-fileupload` `useTempFiles` — temp path race
- `mv()`/`saveAs()` with request-controlled path

## Python — Flask/Django/FastAPI

```python
request.files['f']                      # Flask
f.filename                              # client name
f.save(os.path.join(UP, f.filename))    # naive sink — traversal
secure_filename(f.filename)             # the mitigation — check it's USED

request.FILES['f']                      # Django
f.name                                  # client name — Django does NOT
                                        # sanitize on its own
UploadedFile.content_type               # header
default_storage.save(name, f)           # sink

await file.read() / file.filename       # FastAPI UploadFile
```

Weak spots: absent `secure_filename`, `Path() / filename` join, custom
sanitizer that strips `..` once (`....//` survives), extension check on
`filename.split('.')[-1]`, content check via `imghdr`/`PIL.verify()` on the
prefix only.

## Java — Spring `MultipartFile` / Servlet `Part`

```java
file.getOriginalFilename()              // client name — Java decodes %..%
file.getContentType()                   // header
new File(dir, file.getOriginalFilename())
Files.copy(in, Paths.get(dir, name))
```

Weak spots: `getOriginalFilename` traversal — Java `File` honors `..` and
absolute paths; `FilenameUtils.getExtension` vs double-ext; Tika
`detect(InputStream)` prefix-grade; `.jsp`/`.war` uploads that autodeploy
or land in a JSP-compiled dir.

## ASP.NET — `IFormFile` / `HttpPostedFileBase`

```csharp
file.FileName                           // client name — \ and / both split
Path.Combine(root, file.FileName)       // traversal on Windows separators
file.ContentType                        // header
```

Weak spots: `Path.Combine` honors `..\` AND `/`; `Path.GetExtension` on
`x.aspx;1.jpg` vs IIS handler mapping `.aspx`; content check via
`Image.FromStream` (structural but not payload-safe).

## Ruby — Rails `ActionDispatch::Http::UploadedFile` / CarrierWave / Shrine

```ruby
params[:file].original_filename         # client name
params[:file].content_type              # header
File.open(Rails.root.join('public','uploads', name), 'wb') { |f| f.write(...) }
```

CarrierWave/Shrine/`ActiveStorage` — `ActiveStorage` serves via
`/rails/active_storage/` redirect to storage URL (disk service under
`/rails/active_storage/disk/...`) — files land with encoded keys; direct
path guessing fails; watch `config/storage.yml` for the service. Disk
service serves bytes verbatim — a stored `text/html` upload is an XSS
file if the disk endpoint serves its recorded content_type (it does —
from the blob).

## The multiplexer — APIs that parse multipart differently

- `PUT`/`PATCH` binary bodies — some APIs accept raw `Content-Type:
  application/octet-stream` bodies as uploads — bypass multipart validators
- JSON-upload APIs — `{"filename":..., "content": base64}` — no multipart
  parser in the loop; checks on `filename`+`content` differ
- tus/resumable — chunked assembly; each chunk may skip validation that
  only ran on chunk 0
- GraphQL upload spec (`operations`/`map` fields) — multipart carried but
  field names differ; validators looking for `name="file"` miss `name="0"`

## Sinks to grep for — the white-box list

```
PHP:    move_uploaded_file, copy($_FILES, rename, file_put_contents(.$_FILES
        file_get_contents($_FILES[..tmp_name])
Node:   upload.single/array/fields, busboy, formidable, .mv(, .pipe(fs.createWriteStream
Python: f.save(, shutil.copyfileobj, open(.*filename.*w|wb), zipfile.extractall,
        tarfile.extractall, default_storage.save
Java:   transferTo, Files.copy, new File(dir, getOriginalFilename)
Rails:  File.open(.wb), IO.copy_stream, ActiveStorage::Blob.create_and_upload
.NET:   CopyToAsync/SaveAs with Path.Combine(.*FileName)
Generic: archive extract calls, importer entry points, "plugin/theme install"
```

## Output to record

- the framework + the exact sink API found
- which claim it trusts (name/MIME/sniffed) + the sanitizer absent
