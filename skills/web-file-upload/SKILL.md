---
name: web-file-upload
description: >
  File upload vulnerability detection and exploitation. Use when application
  allows file upload (avatars, documents, imports) with insufficient validation.
  Supports MIME type bypass, extension tricks, content-type bypass, polyglots,
  and archive-based attacks.
tags: [web, file-upload, webshell, mime-bypass]
environment: [ctf, lab, authorized-testing]
budget:
  max_attempts: 5
  stuck_threshold: 3
  time_hint: "30m"
  on_stuck: pivot
  stop_conditions:
    - "extension+MIME combos fail 5 times"
    - "upload OK but no execution path found"
    - "upload path discovery exhausted"
evidence_level: verified
---

# File Upload CTF Playbook

**Verified here.** Chains that prove this class: `htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce`, `htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce`.


## Scope & Safety
- Only upload to authorized targets
- Use benign test files first (e.g., text with unique marker)
- Document upload path and access URL
- Never deploy real backdoors without authorization

## First probe

Upload one benign file with a unique marker in both the filename and the
content, then retrieve it wherever the app serves uploads. Two facts come out
of a single probe: where the file lands and whether it is served back
verbatim. Then upload the same content with one rejected extension — the
layer that answers (client-side only, MIME sniffing, extension list, content
inspection) is the layer to attack.

**Falsifier** — the observation that closes this class: no upload becomes
retrievable through any path you can enumerate, and no server-side parser
(svg, archive, document importer) ever consumes the uploads.

## Discipline

- One upload surface, one probe round: marker upload, retrieval, then one
  rejected extension. Exploit only after both answers are known.
- An upload that succeeds but is never served is storage, not execution;
  pivot to what parses the stored file before trying more extensions.

## Detection Phase

### Initial Test
```bash
# Upload a basic test file
echo "UNIQUE_MARKER_TEST" > test.txt
# Upload via form, note the response

# Check if file is accessible
curl -s https://target.com/uploads/test.txt
```

### Identify Validation
1. Upload with no modifications → note response
2. Try different extension → `.php`, `.php5`, `.phtml`, `.pht`
3. Try different MIME type → `image/jpeg`, `text/plain`
4. Try different content → binary vs text
5. Check if rename/path traversal occurs

## Bypass Techniques Summary
- **Extension filter** → try alternate extensions, hidden chars, double ext → `references/extension-bypass.md`
- **MIME type check** → spoof Content-Type header → `references/mime-bypass.md`
- **Content/magic bytes** → prepend valid headers, exiftool, SVG, polyglots → `references/content-bypass.md`
- **Path traversal** → filename traversal, Zip Slip → `references/path-traversal.md`
- **Archive upload** → Zip Slip, XXE-in-DOCX, SVG XXE, CSV injection → `references/archive-attacks.md`
- **Webshell needed** → per-language templates → `references/webshell-templates.md`

## Common Upload Paths
```
/uploads/  /upload/  /files/  /media/  /images/
/attachments/  /temp/  /tmp/  /assets/uploads/
/public/uploads/  /static/uploads/
```

## Decision Tree
- Simple extension filter → `references/extension-bypass.md`
- MIME type validation only → `references/mime-bypass.md`
- Content validation (magic bytes) → `references/content-bypass.md`
- Path traversal possible → `references/path-traversal.md`
- Archive upload → `references/archive-attacks.md`
- Need webshell → `references/webshell-templates.md`

## Output Required
- Upload endpoint
- Validation mechanisms detected
- Bypass technique used
- Upload path and access URL
- File execution confirmed or denied

## References
- `references/extension-bypass.md` - Extension filter bypass
- `references/mime-bypass.md` - MIME/Content-Type bypass
- `references/content-bypass.md` - Content validation bypass
- `references/path-traversal.md` - Path traversal in upload
- `references/archive-attacks.md` - Archive-based attacks
- `references/webshell-templates.md` - Webshell templates per language

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
