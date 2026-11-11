#!/usr/bin/env python3
"""eml_parse.py -- .eml/.mbox inventory: headers, parts, attachments.

Phishing-analysis Sherlocks hand you an .eml or .mbox. This uses the
stdlib email/mailbox parsers: key headers (From/To/Subject/Date/
Message-ID, Received chain, auth results), every MIME part with its
content type and size, inline vs attachment, and body text. Extract
mode writes one attachment to stdout.

  python3 tools/forensics/eml_parse.py mail.eml
  python3 tools/forensics/eml_parse.py mail.mbox --mbox
  python3 tools/forensics/eml_parse.py mail.eml --attach 2
  python3 tools/forensics/eml_parse.py --selftest
"""
import argparse
import email
import email.policy
import json
import mailbox
import sys

HDRS = ["From", "To", "Cc", "Subject", "Date", "Message-ID",
        "Return-Path", "Reply-To", "Authentication-Results",
        "Received-SPF", "DKIM-Signature"]


def describe(msg):
    parts = []
    for i, p in enumerate(msg.walk()):
        if p.get_content_maintype() == "multipart":
            continue
        disp = p.get_content_disposition()
        payload = p.get_payload(decode=True) or b""
        e = {"index": i, "type": p.get_content_type(),
             "size": len(payload),
             "disposition": disp,
             "filename": p.get_filename()}
        if p.get_content_type() == "text/plain" and disp != \
                "attachment":
            e["text"] = payload.decode("utf-8", "replace")[:2000]
        parts.append(e)
    recvd = msg.get_all("Received", [])
    return {
        "headers": {h: str(msg.get(h)) for h in HDRS if msg.get(h)},
        "received_chain": [str(r) for r in recvd],
        "parts": parts,
        "attachments": [p for p in parts if p["filename"]],
    }


def attachment(msg, index):
    for i, p in enumerate(msg.walk()):
        if i == index and p.get_content_maintype() != "multipart":
            return p.get_payload(decode=True)
    return None


def _selftest():
    raw = (b"From: attacker@evil.example\r\n"
           b"To: v@corp.example\r\n"
           b"Subject: invoice\r\n"
           b"Message-ID: <x@y>\r\n"
           b"Received: from mx.evil by mx.corp\r\n"
           b"MIME-Version: 1.0\r\n"
           b"Content-Type: multipart/mixed; boundary=B\r\n\r\n"
           b"--B\r\nContent-Type: text/plain\r\n\r\n"
           b"see attached flag{phish_body}\r\n"
           b"--B\r\nContent-Type: application/octet-stream\r\n"
           b"Content-Disposition: attachment; filename=inv.bin\r\n"
           b"Content-Transfer-Encoding: base64\r\n\r\n"
           b"RkxBR3thdHRhY2htZW50fQ==\r\n"
           b"--B--\r\n")
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    d = describe(msg)
    assert d["headers"]["Subject"] == "invoice"
    assert "flag{phish_body}" in d["parts"][0]["text"]
    assert d["attachments"][0]["filename"] == "inv.bin"
    att = attachment(msg, 2)
    assert att == b"FLAG{attachment}", att
    print("eml_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="eml/mbox inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--mbox", action="store_true")
    ap.add_argument("--attach", type=int, metavar="INDEX")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    if a.mbox:
        box = mailbox.mbox(a.path)
        out = [describe(m) for m in box]
        print(json.dumps({"messages": len(out), "mails": out},
                         indent=1))
        return
    msg = email.message_from_bytes(
        open(a.path, "rb").read(), policy=email.policy.default)
    if a.attach is not None:
        blob = attachment(msg, a.attach)
        if blob is None:
            sys.exit("no such part")
        sys.stdout.buffer.write(blob)
        return
    print(json.dumps(describe(msg), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
