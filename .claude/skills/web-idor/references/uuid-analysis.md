# IDOR - UUID Analysis

## UUID Version Identification
```
UUID format: xxxxxxxx-xxxx-Vxxx-Nxxx-xxxxxxxxxxxx
V = version digit (position 15, 13th hex char after removing dashes)
N = variant bits
```

## UUID v1 (Time-Based - PREDICTABLE)
```
Structure: time_low-time_mid-time_hi_and_version-clock_seq-node
Contains: timestamp + MAC address (node)

# If you know approximate creation time and MAC/node ID pattern,
# you can predict/brute-force other UUID v1 values

# Python: decode timestamp from UUID v1
import uuid
u = uuid.UUID('550e8400-e29b-11d4-a716-446655440000')
print(u.time)  # 100-nanosecond intervals since UUID epoch (1582-10-15)
```

### UUID v1 Brute Force (if node/MAC is fixed for the server)
```python
import uuid
import time

# If you know the node (MAC-derived) and approximate timestamp,
# enumerate nearby timestamps to guess valid UUIDs
node = 0x446655440000  # extracted from a known UUID
for offset in range(-1000, 1000):
    fake_time = int(time.time() * 1e7) + offset
    # Construct UUID v1 manually with known node and clock_seq
```

## UUID v4 (Random - THEORETICALLY SAFE, check RNG quality)
```
Fully random except version/variant bits (122 bits of randomness)
Not brute-forceable if properly generated (2^122 space)

# BUT: check if the underlying RNG is weak/predictable
# (e.g., Math.random() in old JS instead of crypto.randomUUID())
```

## UUID v3/v5 (Namespace + Name Hash - DETERMINISTIC)
```
UUID = MD5(v3) or SHA1(v5) of (namespace + name)

# If namespace is known/default and name is guessable (e.g., username, email, sequential ID)
# You can COMPUTE the UUID directly without brute force

import uuid
namespace = uuid.NAMESPACE_DNS  # or custom namespace UUID
predicted = uuid.uuid5(namespace, "victim@example.com")
print(predicted)
```

### Common Namespace UUIDs to Test
```
NAMESPACE_DNS  = 6ba7b810-9dad-11d1-80b4-00c04fd430c8
NAMESPACE_URL  = 6ba7b811-9dad-11d1-80b4-00c04fd430c8
NAMESPACE_OID  = 6ba7b812-9dad-11d1-80b4-00c04fd430c8
NAMESPACE_X500 = 6ba7b814-9dad-11d1-80b4-00c04fd430c8
```

## Identifying UUID Version from a Sample
```python
import uuid
u = uuid.UUID('a-sample-uuid-value-here')
print(u.version)  # 1, 3, 4, or 5
```

## Testing Checklist
```
1. Collect several UUIDs from the app (your own account, test accounts, public data)
2. Check version nibble - if 1 (time-based) or 3/5 (namespace-based), NOT safe from prediction
3. For v1: attempt timestamp-based enumeration around known creation windows
4. For v3/v5: try common namespaces + guessable names (email, username, sequential ID)
5. For v4: check RNG source in client-side JS if UUIDs are generated client-side
```

## Tools
```python
# Quick UUID version checker script
import sys, uuid
for u in sys.argv[1:]:
    parsed = uuid.UUID(u)
    print(f"{u}: version={parsed.version}")
```
