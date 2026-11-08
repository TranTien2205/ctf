# DOM-Based XSS

## Common Sources (Attacker-Controlled Input)
```javascript
location.href
location.search
location.hash
location.pathname
document.URL
document.documentURI
document.referrer
window.name
document.cookie
localStorage / sessionStorage
postMessage data
```

## Common Sinks (Dangerous Execution Points)

### HTML Injection Sinks
```javascript
element.innerHTML = source
element.outerHTML = source
document.write(source)
document.writeln(source)
insertAdjacentHTML(position, source)
jQuery: $(x).html(source)
```

### JavaScript Execution Sinks
```javascript
eval(source)
setTimeout(source, 1000)      // if source is string
setInterval(source, 1000)     // if source is string
new Function(source)
element.setAttribute('onclick', source)
```

### URL Sinks
```javascript
location = source
location.href = source
location.assign(source)
location.replace(source)
window.open(source)
```

## Example Vulnerable Patterns

### location.hash → innerHTML
```javascript
// Vulnerable code:
document.getElementById('output').innerHTML = decodeURIComponent(location.hash.substring(1));

// Exploit URL:
https://target.com/page#<img src=x onerror=alert(1)>
```

### URL Parameter → document.write
```javascript
// Vulnerable code:
var name = new URLSearchParams(location.search).get('name');
document.write("Hello " + name);

// Exploit URL:
https://target.com/page?name=<script>alert(1)</script>
```

### postMessage Sink
```javascript
// Vulnerable code:
window.addEventListener('message', function(e) {
    document.getElementById('content').innerHTML = e.data;
});

// Exploit (from attacker page):
targetWindow.postMessage('<img src=x onerror=alert(1)>', '*');
```

## jQuery-Specific Sinks
```javascript
$(source)                    // If source starts with < treated as HTML
$.html(source)
$.append(source)
$.parseHTML(source)
$.globalEval(source)
```

## Testing Methodology
```
1. Search page source/JS files for sources (location, document.URL, etc.)
2. Trace data flow from source to sink
3. Check if sanitization/encoding happens in between
4. Craft payload matching the sink type (HTML vs JS vs URL context)
5. Use browser DevTools breakpoints on innerHTML/eval to trace
```

## Static Analysis Tools
```bash
# Search minified JS for dangerous sinks
grep -oE "\.innerHTML|document\.write|eval\(|\.html\(" bundle.js

# DOM XSS scanners
dom-xss-scanner
DOMPurify bypass testing (if sanitizer present)
```

## Browser DevTools Approach
```
1. Open Sources panel
2. Set DOM breakpoint on subtree modification (for innerHTML sinks)
3. Or search "eval" / "innerHTML" in Debugger search
4. Set XHR/fetch breakpoints to trace source values
```
