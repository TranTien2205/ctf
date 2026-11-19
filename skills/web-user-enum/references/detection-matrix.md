# Detection matrix — observed signal → first hypothesis

| Observed | First hypothesis | First probe |
|---|---|---|
| `"no such user"` in an error | text oracle | 3-request diff |
| a uniform `"invalid credentials"` | timing/side oracle | timing baseline + envelope |
| a `?error=`/`?e=` redirect param | redirect oracle | `Location` diff |
| a `404` vs `401`/`200` | status oracle | `-w '%{http_code}'` |
| `{"error":"user_not_found"}` | JSON oracle | JSON diff |
| `{"available":false}`/`{"taken":true}` | direct oracle | `GET /check?u=` |
| `"username already registered"` | register oracle | `POST /register` |
| `"reset sent"` only for real | reset-send oracle | `POST /reset` + timing |
| a `Set-Cookie` on one arm | side oracle | `-sv` envelope diff |
| a slow `good` arm | timing oracle | median delta |
| a `423`/`429` on a real name | lockout oracle + throttle | bounded burst |
| a `X-Forwarded-For` resets `429` | throttle-bypass | spoofed header |
| every channel uniform | closed (per-form) | next form / record negative |

## The matrix-to-channel map

Every observed signal resolves to a channel — the channel is the
measurement (`channels.md`), the signal is the *hint* that the channel
may fire. A hint is not a finding; the channel measurement is.

## The coverage note

The matrix is the entry hint, not the pass — run the full per-form,
per-channel measurement (`workflow.md`) before closing.
