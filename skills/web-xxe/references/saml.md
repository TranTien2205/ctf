# SAML XXE — the identity-assertion surface

## Why SAML — assertions are signed XML

SAML responses are XML documents, usually wrapped in an XML signature.
The parsing pipeline: `base64-decode → XML parse → signature verify →
assertion read` — the XML parse happens BEFORE signature verification
on many stacks → XXE fires before the signature check.

## The surface — POST to the ACS endpoint

`POST /saml/acs` or `/sso/acs`/`/saml2/acs`/`/adfs/ls` with
`SAMLResponse=<base64>` — decode the base64 → XML → inject the
DOCTYPE+entity → re-base64 → send.

```xml
<?xml version="1.0"?>
<!DOCTYPE samlp:Response [<!ENTITY x SYSTEM "file:///flag">]>
<samlp:Response ...>
  <saml:Assertion>
    <saml:Subject><saml:NameID>&x;</saml:NameID></saml:Subject>
  </saml:Assertion>
</samlp:Response>
```

If `NameID` (or `AttributeValue`) is echoed in the response/error —
in-band read.

## The `<ds:Signature>`/`<ds:KeyInfo>`/`<ds:X509Data>` spots

Elements inside `<ds:Signature>` are parsed by the signature library —
a separate XML parse context — `X509Certificate`/`X509Data`/`KeyName`/
`RetrievalMethod` can carry entities:

```xml
<ds:KeyName>&x;</ds:KeyName>
<ds:RetrievalMethod URI="&x;"/>
<ds:X509Certificate>&x;</ds:X509Certificate>
```

`RetrievalMethod URI=` is itself an external-fetch primitive — an
OOB channel WITHOUT entities.

## The signature-wrapping adjacency — different bug, same surface

XML Signature Wrapping (XSW) — move the signed assertion deeper, put a
forged assertion at the top — signature validates the original while
the app reads the forged one. Not XXE but the same surface — record as
a separate class (auth bypass).

## Blind — param-entity in the assertion

The SAML response can carry a DOCTYPE — param-entity OOB exfil same as
any XML — `blind-xxe.md`.

## The pre-signature-parse order — the critical detail

If the stack parses XML BEFORE checking the signature (many do — you
must parse to FIND the signature), XXE fires regardless of signature
validity. If signature is verified via canonicalization first — still
parses entities during canonicalization — usually still fires.

## The meta-surface — IdP metadata / SP metadata fetch

`/saml/metadata`/`/metadata` endpoints serve XML — if the app FETCHES
a metadata URL you supply (SP onboarding "import IdP metadata"), you
control an XML doc it parses → XXE inside `<EntityDescriptor>`/
`<IDPSSODescriptor>` `<ds:X509Certificate>` elements.

## The compressed/deflated form — SAML binding variants

- HTTP-POST binding — `SAMLResponse` is base64 of the raw XML
- HTTP-Redirect binding — `SAMLRequest` is base64 of DEFLATE'd XML —
  deflate → inject entity → re-deflate → re-base64
- HTTP-Artifact binding — a token resolved via SOAP backchannel —
  SOAP XXE surface

## Falsifiers

- `DtdProcessing`-prohibited / disallowed DOCTYPE AND no RetrievalMethod
  / metadata-import surface → dead
