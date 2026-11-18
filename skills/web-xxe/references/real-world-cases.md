# Real-World Cases — the canonical XXE incidents and shapes

## The CVE catalog — the named cases

- **CVE-2014-3660** — libxml2 recursive entity expansion DoS — the
  amplification-cap origin
- **CVE-2017-9805** — Apache Struts REST plugin — `xstream`/XML
  deserialization XXE — the "accept: application/xml" content-type-confusion
  case
- **CVE-2018-1000849** — OpenMRS — XML parsing XXE
- **CVE-2018-11759** — Apache Tika — OOXML/XML XXE through document
  parsing
- **CVE-2019-*** — dozens of `XmlDocument`/`XmlReader` misconfigs
- **XML-RPC WordPress** — `xmlrpc.php` historic XXE/pingback
- **Apache Solr/Elasticsearch** — XML update endpoints
- **SAP NetWeaver / Oracle WebLogic** — enterprise XML surfaces
- **Spring/JAXB/CXF** — Java framework XXE classes
- **SAML libraries** — `xmlsectool`, `python-saml`, `OpenSAML` — the
  signature-before-parse order
- **Jenkins/GitLab/Confluence** — plugin/CI XML parsers
- **Microsoft Office / LibreOffice** — the OOXML/ODF XXE family
- **ImageMagick/librsvg** — the SVG XXE family
- **APKTool/jadx** — Android XML parsing
- **Exiftool/XMP** — embedded XMP XML in media
- **Ant/Maven/Ivy/Gradle** — build-file XXE (`build.xml`/`pom.xml`/
  `ivy.xml`) — developer-supplied XML
- **MSBuild** — `.csproj`/`.proj` import XXE

## The pentest classics — the field shapes

- **the `?wsdl` endpoint** — SOAP XXE — the go-to XXE surface
- **the XML API next to the JSON API** — `application/xml` content-type
  confusion
- **the SVG-upload** — XXE through a rasterizer
- **the DOCX "preview"** — OOXML text-extraction XXE
- **the SAML assertion** — pre-verification parse
- **the `Content-Type: text/xml` SOAP-ish REST** — a service that
  accepts both XML and JSON
- **the `.xml` config upload** — `web.config`, `pom.xml`, `.plist`
- **the feed-import** — RSS/Atom XXE
- **the `xmlrpc.php`** — WordPress
- **the OCR/doc-processing pipeline** — Tika/POI parsing a submitted doc

## The CTF classics — the shapes that recur

- **"the XML endpoint"** — explicit XML surface, entities on
- **"the JSON endpoint that also accepts XML"** — content-type confusion
- **"upload your avatar (SVG)"** — rasterizer XXE
- **"submit your config"** — `web.config`/`pom.xml`/`.plist` upload
- **"the SAML SSO endpoint"** — assertion XXE
- **"the RSS reader"** — feed XXE
- **"import your bookmarks (OPML)"**
- **"the secret is in a file, the parser is open"** — direct read

## The one verified card — `htb-xxe-content-type-branch`

`knowledge/chains/htb-xxe-content-type-branch-simplexml-noent-file-read.json`
— a JSON-shaped endpoint accepting `application/xml` — PHP `simplexml`
with `LIBXML_NOENT` — `file:`-read the flag. The trap it records:
don't stop at the JSON shape — the XML branch is live.

## The writeup-derived lessons — what solved writeups teach

- XXE is almost never the flag's last hop — it reads the SOURCE that
  names the flag's location
- the "the flag is in a comment/DTD" trick — read the DTD itself
- the "the flag is in an env var" — `/proc/self/environ`
- the "the flag is in a sibling container" — `file://` vs `http://`
  internal
- the "blind-XXE because the echo is suppressed" — param-entity OOB is
  the standard answer
- the "the endpoint takes XML but the app uses it differently" — SVG/
  DOCX/RSS shapes
- the "`data:`-URI DTD" — the no-listener trick for libxml2

## The "it looked like XXE but wasn't" — near-misses

- XPath injection — XML doc but no entities — different class
- XML Signature Wrapping — auth bypass — not entity-resolution
- Billion Laughs — DoS — not data-read
- XSLT injection — the stylesheet, not the entity — exec surface
- `XInclude` used as a read without DOCTYPE — often mislabeled "XXE"
  but it's a different mechanism — `xinclude.md`
