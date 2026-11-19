# Username formats — the slot, the syntax, the normalization

## The live-slot hunt — which field is the username

```bash
for field in user username email login account name uid uname user_name \
             login_id handle member sub principal identifier phone mobile \
             login_hint subject; do
  printf '%-14s ' "$field"
  curl -s -o /dev/null -w '%{http_code}' -X POST -d "$field=$KNOWN&pass=x" "$BASE/login"
  printf '  '; curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "$field=$FAKE&pass=x" "$BASE/login"
done
```

The field that produces a differential (or a different status than the
missing-param `400`) is the live slot. A `400`/`422` on a wrong field
is a missing-param error, not an oracle.

## The format the app expects

```bash
for u in 'admin' 'admin@corp.com' 'corp\admin' 'admin.corp' 'a.admin' \
         '+15555551234' 'admin_x' 'admin-1'; do
  printf '%-18s ' "$u"; curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "user=$u&pass=x" "$BASE/login"
done
```

- a bare `admin` — the username slot
- `admin@corp.com` — the email slot (or an email-username)
- `corp\admin`/`admin.corp`/`a.admin` — a domain/suffix format
- `+1555...` — a phone-as-username
- a `404`/`400` on the wrong format is a FORMAT error — resolve it
  before reading the oracle; it does NOT mean the account is absent

## The normalization matrix

```bash
for u in 'admin' 'Admin' 'ADMIN' 'aDmin' ' admin' 'admin ' 'admin@x.c' 'ADMIN@X.C'; do
  printf '%-14s ' "$u"; curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "user=$u&pass=x" "$BASE/login"
done
```

- `admin`/`Admin`/`ADMIN` all hitting the same oracle → case-insensitive
  (record `normalization: case-fold`) — it does NOT equalize the oracle
- ` admin`/`admin ` → whitespace-trimmed
- `admin@x.c`/`ADMIN@X.C` → email case-folded
- a `Admin` that returns "no such user" where `admin` exists → case-
  SENSITIVE — the format note, not a fake-negative

## The unicode/homoglyph boundary

- `admin` vs `admin` (Cyrillic ``) — a lookalike hitting a DIFFERENT
  user is a homoglyph-confusion — a distinct finding (a spoofable
  username), not this class's oracle
- NFC/NFKC normalization — a `admin`/`admin` that folds to the same
  user is a normalization note

## The terminator/suffix boundary

- `admin\x00`/`admin ` — a null/space the app strips → same oracle
- `admin'`/`"admin"`/`admin;` — a quote/terminator that hits the SQL/
  parser → a different-class differential (`web-sqli`/`web-parser-diff`)
- `admin..`/`.admin`/`admin.` — a dot/suffix format

## The multi-field check — username vs email vs phone

A register/reset may check username OR email OR phone independently:

```bash
curl -d "user=AAA&email=SAME@x.c" "$BASE/register"   # vary user, hold email
curl -d "user=SAME&email=a@x.c" "$BASE/register"     # vary email, hold user
curl -d "user=AAA&phone=SAME" "$BASE/register"       # vary user, hold phone
```

An email-check enumerates EMAILS (a more valuable list — people reuse
emails); a username-check enumerates usernames; a phone-check enumerates
numbers. Record WHICH field is the oracle — the chain target differs.

## The format record

`slot: username` / `slot: email` / `slot: phone`; `normalization:
case-fold|exact`; `format: bare|email|domain|phone` — record the slot
and format; they determine which candidates and which form to run.
