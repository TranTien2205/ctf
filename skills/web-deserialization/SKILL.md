---
name: web-deserialization
description: >
  Deserialization vulnerability detection and exploitation. Use when application
  processes serialized objects (cookies, parameters, API data) and trust them
  without validation. Supports PHP, Java, Python, .NET, Ruby deserialization.
tags: [web, deserialization, rce, php, java, python, dotnet]
environment: [ctf, lab, authorized-testing]
budget:
  max_attempts: 4
  stuck_threshold: 3
  time_hint: "40m"
  on_stuck: pivot
  stop_conditions:
    - "gadget chain fails 3 times"
    - "no public gadget for target version"
    - "phpggc/ysoserial payload errors twice"
evidence_level: catalogue
---

# Deserialization CTF Playbook

**Catalogue class.** This toolkit has never solved one; the content below is
standard published knowledge, not local experience.


## Scope & Safety
- Only test against authorized targets
- Deserialization exploits can cause unintended RCE
- Use non-destructive payloads first

## First probe

Submit a deliberately corrupted serialized object — flip one byte or truncate
the tail — and compare the response with a well-formed one. An application
that unserialises untrusted input almost always answers malformed input with
a parser stack trace, a distinct error, or a timing difference. That single
non-destructive probe confirms the object is actually being deserialised
before any gadget chain is attempted.

**Falsifier** — the observation that closes this class: malformed objects are
rejected with the same response and the same timing as well-formed ones, and
no consumer of the serialized value can be found in source.

## Discipline

- Confirm the deserialisation happens (corrupted-object probe) before
  touching a gadget chain; a gadget that errors proves nothing about the sink.
- One format per round: identify the serialisation format from the magic
  bytes first (PHP `O:`, Java `aced0005`, Python pickle, .NET `AAEAAAD`),
  then read only that format's references.
- Document all findings

## Detection Phase

### Identify Serialized Data
```bash
# Look for serialized data patterns

# PHP: O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";}
# Java: rO0AB (base64) or aced0005 (hex)
# Python: gANj... (base64 pickle)
# .NET: AAEAAAD... (base64)
# Ruby: BAhJ... (base64)
```

### Cookie Inspection
```bash
# Decode cookies
echo -n 'COOKIE_VALUE' | base64 -d

# Check for serialized objects in:
# - Session cookies
# - Authentication tokens
# - User preference cookies
# - Custom headers
```

### Parameter Inspection
```bash
# Check POST bodies for serialized data
# Check URL parameters
# Check hidden form fields
# Check API request/response bodies
```

## Language-Specific Exploitation
- PHP: `references/php-deser.md` — phpggc, POP chains, magic methods
- Java: `references/java-deser.md` — ysoserial, JNDI injection
- Python: `references/python-deser.md` — pickle RCE, RestrictedPython bypass
- .NET: `references/dotnet-deser.md` — ysoserial.net, ViewState, JSON.NET
- Ruby: `references/ruby-deser.md` — Marshal/YAML gadgets, Rails chains

## Decision Tree
- PHP serialized data → `references/php-deser.md`
- Java serialized data → `references/java-deser.md`
- Python pickle → `references/python-deser.md`
- .NET BinaryFormatter → `references/dotnet-deser.md`
- Ruby Marshal → `references/ruby-deser.md`
- Unknown serialization → `references/detection.md`

## Output Required
- Serialization format and library
- Source of serialized data (cookie/param/header)
- Decoded object structure
- Gadget chain used
- RCE or impact confirmed

## References
- `references/php-deser.md` - PHP deserialization techniques
- `references/java-deser.md` - Java deserialization & JNDI
- `references/python-deser.md` - Python pickle attacks
- `references/dotnet-deser.md` - .NET deserialization
- `references/ruby-deser.md` - Ruby deserialization
- `references/detection.md` - Serialization detection methods

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
