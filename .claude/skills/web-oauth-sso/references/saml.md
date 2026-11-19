# SAML — the XML assertion attack surface

SAML (Security Assertion Markup Language) is the XML-based SSO shape: the IdP
returns a `SAMLResponse` parameter containing a base64'd (optionally
DEFLATE-compressed) XML assertion. The application decodes the XML, verifies
the signature, and establishes a session from the `NameID` and attributes.

## The decode step

```bash
python3 tools/web/saml_decode.py resp.txt
```

Decodes the base64 (and DEFLATE if present), pretty-prints the XML, and lists:
- `Issuer` — who issued the assertion
- `NameID` — the identity the assertion claims
- `Attribute` entries — roles, groups, emails the app reads
- whether the assertion is signed — the signature block is the trust anchor

## The attack shapes, cheapest first

| Shape | Mechanism |
|---|---|
| signature removal | delete the `<ds:Signature>` block; some apps skip verification when the element is absent |
| signature stripping | keep the element but empty the `SignatureValue` — the parser may verify a null signature |
| comment injection | `<NameID>user<!-- comment -->@domain</NameID>` — the parser reads `user`, the verifier reads `user@domain` |
| attribute edit | change `<AttributeValue>` for a role or email — the signature covers the XML, but the app may not verify it covers the right part |
| algorithm confusion | the signature declares RSA-SHA256 but the verifier accepts `none` or HMAC with the public key |
| XSW — XML signature wrapping | duplicate the assertion: a signed benign copy for the verifier, an unsigned malicious copy for the app; namespace or position tricks send each to the right consumer |
| expired / not-yet-valid | the `NotBefore`/`NotOnOrAfter` conditions are ignored — replay an old captured assertion |
| missing conditions | no `AudienceRestriction`, so an assertion minted for one app works on another |

## The probe chain

```bash
# 1. decode the captured SAMLResponse
python3 tools/web/saml_decode.py resp.txt

# 2. signature removal — strip the whole Signature block, re-encode
python3 -c "import base64,zlib; r=open('resp.txt').read().strip(); x=base64.b64decode(r); x=zlib.decompress(x,-15); x=x.replace(b'<ds:Signature xmlns:ds=\"http://www.w3.org/2000/09/xmldsig#\">...</ds:Signature>',b''); print(base64.b64encode(zlib.compress(x)[2:-4]).decode())" > resp_nosig.txt

# 3. comment injection — split the NameID
python3 -c "x=open('resp.xml').read(); x=x.replace('user@domain','user<!-- -->@domain'); print(x)" > resp_comment.xml
```

## XSW — the signature-wrapping family

The app reads one assertion; the verifier reads another. Eight named shapes:

1. **XSW1** — the assertion is duplicated; the first (signed) satisfies the verifier, the second (unsigned, malicious) is what the app parses. Uses the same `ID` or namespace tricks.
2. **XSW2** — the malicious assertion is nested inside the signature's `<ds:Object>`.
3. **XSW3** — the assertion is moved to a sibling position; the verifier follows the `Reference` URI to the benign copy.
4. **XSW4** — the signature is duplicated; one verifies the benign assertion, the app reads the malicious one.
5. **XSW5** — the assertion and signature are both moved to `<ds:Object>` or an extension point.
6. **XSW6** — the assertion is moved to `<ds:Object>` inside `<ds:Signature>`; the verifier follows the reference.
7. **XSW7** — a `<Extensions>` block carries the malicious assertion.
8. **XSW8** — a `<ds:Object>` or `<SignatureProperty>` carries it.

Test each by capturing a valid assertion, applying the wrapping shape,
re-encoding, and replaying. The app either accepts the unsigned malicious
copy (a finding) or rejects the malformed XML (a negative).

## Falsifier

The assertion is signed, the signature is verified against the IdP's public key
with an allowlisted algorithm (not `none`, not HMAC), the `NameID` and
attributes are read from the same assertion that was verified (no wrapping
surface), and the `NotOnOrAfter` + `AudienceRestriction` conditions are
enforced. When this holds, move to the OAuth flow or the account-linking
surface.
