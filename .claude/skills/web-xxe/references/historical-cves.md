# Historical CVEs — the named XXE incidents

## The parser-library CVEs — where the bugs lived

- **CVE-2014-3660** — libxml2 — recursive entity expansion DoS — the
  amplification-cap origin
- **CVE-2015-8317** — libxml2 — entity expansion
- **CVE-2017-7375/7376** — libxml2 — entity expansion DoS
- **CVE-2021-** — ongoing libxml2 entity bugs
- **Java Xerces** — the `FEATURE_SECURE_PROCESSING` lineage — the
  features weren't on by default
- **.NET XmlReader** — `DtdProcessing` defaults changed across versions —
  pre-4.5.2 = Parse = live; 4.5.2+ = Prohibit
- **PHP libxml** — `LIBXML_NOENT`-related
- **Python lxml/minidom/sax** — the `resolve_entities`/`feature_external_ges`
  defaults

## The framework CVEs — where the app was vulnerable

- **CVE-2017-9805** — Apache Struts REST plugin — `XStream`/XML
  deserialization — the "accept `application/xml`" shape
- **CVE-2018-11759** — Apache Tika — OOXML/XML XXE
- **CVE-2019-*** — Jenkins, Confluence, GitLab — plugin XML parsers
- **CVE-2020-** — SAML libraries — `python-saml`, `OpenSAML`, `xmlsec`
- **CVE-2021-** — SOAP/XML-RPC libs — `xmlrpc`, `Zeep`, `JAX-WS`, `CXF`
- **WordPress `xmlrpc.php`** — historic XML-RPC XXE + pingback SSRF
- **SAP NetWeaver** — the enterprise XML surfaces
- **Oracle WebLogic** — `wls-wsat`/`uddi`/`bea_wls*` XXE
- **Microsoft Exchange** — `EWS`/`autodiscover` XML
- **Microsoft Office / LibreOffice** — OOXML/ODF XXE

## The library CVEs — the common carriers

- **Apache POI** — OOXML parsing XXE
- **Apache CXF/JAX-WS/Metro** — SOAP XXE
- **XStream/Jackson-XML/JAXB** — data-binding XXE
- **Castor/XmlBeans/JibX** — data-binding
- **dom4j/JDOM/woodstox** — parser wrappers
- **Nokogiri/REXML** — Ruby
- **lxml/xml.etree/defusedxml** — Python
- **xml2js/xmldom/libxmljs** — Node
- **golang stdlib `encoding/xml`** — safe-by-design — no entities
- **PHPWord/PHPPresentation/PhpSpreadsheet** — OOXML libs
- **Apache FOP/POI/Tika** — doc-conversion
- **ImageMagick/librsvg/Batik** — rasterizer XXE
- **Exiftool/XMP-Toolkit** — metadata XXE
- **APKTool/jadx/dex2jar** — Android XXE
- **Maven/Ant/Gradle/Ivy** — build-file XXE
- **MSBuild** — `.csproj` XXE

## The "the CVE tells you the config" — pattern

A CVE named "XXE" is almost always "the default config resolved
external entities and nothing turned it off" — the fix is the config
hardening — `hardening-configs.md` — the same config tells you which
payload tier still works.

## The "the CVE is the fingerprint" — identifying the vulnerable version

- an Apache CXF version → `wsdl`-XXE
- a `python-saml` version → SAML-XXE
- a Struts version → REST-plugin XXE
- a POI version → OOXML XXE
- a `Nokogiri` version → `noent`-XXE

`banner`/version disclosure → known-CVE lookup → the likely-payload.

## The "the CVE is not the whole story" — the config matters MORE than the lib

A "vulnerable" lib with `DtdProcessing.Prohibit` hardening applied is
safe; a "fixed" lib with the hardening reverted is not. The CVE names
the config-to-check, not the verdict — the internal-entity echo is
still the test.
