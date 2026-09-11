---
name: web-idor
description: >
  Insecure Direct Object Reference. Use when the app exposes object IDs
  (sequential/UUID) in URL, API, body, or hidden fields and may not check
  ownership. Reference card — pull references/ for enumeration/UUID depth.
tags: [web, idor, access-control, authorization, broken-auth]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "no privilege delta between roles"
    - "ID sweep >200, no pattern, no new signal"
---

# IDOR — Reference Card

## Recognize
ID đoán được ở: `?id= /api/users/1 /orders/123 file=report_1.pdf {"user_id":1}` hoặc hidden
`<input name=account_id value=1001>`. Nghi IDOR khi resource gắn user mà không check ownership.

## Confirm (cần 2 context)
1. Login user A → ghi lại ID resource của A.
2. Login user B (hoặc bỏ session) → truy cập ID của A. Đọc/ghi được = IDOR.
3. Sequential: `±1` id. UUID: thu thập id trong response; v1 (timestamp) → đoán được → `references/uuid-analysis.md`.

## Vectors cần thử
- **API/GraphQL**: `GET /api/v1/orders/1002`; `{"query":"{user(id:2){email}}"}`.
- **File path**: `download?file=invoice_002.pdf` (+ combine path traversal `../config/db.yml`).
- **JWT/cookie claim**: đổi `user_id`/`role` trong token.
- **Mass assignment**: thêm field `{"user_id":2,"role":"admin"}` vào update.
- **Bypass filter**: đổi method (GET/PUT/DELETE), đổi Content-Type (json↔form), header
  `X-Original-URL: /admin`, `X-Forwarded-For: 127.0.0.1`.

## Route to depth (references/)
sequential → `sequential-enumeration.md` · UUID → `uuid-analysis.md` · API → `api-idor.md` ·
file → `file-idor.md` · quét hàng loạt → `enumeration.md`.

## Discipline (../LOOP_DISCIPLINE.md)
- Phải test bằng 2 danh tính (A tạo, B truy cập) mới chứng minh được IDOR — 1 tài khoản không đủ.
- Không có privilege delta giữa các role → có thể không phải IDOR, đổi hướng.
