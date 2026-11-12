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
evidence_level: verified
---

# Deserialization CTF Playbook

**Verified here.** Chains that prove this class: `htb-dllama-pickle-cookie-auth-bypass-latex-verbatiminput`, `htb-py2-pickle-cookie-reduce-rce-rendered-output`.


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
before any gadget chain is attempted. For the Python path,
`tools/pickle_gen.py --marker TAG` builds the benign object whose
`PWNED-<tag>` appearance in the response is the confirm; `--cmd`/`--eval`
forms are for the already-confirmed sink. To read a captured blob rather
than build one: `python3 tools/pickle_dis.py blob.pkl` walks the opcodes
with `pickletools` — every `GLOBAL`/`STACK_GLOBAL` module.attr resolved,
each `REDUCE` counted, `data-only stream` vs `code-execution opcodes
present` — never unpickle to inspect. For PHP streams,
`python3 tools/php_ser_parse.py blob.ser` (or `--str 'O:8:"User":...'`)
decodes the `a:N:{...}` grammar to JSON and lists every serialized
class name — the object-injection surface to hunt in source. Java
streams too: `python3 tools/java_ser.py payload.ser` (or `--b64
rO0AB...`) walks the `aced 0005` TC_* tokens into a classdesc
inventory (names, serialVersionUIDs, fields) plus every TC_STRING,
and names classes on the known-gadget list when they appear —
analysis only, it never deserialises.

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
  (`tools/web/archive_gen.py phar --metadata '<serialized>'` mints a signed
  phar for the phar:// wrapper path without PHP on the box)
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

## Operational probe

Identify the format from the blob's own magic *before* touching any gadget:

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-deserialization \
  --url "$BASE/api/me" --header "Cookie: user=$BLOB" \
  --evidence-regex 'rO0AB|aced0005|^gAN|O:\d+:"|BAhJ' --evidence-kind class \
  --on-match confirms --on-miss inconclusive
```

Those anchors name Java, Python pickle, PHP and Ruby in that order. A blob that
merely base64-decodes to JSON is not deserialization.

**Falsifier:** the blob is signed with a key that is not leaked and not reachable.
Gadget work before the format is named is the usual way this class burns a budget.

Pipe the result straight into the write gate: `http_probe.py` already emits the
shape `tools/hooks.py post-probe` wants, so the excerpt is verbatim and a
transport failure is recorded as `transport`, which can never confirm.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
