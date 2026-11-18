# Key Hunt — where the signing secret actually lives

## The rule — most "deserialization" CTF is really key management

The blob is signed; the class dies only when the key is unreachable. The
budget order is: find the key → forge → gadget. Don't craft the POP chain
until you know whether you can sign it.

## The per-framework key file

| Framework | The file | The field |
|---|---|---|
| Laravel | `.env` | `APP_KEY=base64:...` |
| Symfony | `.env` / `parameters.yml` | `APP_SECRET` / `secret` |
| Django | `settings.py` | `SECRET_KEY = '...'` |
| Flask | `app.py` / `config.py` / `.env` | `SECRET_KEY` / `app.secret_key` |
| Rails | `config/secrets.yml` / `credentials.yml.enc`+`master.key` | `secret_key_base` |
| ASP.NET | `web.config` / `machine.config` | `machineKey validationKey decryptionKey` |
| Node | `.env` / `config.js` / `session` mw | `secret`, `resave`, `saveUninitialized` |
| JWT | `config`/`env`/`jwks`/`cert.pem` | `secret`, `private.pem`, `JWKS` |
| WordPress | `wp-config.php` | `AUTH_KEY`, `SECURE_AUTH_KEY`, `LOGGED_IN_KEY`, `NONCE_KEY` |
| generic | `.env`, `config.*`, `secrets.*`, `*.pem`, `*.key`, `*.crt` | |

## The error-page oracle — the free key leak

```
DEBUG=True Django crash   → settings dump incl SECRET_KEY
Flask debugger (PIN-less) → interactive console → env read
Laravel Ignition page     → APP_KEY sometimes in context dump
Rails development error   → filtered params show key names
ASP.NET YSOD              → web.config lines incl machineKey
FastAPI / uvicorn debug   → env echo
```

The error page is the cheapest key source — trigger a crash before source-
reviewing. A 500 body with `SECRET_KEY` inside is the class-confirm.

## The .env / config leak paths

- `GET /.env` — an exposed `.env` (web-info-disclosure overlap)
- `GET /config.json` / `/config.yml` / `/settings.json`
- `GET /.git/config` → then `git_dumper` → full source incl secrets
- `GET /backup.tar`/`/src.zip`/`/app.tar.gz` — the handout itself
- `phpinfo()` page → env vars incl `APP_KEY`, `SECRET_KEY`
- `actuator/env` (Spring) → env dump incl secrets
- `/_debug/` `/debug/` `/server-status` → env/config echo

## The default-key dictionary — Blacklist3r family

When no key leaks, try the published defaults:

- **ASP.NET machineKey** — Blacklist3r list of IIS/shared-hosting defaults
- **Rails `secret_key_base`** — the literal `"secret"`, per-app generated
  default in old Rails, the `development`/`test` env keys
- **Flask `SECRET_KEY`** — `'dev'`, `'secret'`, `'changeme'`, `'supersecret'`,
  `'development'`, the app's name
- **Django `SECRET_KEY`** — `'django-insecure-*'` prefix keys are the
  *generated* development keys — a real key but sometimes committed
- **Laravel `APP_KEY`** — `base64:AAAAAAAA...` pattern, old defaults
- **JWT secrets** — `secret`, `password`, `123456`, `key`, the app's name

```bash
# JWT weak-secret brute-force — session_dissect recovers the HMAC key offline
python3 tools/web/session_dissect.py --token "$T" --wordlist /path/to/words
hashcat -m 16500 -a 0 jwt.txt rockyou.txt
```

## The crypto-oracle key-recovery paths

- **JWT `kid` path traversal** — `kid:"../../dev/null"` or `kid:"|id"` →
  the verifier reads a file/SQLi → empty/known key
- **`jku`/`x5u`** — verifier fetches YOUR JWKS → sign with your own key
- **`alg=none`** — verifier accepts it → no key
- **RS256→HS256 confusion** — sign with the public key as HMAC secret
- **the padding oracle** on AES-CBC cookies — decrypt without the key

## The key-derivation trap — `secret_key_base` vs derived keys

Rails `secret_key_base` is the ROOT — per-cookie keys are derived
(`PBKDF2`/`HMAC` derivations). `secret_token` (Rails 3) vs `secret_key_base`
(Rails 4+) — different fields, different derivation. The `credentials.yml.enc`
needs `master.key` to decrypt → then `secret_key_base` inside.

## The "key is in the challenge description" CTF tell

CTF handouts often put the key in the *source they give you* — `secrets.yml`,
`.env.example`, `config.py` in the zip. A deserialization challenge that
ships source is almost always shipping the key — grep the handout first.

## The non-cookie signed channels

- **`X-Signature`/`X-Sig` header** on an API body
- **a `sig`/`mac`/`hmac` field inside JSON**
- **`itsdangerous`/`Signer` blobs** in params beyond cookies
- **a `MessageVerifier`-signed value in a param**
- **a `ViewState`/`__EVENTVALIDATION`** — machineKey

## The falsifier — the key is truly unreachable

- env/secret-manager only, never reflected in source, errors, or any other
  challenge primitive
- `alg=none`/`kid`/`jku`/`x5u`/confusion all verified blocked
- no `.env`/`config`/`jwks`/backup/source leak exists
- no default-key hit
- no padding-oracle/decrypt oracle on the channel

THEN the class is closed *for that channel* — pivot to a second-order sink
(the store-write path doesn't sign) or report the signature honestly.

## Output to record

- The key + where it came from (file path, error page, default list, brute)
- Or which header-attack bypassed verification
- The forge recipe (serializer + key + format)
