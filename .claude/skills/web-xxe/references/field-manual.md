# Field Manual — the tables you pull mid-engagement

## The entity-type table

| Decl | Reference | Scope | Use |
|---|---|---|---|
| `<!ENTITY x "v">` | `&x;` | body | marker |
| `<!ENTITY x SYSTEM "u">` | `&x;` | body | file/URL read |
| `<!ENTITY % p "v">` | `%p;` | DTD | DTD-building |
| `<!ENTITY % p SYSTEM "u">` | `%p;` | DTD | fetch/OOB |
| `<!ENTITY u SYSTEM "u" NDATA n>` | attr `u` | body | unparsed read |

## The file-path table — the first 10 reads

```
/etc/passwd                /etc/hostname
/etc/hosts                 /etc/os-release
/proc/self/environ         /proc/self/cmdline
/proc/self/cwd             /proc/self/exe
/proc/net/tcp              /proc/1/environ
/var/www/html/index.php    /var/www/html/.env
/app/main.py               /app/config.yml
/root/flag                 /flag  /flag.txt
C:\windows\win.ini         C:\windows\system32\drivers\etc\hosts
C:\inetpub\wwwroot\web.config
```

## The protocol table

| Scheme | Java | .NET | libxml2 | PHP | Python(lxml) | Node |
|---|---|---|---|---|---|---|
| `file:` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `http:` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `ftp:` | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `data:` | — | — | ✓ | ✓ | ✓ | — |
| `php://` | — | — | — | ✓ | — | — |
| `phar://` | — | — | — | ✓ | — | — |
| `expect://` | — | — | — | ✓ | — | — |
| `jar:`/`netdoc:` | ✓ | — | — | — | — | — |
| `gopher:` | old | — | curl | curl | curl | — |
| `smb:`/UNC | — | ✓ | — | — | — | — |

## The content-type table

| Content-Type | Surface |
|---|---|
| `application/xml` | generic XML |
| `text/xml` | SOAP/XML-RPC legacy |
| `application/soap+xml` | SOAP 1.2 |
| `application/atom+xml`/`rss+xml` | feeds |
| `image/svg+xml` | SVG |
| `application/xslt+xml` | XSLT |
| `application/wsdl+xml` | WSDL |
| `application/x-www-form-urlencoded` | `xml=` field |
| `multipart/form-data` | file-upload |
| `application/json` | nested `xml` field |

## The error→parser table

| Error | Parser |
|---|---|
| `SAXParseException` | Java |
| `XmlException`/`DTD is prohibited` | .NET |
| `libxml`/`DOMDocument`/`simplexml` | PHP |
| `XMLSyntaxError`/`lxml`/`ElementTree`/`ParseError` | Python |
| `REXML`/`Nokogiri` | Ruby |
| `Expat`/`xml2js`/`sax` | Node |
| `encoding/xml` | Go |
| `EntitiesForbidden` | defusedxml |

## The entity-config-flags table — the hardening flags

| Flag | Parser | Kills |
|---|---|---|
| `disallow-doctype-decl` | Java | all DOCTYPE |
| `external-general-entities` | Java | `&x;` ext |
| `external-parameter-entities` | Java | `%x;` ext |
| `load-external-dtd` | Java | ext-DTD fetch |
| `DtdProcessing` | .NET | DOCTYPE |
| `XmlResolver` | .NET | ext resolution |
| `LIBXML_NOENT` | PHP | ext-entity expand |
| `no_network` | lxml | fetches |
| `resolve_entities` | lxml | expansion |

## The exfil-channel table

| Channel | Content limit | Egress need |
|---|---|---|
| `?d=` query | ~8KB | HTTP |
| path | ~8KB | HTTP |
| DNS label | 63c alnum-dash | UDP 53 |
| FTP command | ~8KB | FTP |
| error URI | ~4KB | none (in-band) |
| header | ~8KB | HTTP |

## The "which flag-path" table

| Stack | Flag locations |
|---|---|
| Linux | `/flag` `/flag.txt` `/root/flag` `/app/flag` `/var/flag` |
| Docker | `/proc/1/environ` `FLAG` env `/run/secrets/*` |
| k8s | `/var/run/secrets/kubernetes.io/...` |
| Windows | `C:\flag.txt` `C:\Users\*\Desktop\flag.txt` |
| PHP | `.env` `config.php` `getenv("FLAG")` |
| Python | `.env` `os.environ["FLAG"]` |
| Node | `.env` `process.env.FLAG` |
| Java | `application.properties` `System.getenv` |

## The budget table — the rung-cost

| Rung | Probes | Time |
|---|---|---|
| baseline | 1 | 5s |
| `&probe;` | 1 | 5s |
| `file:`-read | 1 | 5s |
| OOB-hit | 1 | 5s |
| blind-exfil | 2-4 | 2m |
| XInclude | 1 | 5s |
| per-mechanism cap | 5 | 15m |
