#!/usr/bin/env python3
"""cert_info.py -- X.509 certificate inventory: fields that carry the flag.

Cert handouts hide the answer in subject/issuer/SAN strings, in a
strength-on-purpose key (512-bit RSA), or in a date that answers a
question. This decodes PEM or DER through `cryptography` when present
(falling back to a bare ASN.1 subject/issuer/serial read otherwise),
then reports names, SANs, validity window, key kind + size, signature
algorithm and flag-format hits in any string field.

  python3 tools/cert_info.py cert.pem
  python3 tools/cert_info.py cert.der --der
  python3 tools/cert_info.py --selftest
"""
import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone


def _flag(s):
    return re.findall(r"[A-Za-z0-9_]+\{[^}]{3,}\}", s)


def _with_crypto(data, der):
    from cryptography import x509
    cert = x509.load_der_x509_certificate(data) if der else \
        x509.load_pem_x509_certificate(data)
    def names(n):
        return ", ".join("%s=%s" % (a.oid._name or a.oid.dotted_string,
                                    a.value) for a in n)
    sans = []
    try:
        ext = cert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        sans = [str(v) for v in ext.value]
    except x509.ExtensionNotFound:
        pass
    pub = cert.public_key()
    ktype = type(pub).__name__
    ksize = getattr(pub, "key_size", None)
    sig = cert.signature_hash_algorithm
    weak = []
    if ksize and "RSA" in ktype and ksize < 1024:
        weak.append("rsa key %d bits -- brute-forcable" % ksize)
    if sig and sig.name in ("md5", "sha1"):
        weak.append("%s signature -- collision-grade" % sig.name)
    texts = " ".join([names(cert.subject), names(cert.issuer)] + sans)
    return {"backend": "cryptography",
            "subject": names(cert.subject),
            "issuer": names(cert.issuer),
            "serial": "%x" % cert.serial_number,
            "not_before": cert.not_valid_before_utc.isoformat(),
            "not_after": cert.not_valid_after_utc.isoformat(),
            "expired": cert.not_valid_after_utc
            < datetime.now(timezone.utc),
            "sans": sans,
            "key": {"type": ktype, "bits": ksize},
            "sig_alg": sig.name if sig else None,
            "version": "v%d" % (cert.version.value + 1),
            "weak_notes": weak,
            "flag_strings": _flag(texts)}


def _bare(data):
    """PEM->DER strip, then a shallow ASN.1 walk for serial + both names."""
    m = re.search(br"-----BEGIN CERTIFICATE-----\s*([A-Za-z0-9+/=\s]+?)"
                  br"-----END CERTIFICATE-----", data)
    if m:
        data = base64.b64decode(re.sub(br"\s", b"", m.group(1)))
    # outer SEQUENCE -> TBSCertificate SEQUENCE; serial is int at [1]
    def tlv(b, i):
        ln = b[i + 1]
        if ln & 0x80:
            n, ln = ln & 0x7F, int.from_bytes(b[i + 2:i + 2 + (b[i + 1] & 0x7F)],
                                              "big")
            i += 2 + n
        else:
            i += 2
        return b[i:i + ln], i + ln, i - ln + (2 if ln < 0x80 else 0)
    try:
        body, _, _ = tlv(data, 0)                    # Certificate
        tbs, _, hdr = tlv(body, 0)                   # TBSCertificate
        i = 0
        if tbs[0] == 0xA0:                           # [0] version
            _, i, _ = tlv(tbs, 0)
        serial, i, _ = tlv(tbs, i)                   # serialNumber
        _alg, i, _ = tlv(tbs, i)                     # signature alg
        issuer, i, _ = tlv(tbs, i)                   # issuer Name
        _val, i, _ = tlv(tbs, i)                     # validity
        subject, i, _ = tlv(tbs, i)                  # subject Name
        def rdns(b):
            # each RDN is a SET of SEQUENCE(oid, value); pull every
            # PrintableString/UTF8/BMP-ish string inside
            out = []
            j = 0
            while j < len(b):
                rdn, j, _ = tlv(b, j)
                for m3 in re.finditer(b"[\x0c\x13\x16](.)([^\x00]{2,})",
                                      rdn):
                    out.append(m3.group(2).decode("utf-8", "replace"))
            return out
        sub, iss = rdns(subject), rdns(issuer)
        texts = " ".join(sub + iss)
        return {"backend": "bare-asn1 (cryptography absent)",
                "serial": serial.hex(),
                "issuer_strings": iss, "subject_strings": sub,
                "flag_strings": _flag(texts),
                "note": "SAN/key/signature fields need the "
                        "cryptography package"}
    except Exception as exc:
        return {"error": "asn1 walk failed: %s" % exc}


def _selftest():
    pem = (b"-----BEGIN CERTIFICATE-----\n"
           + base64.encodebytes(_mkcert()) + b"-----END CERTIFICATE-----")
    d = _with_crypto(pem, der=False)
    assert d["serial"] == "1e240"
    assert "flag{c3rt_inspector}" in d["subject"], d["subject"]
    assert d["flag_strings"], d
    print("cert_info selftest: ok")


def _mkcert():
    """Build a real self-signed cert via cryptography for the fixture."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    key = rsa.generate_private_key(65537, 2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,
                                         "flag{c3rt_inspector}")])
    c = (x509.CertificateBuilder()
         .subject_name(name).issuer_name(name)
         .public_key(key.public_key())
         .serial_number(0x1E240)
         .not_valid_before(datetime(2020, 1, 1))
         .not_valid_after(datetime(2040, 1, 1))
         .add_extension(x509.SubjectAlternativeName(
             [x509.DNSName("ctf.example")]), critical=False)
         .sign(key, hashes.SHA256()))
    return c.public_bytes(serialization.Encoding.DER)


def main():
    ap = argparse.ArgumentParser(description="X.509 certificate inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--der", action="store_true", help="input is raw DER")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("cert path required")
    data = open(a.path, "rb").read()
    try:
        print(json.dumps(_with_crypto(data, a.der or
                                      not data.startswith(b"-----")), indent=1))
    except ImportError:
        print(json.dumps(_bare(data), indent=1))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
