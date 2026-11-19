# Per-check: state parameter — the CSRF binding

`state` is the cheapest falsifier to test and the most common bug. This
module names every check on the `state` parameter, what each proves, and
the falsifier that closes it.

## The check list

| Check | Probe | Confirmation | Falsifier |
|---|---|---|---|
| `state` not validated | callback with a random `state` | session issued | `400 state mismatch` |
| `state` not bound to session | callback with a `state` from a different session | session issued | `400 state mismatch` |
| `state` not single-use | same `state` twice | session issued both times | second `400` |
| `state` predictable | two flows, diff the `state`s | sequential or timestamp-derived | cryptographically random |
| `state` reflected | `state` in the callback page's HTML | a DOM sink | encoded or not reflected |
| `state` not cleared | `state` stored in session after use | still valid on a second callback | cleared after exchange |

## The baseline probe

```bash
# capture the state the app issued for this session
STATE=$(curl -si -b "$JAR" -c "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+')
echo "issued: $STATE"

# replay the callback with a DIFFERENT state
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=DIFFERENT"
```

## The cross-session test

```bash
# session 1 stores state S1
curl -si -b "$JAR1" -c "$JAR1" "$BASE/login" | grep -oP 'state=\K[^&\s]+' > s1.txt

# session 2 stores state S2 — a different session
curl -si -b "$JAR2" -c "$JAR2" "$BASE/login" | grep -oP 'state=\K[^&\s]+' > s2.txt

# replay S1 against session 2's callback
curl -i -b "$JAR2" "$BASE/callback?code=ABC&state=$(cat s1.txt)"
# if session 2 establishes a session, S1 was accepted by a session that never stored it
```

## The predictability test

```bash
# capture two states
S1=$(curl -si -b "$JAR" -c "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+')
S2=$(curl -si -b "$JAR" -c "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+')
echo "S1: $S1"
echo "S2: $S2"
# diff — a fixed offset, a timestamp, or a counter is predictable
```

## The reflected-state test

```bash
# inject HTML into state
curl -i -b "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+' > s.txt
# modify the authorize URL to carry an injection payload in state
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=<script>alert(1)</script>"
# check whether the callback page renders it unencoded
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=<script>alert(1)</script>" | grep "<script>"
```

## The falsifier

`state` is a cryptographically random value stored in the session cookie
before the redirect, the callback rejects any state that does not match the
session's stored value, and the stored value is cleared after use. When this
holds, the CSRF shape is dead — record the falsifier and move to redirect_uri.

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict falsifier \
  --request "callback with mismatched state" \
  --result "400 Bad Request: state mismatch — state is bound to session; the CSRF shape is dead"
```
