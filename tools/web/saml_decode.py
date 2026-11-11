#!/usr/bin/env python3
"""saml_decode.py -- decode a SAMLResponse/SAMLRequest blob.

SSO challenges carry base64 (optionally DEFLATE'd) XML in the
SAMLResponse / SAMLRequest params. This decodes both shapes and
surfaces the fields an attacker edits: Issuer, NameID, every
AttributeStatement attribute, Signature presence and Reference
URIs — the checklist for signature-removal, comment-injection
(XMLDSig truncated-name), and assertion-confusion tests.

  python3 tools/web/saml_decode.py resp.txt
  python3 tools/web/saml_decode.py --b64 'PD94bWwg...'
  python3 tools/web/saml_decode.py --selftest

Analysis only — it never signs and never sends. Re-encode the
edited XML yourself; resigning is a different class of problem.
"""
import argparse
import base64
import json
import re
import sys
import zlib


def decode_blob(raw):
    d = base64.b64decode(raw + "=" * (-len(raw) % 4))
    if d[:2] in (b"\x78\x9c", b"\x78\x01", b"\x78\xda"):
        d = zlib.decompress(d)
    elif d[:1] != b"<":
        try:
            d = zlib.decompress(d, -15)
        except zlib.error:
            pass
    return d


def analyse(xml):
    out = {"issuer": None, "nameid": None, "attributes": {},
           "signed": False, "references": [], "not_on_or_after": None}
    m = re.search(rb"<[a-zA-Z0-9:._-]*Issuer[^>]*>([^<]+)", xml)
    if m:
        out["issuer"] = m.group(1).decode("utf-8", "replace")
    m = re.search(rb"<[a-zA-Z0-9:._-]*NameID[^>]*>([^<]+)", xml)
    if m:
        out["nameid"] = m.group(1).decode("utf-8", "replace")
    out["signed"] = b"<" in xml and re.search(
        rb"<[a-zA-Z0-9:._-]*Signature[\s>]", xml) is not None
    out["references"] = [u.decode("utf-8", "replace") for u in
                         re.findall(rb"URI=\"#?([^\"]+)\"", xml)]
    m = re.search(rb"NotOnOrAfter=\"([^\"]+)\"", xml)
    if m:
        out["not_on_or_after"] = m.group(1).decode()
    for m in re.finditer(
            rb"Attribute[^>]*Name=\"([^\"]+)\"[^>]*>\s*"
            rb"<[a-zA-Z0-9:._-]*AttributeValue[^>]*>([^<]*)", xml):
        out["attributes"][m.group(1).decode("utf-8", "replace")] = \
            m.group(2).decode("utf-8", "replace")
    return out


def _selftest():
    xml = (b'<samlp:Response xmlns:samlp="u:s" '
           b'xmlns:saml="u:a"><saml:Issuer>idp.example</saml:Issuer>'
           b'<saml:Assertion><saml:Subject><saml:NameID>user1'
           b'</saml:NameID></saml:Subject>'
           b'<saml:AttributeStatement><saml:Attribute Name="role">'
           b'<saml:AttributeValue>user</saml:AttributeValue>'
           b'</saml:Attribute></saml:AttributeStatement>'
           b'</saml:Assertion></samlp:Response>')
    blob = base64.b64encode(xml).decode()
    x = decode_blob(blob)
    d = analyse(x)
    assert d["issuer"] == "idp.example" and d["nameid"] == "user1", d
    assert d["attributes"]["role"] == "user" and not d["signed"]
    xz = decode_blob(base64.b64encode(zlib.compress(xml)).decode())
    d2 = analyse(xz)
    assert d2["nameid"] == "user1"
    print("saml_decode selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="SAML blob decoder")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--b64")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    raw = a.b64 or (open(a.path).read().strip() if a.path else None)
    if raw is None:
        ap.error("path or --b64 required")
    try:
        xml = decode_blob(raw)
    except Exception as ex:
        sys.exit(f"decode failed: {ex}")
    d = analyse(xml)
    d["xml_len"] = len(xml)
    print(json.dumps(d, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
