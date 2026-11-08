# SSTI Engine Detection

## Detection Flowchart

```
Send {{7*7}}
├── Returns 49 → Jinja2/Twig (Python/PHP)
│   └── Send {{7*'7'}}
│       ├── Returns 49 → Jinja2
│       └── Returns 7777777 → Twig
├── No match → Send ${7*7}
│   ├── Returns 49 → Freemarker/Velocity (Java)
│   │   └── Send ${"abc".length()}
│   │       ├── Returns 3 → Freemarker
│   │       └── Error → Velocity
├── No match → Send #{7*7}
│   └── Returns 49 → Thymeleaf (Java)
└── No match → Send <%= 7*7 %>
    └── Returns 49 → ERB (Ruby)
```

## Error Messages by Engine

| Engine | Error Pattern |
|--------|---------------|
| Jinja2 | `jinja2.exceptions.TemplateSyntaxError` |
| Twig | `Twig\Error\SyntaxError` |
| Freemarker | `freemarker.core.InvalidReferenceException` |
| Velocity | `org.apache.velocity.Template` |
| Mako | `mako.exceptions.TemplateSyntaxError` |
| Thymeleaf | `org.thymeleaf.exceptions.*` |
| ERB | `erb: syntax error` |

## Mathematical Tests

| Test | Jinja2 | Twig | Freemarker | Velocity |
|------|--------|------|------------|----------|
| `{{7*7}}` | 49 | 49 | - | - |
| `${7*7}` | - | - | 49 | 49 |
| `{{7*'7'}}` | 49 | 7777777 | - | - |

## Context Clues

### Framework Detection
```
Django → likely Jinja2
Flask → likely Jinja2
Laravel → likely Blade/Twig
Spring → likely Freemarker/Thymeleaf
Express → likely EJS/Pug/Nunjucks
```

### Response Headers
```
X-Powered-By: PHP → Twig possible
Server: Apache/Tomcat → Java possible
X-Generator: Django → Jinja2 possible
```
