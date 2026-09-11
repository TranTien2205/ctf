# Session Token Analysis

## Entropy Assessment
```bash
# Collect multiple session tokens (e.g. re-login several times)
# Compare length, character set, and structure

# Quick entropy estimate
python3 -c "
import math
from collections import Counter
token = 'PASTE_TOKEN_HERE'
counts = Counter(token)
length = len(token)
entropy = -sum((c/length) * math.log2(c/length) for c in counts.values())
print(f'Shannon entropy per char: {entropy:.2f} bits')
print(f'Total estimated entropy: {entropy*length:.2f} bits')
"
```
Tokens with low character diversity or visible patterns (timestamps,
sequential counters, base64 of predictable data) are weak.

## Predictability Testing
```
[ ] Generate N tokens in sequence (re-login repeatedly) and diff them
[ ] Check if token embeds timestamp (convert suspect segments from hex/
    decimal to Unix time and compare to request time)
[ ] Check if token is base64/hex of a simple counter or username+timestamp
[ ] If pattern found, attempt to predict/forge a valid token for another
    session ID space
```

## Session Fixation
```
[ ] Note session ID before login (as anonymous user)
[ ] Log in
[ ] Check if session ID changes after authentication
      - If unchanged → session fixation vulnerability (attacker can set
        victim's session ID pre-auth, then hijack post-auth)
```
Test:
```bash
# Get pre-auth session
curl -c cookies.txt https://target.com/
cat cookies.txt   # note session value

# Log in using same cookie jar
curl -b cookies.txt -c cookies.txt -d "user=victim&pass=pass" https://target.com/login
cat cookies.txt   # compare session value - did it change?
```

## Cookie Flag Review
```bash
curl -sI https://target.com/login | grep -i set-cookie
```
```
Missing HttpOnly  → session token readable via JS (XSS impact amplified)
Missing Secure    → token can be sent over plain HTTP if downgrade possible
Missing SameSite  → CSRF risk increased
SameSite=None without Secure → rejected by modern browsers, but check anyway
```

## Logout Behavior
```bash
# Capture session token before logout
# Log out
# Replay the OLD token against an authenticated endpoint
curl -H "Cookie: session=<old_token>" https://target.com/account
# If it still works → server-side session not invalidated on logout
```

## Concurrent Session Handling
```
[ ] Does logging in from a second device invalidate the first session?
[ ] Is there a "view active sessions" / "log out all devices" feature?
[ ] Can a stolen token be used indefinitely, or is there device/IP binding?
```

## Cross-Site Request Forgery (Related)
```
[ ] Is there a CSRF token on state-changing requests?
[ ] Is the CSRF token tied to the session, or is it static/predictable?
[ ] Does SameSite cookie policy provide sufficient CSRF protection already?
```
