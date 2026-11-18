# SOAP Deep — the envelope grammar and the injection slots

## The envelope grammar — every element

```xml
<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:m="urn:example">
  <soap:Header>
    <m:AuthHeader>
      <m:Token>&x;</m:Token>              — header-entity injection
    </m:AuthHeader>
  </soap:Header>
  <soap:Body>
    <m:MethodName>
      <m:param1>&x;</m:param1>            — body-entity injection
      <m:param2>&x;</m:param2>
    </m:MethodName>
  </soap:Body>
</soap:Envelope>
```

The entity can live in `<soap:Header>` elements, `<soap:Body>` params,
or inside nested children — the parser expands everywhere.

## The SOAP namespaces — the two versions

```
SOAP 1.1:  http://schemas.xmlsoap.org/soap/envelope/
SOAP 1.2:  http://www.w3.org/2003/05/soap-envelope/
```

The namespace URI must be right — a 1.1-envelope-namespace on a 1.2-
expecting service = parse error — fingerprint the version via the error.

## The `mustUnderstand`/`actor`/`role` — the routing attrs

```xml
<soap:Header>
  <m:H soap:mustUnderstand="1" soap:actor="urn:x">&x;</m:H>
  <m:H2 soap:role="http://...">...</m:H2>
</soap:Header>
```

`mustUnderstand="1"` — the receiver MUST process the header or fault —
an entity inside a mustUnderstand header is guaranteed-evaluated.

## The `<soap:Fault>` — the response-side surface

```xml
<soap:Envelope>
  <soap:Body>
    <soap:Fault>
      <faultcode>soap:Client</faultcode>
      <faultstring>&x;</faultstring>      — the error-channel inside the spec
      <faultactor>http://x</faultactor>
      <detail><m:d>&x;</m:d></detail>
    </soap:Fault>
  </soap:Body>
</soap:Envelope>
```

If the service echoes a Fault — the `faultstring`/`detail` carry the
substituted entity — the spec-defined error channel.

## The `m:MethodName` — discovering operations

`?wsdl` returns `<wsdl:definitions>` listing `<wsdl:operation name="...">`
+ the `<xs:element>` for each param — inject entities into the right
param element — the WSDL is the method-map.

## The `Content-Type`/`SOAPAction` — the SOAP-1.1-required headers

```
Content-Type: text/xml                  — SOAP 1.1
SOAPAction: "urn:Method"                — SOAP 1.1
Content-Type: application/soap+xml      — SOAP 1.2
Content-Type: application/soap+xml; action="urn:Method"  — SOAP 1.2
```

`SOAPAction` selects the method for 1.1 — the action-name is NOT an
entity — but it routes which method runs.

## The `<m:encoded>`/`xsi:type` — the type-annotated params

```xml
<m:param xsi:type="xsd:string">&x;</m:param>
```

`xsi:type` annotates the param type — the entity inside still expands —
the type just describes the value.

## The `soapenc`/`soapenc:Array` — the array params

```xml
<m:list soapenc:arrayType="xsd:string[3]">
  <item>&x;</item><item>&x;</item>
</m:list>
```

Entity inside an array item — each item is a substitution point.

## The `attachments`/`MIME` — SOAP-with-attachments

`multipart/related` — a SOAP envelope + MIME attachments — the CID-
referenced parts — `cid:` URIs inside the envelope — a nested-fetch
channel.

## The `WS-Security`/`wsse` — the security headers

```xml
<wsse:Security>
  <wsse:UsernameToken>
    <wsse:Username>&x;</wsse:Username>
    <wsse:Password>&x;</wsse:Password>
  </wsse:UsernameToken>
  <ds:Signature>
    <ds:KeyInfo><ds:X509Data><ds:X509Certificate>&x;</ds:X509Certificate></ds:X509Data></ds:KeyInfo>
  </ds:Signature>
</wsse:Security>
```

The security-header elements are parsed by the WS-Security handler —
entities inside them expand before auth checks — the pre-auth-parse
gap.

## The `ds:Signature`/`ds:SignedInfo` — the signature context

The XML-DSig inside `<wsse:Security>` — `<ds:RetrievalMethod URI="...">` —
the URI is fetched during canonicalization — an OOB fetch WITHOUT
entities.

## The `xfire`/`axis`/`cxf`/`metro`/`jaxws` — the Java SOAP libs

| Lib | Parser | XXE |
|---|---|---|
| Axis2 | AXIOM/StAX | depends |
| Apache CXF | StAX | yes if configured |
| Metro/JAX-WS-RI | StAX | yes |
| SAAJ | DOM | yes |
| Spring-WS | DOM/StAX | yes |
| .NET WCF/ASMX | XmlReader | default-Prohibit |
| PHP SoapClient/Server | libxml2 | yes |

## The "the service names the parser" — the error fingerprint

- `javax.xml.soap`/`AxisFault`/`org.apache.axis` → Axis
- `com.sun.xml.ws`/`metro` → Metro
- `org.apache.cxf` → CXF
- `System.Web.Services`/`SoapException` → .NET ASMX
- `WCF`/`System.ServiceModel` → WCF
- `libxml`/`SoapFault`/`SOAP-ENV` → PHP
- `Zeep`/`suds` → Python

## The "the WSDL is itself XML" — the secondary surface

If you can get the app to PARSE a WSDL you supply — a `?wsdl`-import
feature, an "import service definition" — the WSDL's `<xsd:schema>`
carries entities — a WSDL-XXE — a niche second surface.
