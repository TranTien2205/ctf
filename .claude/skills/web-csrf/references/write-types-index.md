# Write-types index — the endpoint → payload → oracle lookup

The reverse index: name the endpoint's write-shape, get the carrier,
the payload, and the readback oracle.

---

## Credential writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /change-email` | urlencoded form | `email=yours` | reset-flow or profile read |
| `POST /change-password` | urlencoded form | `new_password=x` | log in with it |
| `POST /login` | urlencoded or text/plain JSON | `u=me&p=x` | your session active |
| `POST /link-account` | urlencoded form | `provider=x&oauth_id=yours` | your OAuth login lands in victim's |

## Privilege writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /admin/role` | urlencoded form | `user=me&role=admin` | your account admin |
| `POST /grant` | urlencoded form | `permission=admin&user=me` | the grant read |
| `POST /approve` | urlencoded form | `request=1&approved=true` | the state flipped |
| `GET /admin/stats` | top-nav GET | — | the stats page read |

## Asset writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /transfer` | urlencoded form | `to=me&amount=999` | your balance/objects |
| `GET /transfer` | top-nav GET | `?to=me&amount=1` | same |
| `POST /send` | urlencoded form | `recipient=me&value=x` | your account |

## Object writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /post` | urlencoded form | `title=x&body=marker` | the post in a list |
| `POST /comment` | urlencoded form | `body=marker` | the comment rendered |
| `POST /bio` | urlencoded form | `bio=<xss/marker>` | the bio rendered |
| `POST /note` | urlencoded form | `text=marker` | the note present |
| `POST /update` (JSON) | text/plain form | `{"a":"x","i":"="}` | the field updated |
| `POST /upload` | multipart form | file+fields | the file reachable |

## Config writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /settings` | urlencoded form | `public=true` | the config's effect |
| `POST /config` | text/plain JSON | `{"debug":true}` | the config active |
| `POST /webhook` | urlencoded form | `url=https://yours` | the OOB hit |

## State writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /delete` | urlencoded form | `id=1` | the object 404s |
| `GET /delete` | top-nav GET | `?id=1` | same |
| `POST /confirm` | urlencoded form | `confirmed=true` | the state flipped |
| `POST /publish` | urlencoded form | `status=published` | the state flipped |

## Flag-path writes

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST /submit` | urlencoded form | `answer=FLAG{x}` | the submission on your account |
| `POST /answer` | urlencoded form | `flag=FLAG{x}` | same |
| `POST /assign` | text/plain JSON | `{"flag":"to-me"}` | the assignment read |

## Internal/loopback writes (the bot reaches)

| Endpoint | Carrier | Payload | Oracle |
|---|---|---|---|
| `POST http://127.0.0.1/x` | form nav text/plain | `{"a":"x","i":"="}` | the internal record |
| `POST http://app:8080/x` | form nav | fields | the internal service's output |
| `POST http://internal/x` | form nav | fields | same |

## The lookup → decision

```text
name the endpoint's write-shape → the carrier is the form-shape the
content-type allows → the payload is the field-set the endpoint's
bind accepts → the oracle is the readable state the write changes.
```
