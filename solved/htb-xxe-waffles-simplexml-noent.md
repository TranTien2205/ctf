# xxe ("WAFfles or Ice Cream") — SOLVED (self-solved)

- Platform: HackTheBox (web). Authors in page meta: makelaris, makelarisjr.
- Date: 2026-09-18
- Target supplied: `http://154.57.164.70:30598` (black-box; source then read through the bug)
- Flag: redacted; verified live in the `POST /api/order` response body
- Cost: 4 probes, ~3 minutes. No WAF bypass was needed — see below.

## Chain

1. `GET /` → 200, nginx, `X-Powered-By: PHP/7.4.15`, `<title>xxe</title>`.
   The page is a food-order form themed "WAFfles or Ice Cream".
2. `/assets/js/main.js` shows the form does **not** post itself. It fetches
   `POST /api/order` with `Content-Type: application/json` and a body of
   `{table_num, food}`. That is the only endpoint in the application.
3. The same endpoint with `Content-Type: application/xml` and an equivalent XML
   document also succeeds, and the reply interpolates the `food` value:
   `Your WAFfles order has been submitted successfully.` — a reflection sink.
4. Internal entity `<!ENTITY t "PROBE123">` in `food` comes back as
   `Your PROBE123 order ...`, so entities are substituted before interpolation.
5. `<!ENTITY t SYSTEM "file:///etc/passwd">` returns the file inline. Alpine
   (`/bin/ash`), and the app runs as `www` (uid 1000, home `/home/www`).
6. `file:///etc/nginx/nginx.conf` gives `root /www;`.
7. `php://filter/convert.base64-encode/resource=` is needed for the PHP sources,
   because raw PHP contains `<` and breaks the XML parse. `/www/index.php` shows
   the router and `POST /api/order -> OrderController@order`;
   `/www/controllers/OrderController.php` shows the actual sink:
   `simplexml_load_string($body, 'SimpleXMLElement', LIBXML_NOENT)`.
8. `file:///flag` returns the flag in the same reflected position.

## The WAF that is not there

The whole challenge is themed around a WAF ("WAFfles", "Both" disabled in the
dropdown) and the local matcher offered
`htb-red-island-2-json-unicode-waf-bypass-time-blind-sqli` on exactly that cue.
There is no WAF. `OrderController.php` contains no filtering of any kind: it
branches on `$_SERVER['HTTP_CONTENT_TYPE']` and hands the body straight to
`simplexml_load_string` with `LIBXML_NOENT`. The plainest possible payload —
`<!ENTITY t SYSTEM "file:///etc/passwd">`, no encoding tricks — worked on the
first attempt. The theme is a decoy.

## Reusable lessons

- **Read the JS before believing the form.** The visible `<form method='POST'>`
  posts nothing; `main.js` redirects it to a JSON API. The XML content type is
  invisible from the HTML and is the entire bug.
- **A content-type branch is an attack surface by itself.** When an endpoint
  accepts JSON, try the other parsers the framework has. Here `application/xml`
  reached a different, unguarded code path in the same handler.
- **Confirm entity substitution with an internal entity first.** One harmless
  `<!ENTITY t "PROBE123">` separates "entities are expanded" from "the file was
  unreadable", so a later empty response is unambiguous.
- **`php://filter/convert.base64-encode/resource=` is mandatory for source**, not
  optional: a raw PHP file read back into an XML document breaks the parse and
  looks like a failed read.
- **Do not let the theme pick the technique.** A WAF-themed name made a WAF-bypass
  chain the top local match; the bypass was never needed. Probe the plain payload
  before the clever one.
