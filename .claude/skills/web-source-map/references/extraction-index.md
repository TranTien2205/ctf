# Extraction index — every grep grammar in one place

## Endpoints

```bash
grep -oE '"/[A-Za-z0-9_./?=&{}:%@!$~+-]+"' b.js | tr -d '"' | sort -u
grep -oE '`/[A-Za-z0-9_./?=&{}:$-]+`' b.js | tr -d '`' | sort -u
grep -oE '"/(api|v[0-9]+|internal|admin|graphql|auth|user|file|upload|export|debug)[^"]*"' b.js | sort -u
grep -oE '(fetch|axios\.[a-z]+|\.ajax|\.get|\.post|\.put|\.delete|\.patch|http)\s*\(\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
grep -oE 'https?://[A-Za-z0-9._/?=&:%-]+' b.js | sort -u
```

## Params

```bash
grep -oE '[{,]\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*:' b.js | sort -u
grep -oE '(append|set|get|delete)\s*\(\s*["'"'"'][a-zA-Z_$]+' b.js | sort -u
grep -oE '[?&][a-zA-Z_$]+=' b.js | sort -u
grep -oE '\$\{[a-zA-Z_$][a-zA-Z0-9_$.]*\}' b.js | sort -u
grep -oE '(body|data|params|payload)\s*:\s*\{[^{}]{10,}' b.js | head -30
```

## Routes

```bash
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
grep -oE '(component|element|lazy|import|loadChildren)\s*:\s*[A-Za-z_$.(]+' b.js | sort -u
grep -oE '(routes|ROUTES|Paths)\s*[:=]\s*\[[^\]]{20,}' b.js
grep -oE 'import\(\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
```

## Secrets

```bash
grep -oE 'eyJ[\w-]+\.[\w-]+\.[\w-]+' b.js
grep -oE '(AKIA|ASIA)[0-9A-Z]{16}' b.js
grep -oE 'AIza[0-9A-Za-z_-]{35}' b.js
grep -oE '(ghp|gho|ghs|github_pat_|glpat-)[0-9A-Za-z_-]{20,}' b.js
grep -oE 'xox[baprs]-[0-9A-Za-z-]{10,}' b.js
grep -oE '(sk|pk|rk)_(live|test)_[0-9A-Za-z]+' b.js
grep -oE '-----BEGIN [A-Z ]+PRIVATE KEY-----' b.js
grep -oE '(api[_-]?key|secret|token|password|client_secret|auth)["'"'"'\s:=]+["'"'"'][A-Za-z0-9_./+@=-]{6,}' b.js
grep -oE '(postgres|mysql|mongodb|redis|amqp)://[^"'"'"']+' b.js
```

## Config / env / flags

```bash
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE|GATSBY|NUXT)_[A-Z_]+' b.js | sort -u
grep -oE 'process\.env\.[A-Z_a-z]+' b.js | sort -u
grep -oE 'import\.meta\.env\.[A-Z_]+' b.js | sort -u
grep -oE '(feature|flags|config|settings|debug|env)\.[a-zA-Z_.]+' b.js | sort -u
grep -oE 'window\.__[A-Z_]+__\s*=\s*[^;]+' b.js
grep -oE '(isAdmin|is_admin|role|admin|internal|beta|canary)\s*[:=]' b.js | sort -u
```

## Auth surface

```bash
grep -oE '(localStorage|sessionStorage)\.[gs]etItem\([^)]*\)' b.js | sort -u
grep -oE '(Authorization|Bearer|X-[A-Za-z-]*Token|api[_-]?key)["'"'"'\s:=]+' b.js | sort -u
grep -oE 'document\.cookie' b.js
grep -oE '(jwt|sign|verify|secret|token)\s*[:=(]' b.js | sort -u
```

## Flag + comments (recovered source)

```bash
grep -rnoE '(flag|ctf)\{[^}]*\}' recovered/
grep -rniE '//\s*(TODO|FIXME|HACK|secret|password|key|flag|admin|internal|debug|remove|hardcode)' recovered/
grep -rniE 'console\.(log|debug|warn)\([^)]*(key|token|secret|pass|flag)' recovered/
```

## Sinks (recovered/beautified source)

```bash
grep -rniE 'eval|new Function|innerHTML|dangerouslySetInnerHTML|document\.write|deserialize|pickle|exec|spawn|child_process|subprocess|readFile|file_get_contents|render_template|__proto__|Object\.assign|merge\(|fetch\(|axios' recovered/ pretty.js
```

## GraphQL

```bash
grep -oE '"/?(graphql|gql|query)"' b.js | sort -u
grep -oE '(query|mutation|subscription)\s+[A-Za-z_]+' b.js | sort -u
grep -oE 'fragment\s+[A-Za-z_]+\s+on\s+[A-Za-z_]+' b.js | sort -u
```

## Obfuscation fallbacks

```bash
strings b.js | grep -oE '/[a-z0-9_./-]+|https?://\S+|flag\{[^}]*\}|[A-Za-z0-9+/=]{20,}' | sort -u
grep -oE 'atob\(["'"'"'][A-Za-z0-9+/=]+' b.js
grep -oE "(\\\\x[0-9a-fA-F]{2}|\\\\u[0-9a-fA-F]{4}){4,}" b.js
```
