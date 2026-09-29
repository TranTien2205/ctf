#!/usr/bin/env python3
"""Generate knowledge/bug-classes.json — the bug-class taxonomy.

One entry per bug class. Every field is either observed in this toolkit's own
solved chains, or is standard published knowledge about that class. The
`evidence_level` field keeps the difference honest:

  verified   this toolkit has at least one verified chain card for the class;
             `verified_by` names them.
  catalogue  the class is real and standard, but nothing here has solved one.
             The skill exists so the router has a destination and so the first
             solve has somewhere to land. Treat its content as a starting point,
             not as proven local knowledge.

`observation_signals` match black-box evidence: banners, headers, response text,
challenge wording. `source_signals` match white-box evidence: code.
Both are Python regexes, matched case-insensitively.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "knowledge", "bug-classes.json")

CLASSES = [
    # ---------------------------------------------------------------- injection
    {
        "id": "web-sqli", "name": "SQL injection", "skill_dir": "web-sqli",
        "evidence_level": "verified",
        "verified_by": ["htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli",
                        "htb-red-island-2-json-unicode-waf-bypass-time-blind-sqli"],
        "observation_signals": [r"\bsql\b", r"sqlite|mysql|mariadb|postgres|mssql|oracle",
                                r"\bselect\b[^\n]{0,80}\bfrom\b[^\n]{0,60}\bwhere\b",
                                r"vsprintf|sprintf[^\n]{0,40}(?:select|insert|update)",
                                r"syntax error|sqlstate|you have an error in your sql",
                                r"order\s*by|union\s+select", r"boolean.{0,12}(?:delta|difference)",
                                r"time.?based|sleep\(|pg_sleep|waitfor delay",
                                r"\bsingle quote\b|\bapostrophe\b",
                                r"database error|db error|query (?:error|failed)"],
        "source_signals": [r"SELECT[\s\S]{0,160}(?:\+|%|\.format|\$\{|f[\"'])",
                           # .NET: raw-SQL APIs handed a C# interpolated string.
                           # Nexus Void ranked no SQL class at all from source
                           # because every existing pattern was written for
                           # python, node or php quoting.
                           r"(?:FromSqlRaw|ExecuteSqlRaw|ExecuteSqlInterpolated|CommandText\s*=|new\s+SqlCommand)[^\n]{0,80}\$\"",
                           r"\$\"[^\"\n]{0,100}\b(?:SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b[^\"\n]{0,200}\{",
                           # The python twin of the line above, and the reason
                           # No Threshold ranked SQL injection third: an f-string
                           # prefix comes BEFORE the verb, so a pattern looking
                           # for a quote AFTER SELECT never sees it.
                           r"f\"[^\"\n]{0,60}\b(?:SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b[^\"\n]{0,200}\{"
                           r"|f'[^'\n]{0,60}\b(?:SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b[^'\n]{0,200}\{",
                           r"(?:execute|query|run)\s*\([^\n]*(?:%|format|\+|\$\{)",
                           r"(?:INSERT|UPDATE|DELETE)[^\n]*\$\{", r"cursor\.execute"],
        "first_probe": "one syntax marker, then a matched true/false pair against the same input",
        "falsifier": "for an immediate sink, identical validated response for the true and false forms; for a stored or deferred sink, the same result after the consumer is triggered",
        "depth_refs": ["skills/web-sqli/references/README.md",
                        "skills/web-sqli/references/extended-corpus.md"],
        "confusable_with": ["web-nosqli"],
    },
    {
        "id": "web-nosqli", "name": "NoSQL / operator injection", "skill_dir": "web-nosqli",
        "evidence_level": "verified",
        "verified_by": ["htb-secnotes-mongoose-rename-prototype-pollution-local-gate"],
        "observation_signals": [r"mongo|mongoose|couch|elasticsearch|redis\b",
                                r"\$ne\b|\$gt\b|\$where\b|\$regex\b|\$rename\b",
                                r"[0-9a-f]{24}\b", r"__v\b",
                                r"object datastore|object-shaped filter|24-hex id",
                                # Measured gap: htb-unearthly-shop's opener — "the decoded
                                # request body is handed to the driver as the whole query
                                # structure" — matched nothing, because every signal above
                                # names an operator or a driver, never the shape of the handoff.
                                r"aggregation (?:pipeline|stage)|\$(?:match|lookup|group|unwind)\b",
                                r"body (?:becomes|is) the (?:query|filter)|whole query structure",
                                r"reaches (?:the )?(?:driver|query) (?:whole|unchanged|as-is)"],
        "source_signals": [r"mongoose\.model|findOne\s*\(\s*req\.|find\s*\(\s*req\.(?:body|query)",
                           r"updateMany|updateOne\s*\(\s*req\.", r"\$where"],
        "first_probe": "send the filter pinned to an object you created, with every write field omitted, and read what comes back",
        "falsifier": "the value is coerced to a string, so no object reaches the query",
        "depth_refs": ["skills/web-nosqli/references/README.md",
                        "skills/web-nosqli/references/operators.md"],
        "confusable_with": ["web-sqli", "web-prototype-pollution"],
        "blast_radius": "a broad filter combined with write fields rewrites the whole collection",
    },
    {
        "id": "web-command-injection", "name": "OS command injection", "skill_dir": "web-command-injection",
        "evidence_level": "verified",
        "verified_by": ["htb-pcalc-php-eval-letter-filter-highbyte-constant-tilde-complement-rce"],
        "observation_signals": [r"command injection",
                                # pcalc: classify returned NOTHING for a textbook
                                # eval-injection observation, because this class
                                # only knew about OS commands. Code reaching an
                                # evaluator is the same class of finding.
                                r"(?:calculator|expression|formula|math|template)[^\n]{0,60}(?:evaluat\w+|\beval\b|comput\w+ (?:the )?(?:result|value))",
                                r"\beval\b[^\n]{0,60}(?:user|request|input|param\w*|\bget\b|\bpost\b|formula|expression|supplied)",
                                r"(?:user|request|input|param\w*|formula|expression|supplied)[^\n]{0,60}(?:reaches|passed to|handed to|goes into|lands in)[^\n]{0,30}\beval\b",
                                r"(?:filter|denylist|blocklist|blocks?|rejects?|strips?)[^\n]{0,70}(?:letters|alphabetic|\ba-z\b|quote\w*)[^\n]{0,70}(?:eval\w*|expression|formula|sandbox|evaluator)", r"\bping\b.{0,20}(?:host|ip|target)",
                                r"uid=\d+\(|gid=\d+\(", r"sh: \d+:|/bin/sh"],
        "source_signals": [r"os\.system\s*\(|subprocess\.(?:run|call|Popen)[^\n]*shell\s*=\s*True",
                           # An evaluator fed by string concatenation, and the
                           # character-class denylist that is usually the only
                           # thing in front of it.
                           r"\beval\s*\(\s*['\"][^'\"\n]{0,40}['\"]\s*\.\s*\$",
                           r"\beval\s*\([^\n]{0,60}(?:\$_(?:GET|POST|REQUEST)|request\.(?:args|form|GET|POST)|params\[)",
                           r"new\s+Function\s*\(|vm\.run(?:InNewContext|InThisContext|InContext)?\s*\(",
                           r"preg_match(?:_all)?\s*\(\s*['\"]/\[[^\]\n]{0,20}a-z[^\]\n]{0,20}\]",
                           r"shell_exec\s*\(|passthru\s*\(|proc_open\s*\(|\bsystem\s*\(\s*\$",
                           r"require\s*\(\s*[\"']child_process|from subprocess import",
                           r"(?:execSync|spawnSync|execFileSync)\s*\(",
                           r"child_process[^\n]{0,40}exec\s*\("],
        "first_probe": "one benign separator with a command whose output is unmistakable, and a timing variant as a fallback channel",
        "falsifier": "the value is passed as a single argv element, never through a shell",
        "depth_refs": ["skills/ctf-web/server-side-exec.md", "skills/ctf-web/server-side-2.md"],
        "confusable_with": ["web-ssti"],
    },
    {
        "id": "web-ssti", "name": "Server-side template injection", "skill_dir": "web-ssti",
        "evidence_level": "verified",
        "verified_by": ["htb-neonify-erb-ssti-newline-filter-bypass",
                        "htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce",
                        "htb-jerryboree-twig-ssti-symfony-fragment-filesystem-write-htaccess-cgi-escape"],
        "observation_signals": [r"\{\{|\$\{|#\{|<%=", r"jinja|twig|freemarker|velocity|thymeleaf|mako|erb\b",
                                r"template", r"\b49\b"],
        "source_signals": [r"render_template_string|Template\s*\(|ERB\.new|\.render\s*\(\s*(?:req|params)",
                           r"eval\s*\(\s*(?:template|tpl)"],
        "first_probe": "one arithmetic marker; confirm the engine from the evaluated form or the error string before any chain",
        "falsifier": "the marker is reflected literally, which is an XSS shape rather than template evaluation",
        "depth_refs": ["skills/ctf-web/server-side-exec.md"],
        "confusable_with": ["web-xss", "web-command-injection"],
    },
    {
        "id": "web-xxe", "name": "XML external entity", "skill_dir": "web-xxe",
        "evidence_level": "verified",
        "verified_by": ["htb-xxe-content-type-branch-simplexml-noent-file-read"],
        "observation_signals": [r"<\?xml|application/xml|text/xml|soap|wsdl",
                                r"\.docx|\.xlsx|\.svg\b", r"doctype|entity"],
        "source_signals": [r"etree\.(?:parse|fromstring)|lxml|xml\.dom|SAXParser|DocumentBuilder",
                           r"simplexml_load|libxml_disable_entity_loader",
                           r"resolve_entities\s*=\s*True"],
        "first_probe": "one entity pointing at a path the target certainly has, and an out-of-band entity when nothing is echoed",
        "falsifier": "the parser is configured with entity resolution disabled",
        "depth_refs": ["skills/ctf-web/server-side-2.md"],
        "confusable_with": ["file-read-primitives", "web-ssrf"],
    },
    # ------------------------------------------------------------ server fetch
    {
        "id": "web-ssrf", "name": "Server-side request forgery", "skill_dir": "web-ssrf",
        "evidence_level": "verified",
        "verified_by": ["htb-red-island-ssrf-gopher-redis-lua-rce",
                        "htb-weather-app-ssrf-crlf-request-smuggling-upsert"],
        "observation_signals": [r"\bssrf\b",
                                r"loopback-only|reachable by the backend itself",
                                r"url\s*[=:]|endpoint\s*[=:]|webhook|url (?:field|param\w*|input)",
                                r"server.?side (?:fetch|request)|fetches? (?:the |a )?url",
                                r"pdf|screenshot|render|thumbnail|preview|import from url",
                                r"127\.0\.0\.1|localhost|169\.254|metadata", r"admin bot|headless",
                                r"outbound (?:http|https|network) request",
                                r"\burl\b[^\n]{0,30}(?:supplied|provided|controlled|given|submitted)",
                                r"\bcurl\b|file_get_contents|http client|requests\.get"],
        "source_signals": [r"requests\.(?:get|post)\s*\(\s*(?:req|request|params|url)",
                           r"urlopen\s*\(|\bhttp\.(?:get|request)\s*\(|\bfetch\s*\(\s*(?:req|url|`)",
                           r"curl_setopt|file_get_contents\s*\(\s*\$", r"http://\$\{|https://\$\{"],
        "first_probe": "one address you control, then the same request against an internal-only address, comparing status and timing",
        "falsifier": "the fetch target is fixed in source and the request never influences it",
        "depth_refs": ["skills/web-ssrf/references/protocol-smuggling.md",
                       "skills/ctf-web/server-side-advanced.md"],
        "confusable_with": ["file-read-primitives", "web-request-smuggling"],
    },
    {
        "id": "web-request-smuggling", "name": "Request smuggling / CRLF injection", "skill_dir": "web-request-smuggling",
        "evidence_level": "verified",
        "verified_by": ["htb-weather-app-ssrf-crlf-request-smuggling-upsert"],
        "observation_signals": [r"smuggl|desync|crlf", r"content-length|transfer-encoding",
                                r"%0d%0a|\\r\\n|\\u010d|\\u010a", r"proxy|gateway|load balancer|nginx|haproxy|traefik"],
        "source_signals": [r"http://\$\{[^}]*\}|https://\$\{[^}]*\}",
                           r"(?:url|endpoint|host)\s*[+]\s*(?:req|request|params)",
                           r"setHeader\s*\([^)]*(?:req|request|params)"],
        "first_probe": "one folded control character inside the interpolated value; compare the upstream error with an ordinary hostname",
        "falsifier": "the value is percent-encoded or validated, so no control character survives into the outbound request",
        "depth_refs": ["skills/ctf-web/client-side.md", "skills/web-triage/references/http-parser-differential.md"],
        "confusable_with": ["web-ssrf", "web-parser-differential"],
        "blast_radius": "a smuggled request executes against the backend as a trusted client; it can change state for everyone",
    },
    {
        "id": "web-parser-differential", "name": "Parser differential / proxy trust", "skill_dir": "web-parser-differential",
        "evidence_level": "verified",
        "verified_by": ["htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce"],
        "observation_signals": [r"traefik|envoy|nginx|haproxy|cloudfront|gateway|reverse proxy",
                                # Wizard Shop: the classifier named only request
                                # smuggling, on the bare word "proxy", because
                                # this class had no vocabulary at all for the
                                # thing it is actually about -- two programs
                                # disagreeing about what a path means.
                                # (?<![:/]) so http:// and https:// are not read as a doubled
                                # path separator; that alone took this signal from
                                # 11 of 48 handouts to 2; requiring a path character right
                                # after the slashes rules out a // line comment.
                                r"(?:(?<![:/])//(?=[A-Za-z0-9_%.-])|/\./|%2e|%2f|dot.?segment|doubled? slash|trailing slash)[^\n]{0,70}(?:bypass\w*|reach\w*|allowed|accepted|\b200\b|differ\w*|through|throttl\w*|\blimit\w*|denied|\b40[13]\b|\b429\b)",
                                r"(?:normali[sz]\w+|decod\w+|resolv\w+|collaps\w+|merg\w+)[^\n]{0,60}\b(?:path|url|uri|slash|segment)\b[^\n]{0,70}(?:differ\w*|before|but|while|backend|upstream|app\b|framework|proxy)",
                                r"(?:proxy|gateway|front|edge|waf|acl|rule|filter)[^\n]{0,70}(?:exact|literal|string|verbatim)[^\n]{0,40}(?:path|match|compar\w+)",
                                r"(?:403|401|denied|blocked|forbidden|rate.?limit\w*|429)[^\n]{0,70}\bexact\b[^\n]{0,30}path",
                                # Two DIFFERENT path shapes close together is the
                                # mechanism itself -- varying the shape rather
                                # than the path -- and needs no vocabulary for
                                # the outcome, which is what the signal above
                                # was too narrow about.
                                r"(?:(?<![:/])//[A-Za-z0-9_]|/\./|%2f|%2e)[^\n]{0,70}(?:(?<![:/])//[A-Za-z0-9_]|/\./|%2f|%2e)",
                                # "the same route spelled differently is treated
                                # differently" stated in words rather than in
                                # path syntax.
                                r"(?:same|identical)\s+(?:path|route|endpoint|url)[^\n]{0,70}(?:differ\w*|never|not |no longer|bypass\w*|allowed|throttl\w*|\blimit\w*|denied|\b429\b)",
                                r"inspects the raw body|raw body before a decoder|before a decoder runs",
                                r"x-real-ip|x-forwarded-for|x-forwarded-host|connection:",
                                r"hop-by-hop", r"403.{0,40}(?:only|internal|local)",
                                # Measured gap: the blind mechanism label for htb-neurosync —
                                # "one front layer is the whole authorization story and its
                                # decision is keyed on a header the client can supply" — named
                                # no class, though it is exactly a proxy-trust boundary.
                                r"middleware|x-middleware|edge (?:function|runtime)",
                                r"(?:one|only|single|front) (?:front )?layer.{0,40}authori",
                                r"header the client can (?:set|supply|control|choose)",
                                r"internal[- ]subrequest|x-middleware-subrequest"],
        "source_signals": [r"headers\.get\s*\(\s*[\"']x-(?:real-ip|forwarded)",
                           r"request\.headers\[[\"']x-", r"if not .*header.*:\s*\n\s*.*local",
                           # A parser differential is a disagreement between TWO
                           # parsers. The three patterns above only describe the
                           # application half, so a proxy config stating the whole
                           # boundary — acl on path,url_dec plus a network ACL —
                           # produced no candidate at all.
                           r"acl\s+\S+\s+(?:path|url|req\.hdr|hdr|method|base)\b",
                           r"http-request\s+(?:deny|set-header|replace-path)\b",
                           r"use_backend\s+\S+\s+if\b|acl\s+\S+\s+src\s+\d",
                           r"-m\s+(?:beg|sub|dir|reg|end)\b",
                           r"location\s+[~^=]|^\s*internal\s*;|proxy_set_header\s"],
        "first_probe": "send the same authenticated-only request twice, once normally and once with the proxy header named in the Connection header",
        "falsifier": "both forms are rejected, so the trust check does not depend on that header",
        "depth_refs": ["skills/web-triage/references/http-parser-differential.md"],
        "confusable_with": ["web-request-smuggling", "web-auth-session"],
    },
    # ------------------------------------------------------------- client side
    {
        "id": "web-xss", "name": "Cross-site scripting", "skill_dir": "web-xss",
        "evidence_level": "verified",
        "verified_by": ["htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce",
                        "htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce"],
        "observation_signals": [r"\bxss\b", r"admin bot|bot visits|report (?:url|link)",
                                # The class had no words for what you actually
                                # SEE first: your own input coming back into the
                                # page. pcalc reflected the raw parameter into a
                                # form value while its filter was refusing the
                                # very same string.
                                r"(?:echo\w*|reflect\w*|render\w*|repopulat\w*|appears?|shown|displayed|comes? back|put back)[^\n]{0,70}(?:unescaped|unencoded|\braw\b|verbatim|without (?:being )?escap\w+|not escaped|as.is|into the (?:form|field|input|page|attribute))",
                                r"(?:refus\w+|reject\w+|error message|invalid|blocked|denied)[^\n]{0,70}\b(?:still|but|yet|anyway)\b[^\n]{0,50}(?:echo\w*|reflect\w*|shown|displayed|appears?|comes? back)",
                                r"content-security-policy|nonce-", r"dompurify|sanitiz"],
        "source_signals": [r"innerHTML|outerHTML|document\.write|insertAdjacentHTML",
                           # PHP had no representation here at all, so pcalc's
                           # views/index.php:21 -- a raw $_GET echoed into an
                           # attribute -- ranked nothing. Tempered so that an
                           # escaped echo does not match.
                           r"<\?=\s*(?:(?!htmlspecialchars|htmlentities|esc_|strip_tags)[^?\n]){0,70}\$_(?:GET|POST|REQUEST|COOKIE)",
                           r"\becho\s+(?:(?!htmlspecialchars|htmlentities|esc_|strip_tags)[^;\n]){0,70}\$_(?:GET|POST|REQUEST|COOKIE)",
                           r"dangerouslySetInnerHTML|mark_safe|\|\s*safe\b|\{\{\{",
                           # The template engines' own opt-out-of-escaping
                           # syntax. The Galactic Times renders stored feedback
                           # through pug's !{...} and nothing here matched it,
                           # so the one real sink in the tree ranked nothing.
                           r"!\{\s*[A-Za-z_$][\w$.\[\]'\"]{0,40}\s*\}",
                           r"<%-\s*[A-Za-z_$]|\{%\s*autoescape\s+(?:off|false)",
                           r"res\.(?:send|write|end)\s*\(\s*`[^`\n]*\$\{",
                           r"(?:render|reply)\s*\([^)\n]*\bhtml\b[^)\n]*\$\{",
                           r"v-html|\bunescape\b|autoescape\s*=\s*False"],
        "first_probe": "one unique harmless marker; find which context it lands in before choosing any payload",
        "falsifier": "nothing renders the injected markup, so there is no viewer and no flag path",
        "depth_refs": ["skills/ctf-web/client-side.md", "skills/ctf-web/client-side-advanced.md"],
        "confusable_with": ["web-ssti", "web-csrf"],
    },
    {
        "id": "web-csrf", "name": "Cross-site request forgery", "skill_dir": "web-csrf",
        "evidence_level": "verified",
        "verified_by": ["htb-tornadoservice-bot-csrf-class-pollution",
                        "htb-ssos-oauth-registration-race-cookie-swap-json-csrf"],
        "observation_signals": [r"\bcsrf\b|xsrf", r"samesite|sameorigin",
                                r"admin bot|bot visits", r"text/plain|enctype"],
        "source_signals": [r"csrf.{0,20}(?:disable|exempt|false)", r"@csrf_exempt",
                           r"samesite\s*[=:]\s*[\"']?none"],
        "first_probe": "a cross-origin form whose content type the endpoint still accepts, submitted by the viewer you control",
        "falsifier": "the endpoint requires a token the attacker page cannot read or a content type a form cannot produce",
        "depth_refs": ["skills/ctf-web/client-side.md"],
        "confusable_with": ["web-xss", "web-cors"],
    },
    {
        "id": "web-cors", "name": "CORS misconfiguration", "skill_dir": "web-cors",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [r"access-control-allow-origin|access-control-allow-credentials",
                                r"\bcors\b", r"origin:",
                                r"\borigin header\b|cross.?origin",
                                r"allows? credentials|with credentials"],
        "source_signals": [r"Access-Control-Allow-Origin[\"']?\s*[,:]\s*[\"']?\*",
                           r"origin.{0,30}(?:reflect|echo)", r"cors\s*\(\s*\{[^}]*origin\s*:\s*true"],
        "first_probe": "repeat an authenticated request with a foreign Origin and read whether the origin is reflected alongside credentials",
        "falsifier": "the allowed origin is a fixed allowlist, or credentials are not permitted",
        "depth_refs": ["skills/ctf-web/auth-infra.md"],
        "confusable_with": ["web-csrf"],
    },
    {
        "id": "web-open-redirect", "name": "Open redirect", "skill_dir": "web-open-redirect",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [r"redirect|next=|returnurl|callback=|continue=", r"\b30[1237]\b"],
        "source_signals": [r"redirect\s*\(\s*(?:req|request|params|\$_)", r"Location:\s*[\"']?\s*\+"],
        "first_probe": "one external destination in the redirect parameter, following the response Location header exactly",
        "falsifier": "the destination is validated against an allowlist or forced to a relative path",
        "depth_refs": ["skills/ctf-web/auth-and-access.md"],
        "confusable_with": ["web-ssrf", "web-oauth-sso"],
    },
    {
        "id": "web-cache-poisoning", "name": "Cache poisoning / deception", "skill_dir": "web-cache-poisoning",
        "evidence_level": "verified",
        "verified_by": ["htb-encodecept-charset-xss-cache-deception-orm-oracle-marshal-rce"],
        "observation_signals": [r"x-cache|cf-cache-status|\bage:\s*\d|\bvary:", r"cache", r"cdn|varnish|cloudfront"],
        "source_signals": [r"Cache-Control|s-maxage", r"cache\.(?:set|get)\s*\(\s*(?:req|request)"],
        "first_probe": "send an unkeyed header with a unique marker, then request the same URL cleanly and look for the marker",
        "falsifier": "the header is part of the cache key, so the poisoned copy is never served to anyone else",
        "depth_refs": ["skills/ctf-web/client-side.md"],
        "confusable_with": ["web-parser-differential"],
        "blast_radius": "a poisoned entry is served to every other player until it expires",
    },
    # --------------------------------------------------------- object / state
    {
        "id": "web-prototype-pollution", "name": "Prototype / class pollution", "skill_dir": "web-prototype-pollution",
        "evidence_level": "verified",
        "verified_by": ["htb-secnotes-mongoose-rename-prototype-pollution-local-gate",
                        "htb-tornadoservice-bot-csrf-class-pollution",
                        "htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce"],
        "observation_signals": [r"__proto__|prototype pollution|class pollution",
                                r"connection-derived|derived from the connection",
                                r"constructor|__class__|__globals__|__init__",
                                r"merge|deep.?(?:assign|copy|merge)"],
        "source_signals": [r"__proto__", r"Object\.assign\s*\(\s*\{\}?\s*,\s*(?:req|body)",
                           r"(?:_\.)?merge\s*\(|extend\s*\(\s*true", r"setattr\s*\(", r"\$rename"],
        "first_probe": "pollute one harmless property, then read it back through a path that should not have it",
        "falsifier": "the merge rejects reserved keys, or nothing reads the polluted property with a fallback",
        "depth_refs": ["skills/ctf-web/node-and-prototype.md"],
        "confusable_with": ["web-nosqli", "web-deserialization"],
        "blast_radius": "pollution is global to the process: every later request inherits it until restart",
    },
    {
        "id": "web-deserialization", "name": "Unsafe deserialization", "skill_dir": "web-deserialization",
        "evidence_level": "verified",
        "verified_by": ["htb-dllama-pickle-cookie-auth-bypass-latex-verbatiminput",
                        "htb-py2-pickle-cookie-reduce-rce-rendered-output"],
        "observation_signals": [r"\brO0AB|\baced0005|\bgAN|O:\d+:\"|\bBAhJ|\bAAEAAAD",
                                r"deserial|unserial|pickle|marshal|viewstate"],
        "source_signals": [r"pickle\.loads|yaml\.load\s*\(|unserialize|ObjectInputStream|readObject",
                           # .NET: the configuration IS the vulnerability. Any
                           # TypeNameHandling but None lets the JSON name the
                           # CLR type, so look in the app's own assembly for a
                           # property setter with a side effect.
                           r"TypeNameHandling\s*(?:=|\.)\s*(?:TypeNameHandling\.)?(?:All|Objects|Auto|Arrays)",
                           r"JavaScriptSerializer|SimpleTypeResolver|LosFormatter|NetDataContractSerializer|ObjectStateFormatter|EnableUnsafeBinaryFormatterSerialization",
                           r"Marshal\.load|BinaryFormatter|torch\.load|joblib\.load",
                           # pickle.loads is the convenience form. A challenge that
                           # WANTS a restricted unpickler subclasses Unpickler and
                           # overrides find_class, which the line above never saw.
                           r"Unpickler\b|find_class\s*\(|restricted_loads|\.load\s*\(\s*\)\s*$"],
        "first_probe": "identify the format from the blob's own magic before touching any gadget",
        "falsifier": "the blob is signed with a key that is not leaked and not reachable",
        "depth_refs": ["skills/ctf-web/server-side-deser.md"],
        "confusable_with": ["web-prototype-pollution"],
    },
    {
        "id": "web-race-condition", "name": "Race condition / TOCTOU", "skill_dir": "web-race-condition",
        "evidence_level": "verified",
        "verified_by": ["htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce",
                        "htb-ssos-oauth-registration-race-cookie-swap-json-csrf"],
        "observation_signals": [r"race condition|toctou", r"balance|coupon|voucher|one.?time|redeem",
                                r"verification token|confirmation (?:code|email|link)", r"rate.?limit|per.?user limit|quota"],
        "source_signals": [r"(?:get|select|find)[^\n]{0,80}\n[^\n]{0,80}(?:update|save|commit)",
                           r"await [^\n]*\n[^\n]*await [^\n]*(?:token|balance|count)"],
        "first_probe": "two interleaved requests, not a flood: the point is to land the second commit inside the window, and a flood hides which one did",
        "falsifier": "the read and the write happen inside one transaction or behind one lock",
        "depth_refs": ["skills/web-race-condition/references/README.md"],
        "confusable_with": ["web-logic-flaw"],
        "blast_radius": "racing a shared resource can corrupt it for other players; race an object you own",
    },
    {
        "id": "web-logic-flaw", "name": "Business logic / mass assignment", "skill_dir": "web-logic-flaw",
        "evidence_level": "verified",
        "verified_by": ["pico-pachinko-revisited-node-offset-scale-wrap-instruction-overwrite"],
        "observation_signals": [r"registration|signup|checkout|coupon|workflow|approval",
                                r"role|is_?admin|privilege|status"],
        "source_signals": [r"(?:update|create)\s*\(\s*(?:req\.body|request\.(?:json|form))\s*\)",
                           r"\*\*(?:request|data)\b", r"setattr\s*\(\s*\w+\s*,\s*k"],
        "first_probe": "one extra field the model has but the form does not send, or one step of the flow skipped",
        "falsifier": "the handler reads an explicit allowlist of fields and ignores everything else",
        "depth_refs": ["skills/ctf-web/auth-and-access.md"],
        "confusable_with": ["web-idor", "web-race-condition"],
    },
    # --------------------------------------------------------- identity / authz
    {
        "id": "web-auth-session", "name": "Authentication and session", "skill_dir": "web-auth-session",
        "evidence_level": "verified",
        "verified_by": ["htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli",
                        "htb-tornadoservice-bot-csrf-class-pollution",
                        "htb-ssos-oauth-registration-race-cookie-swap-json-csrf"],
        "observation_signals": [r"\bjwt\b|bearer |eyJ[A-Za-z0-9_-]{6,}",
                                r"session|jsessionid|connect\.sid|phpsessid|laravel_session",
                                r"cookie_secret|app_key|secret_key|signed cookie", r"""\balg\b|\bhs256\b|\brs256\b|alg\w*\s*['"]?\s*[:=]\s*['"]?\s*none""",
                                r"\botp\b|one.?time (?:code|password)|verification code|confirmation code|activation code",
                                r"password reset|forgot password|magic link",
                                r"passwordless|no password (?:field|input|required)|no credential",
                                r"(?:log ?in|sign ?in|authenticat\w+)[^\n]{0,40}\b(?:only|just)\b[^\n]{0,30}(?:username|user name|email|account name)",
                                r"(?:signature|\bmacs?\b|hmac|hash|integrity check)[^\n]{0,45}(?:does not cover|only covers?|covers? only|computed over only|applied to a prefix|prefix of)",
                                r"reuse the (?:original |old )?(?:signature|mac|hmac)",
                                r"\bbcrypt\b[^\n]{0,40}(?:72|truncat)"],
        "source_signals": [r"jwt\.(?:decode|verify|sign)|jsonwebtoken|create_signed_value",
                           # .NET: claims taken from a PARSE rather than from
                           # the validated token, and the middleware shape that
                           # writes a redirect and then runs the pipeline anyway.
                           r"(?:ReadJwtToken|ReadToken)\s*\([^\n)]*\)\s*as\s+JwtSecurityToken",
                           r"Response\.Redirect\s*\([^\n]*\)\s*;[\s\S]{0,500}await\s+_next\s*\(\s*context\s*\)",
                           r"APP_KEY|SECRET_KEY|cookie_secret|secure_cookie",
                           r"verify\s*=\s*False|algorithms\s*=\s*\[[^\]]*none"],
        "first_probe": "decode and read the token before modifying anything; the weakness is usually visible in the header or the claims",
        "falsifier": "the signature is verified with a key that is neither leaked nor guessable",
        "depth_refs": ["skills/web-auth-session/references/jwt-attacks.md",
                        "skills/web-auth-session/references/extended-jwt.md"],
        "confusable_with": ["web-oauth-sso", "web-idor"],
    },
    {
        "id": "web-oauth-sso", "name": "OAuth / SSO flow", "skill_dir": "web-oauth-sso",
        "evidence_level": "verified",
        "verified_by": ["htb-ssos-oauth-registration-race-cookie-swap-json-csrf"],
        "observation_signals": [r"oauth|openid|oidc|saml|single sign|sso\b",
                                r"redirect_uri|client_id|response_type|authorization_code",
                                r"state=|nonce=", r"/authorize|/token|/callback"],
        "source_signals": [r"client_secret|redirect_uri", r"state\s*(?:!=|==)\s*", r"\.well-known/openid"],
        "first_probe": "walk the whole flow once and record every redirect, parameter and cookie set, before changing any of them",
        "falsifier": "the state parameter is bound to the session and the redirect target is a strict allowlist",
        "depth_refs": ["skills/web-auth-session/references/oauth-flow-issues.md", "skills/ctf-web/auth-infra.md"],
        "confusable_with": ["web-auth-session", "web-open-redirect"],
    },
    {
        "id": "web-idor", "name": "Broken object-level authorization", "skill_dir": "web-idor",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [r"\bidor\b", r"/(?:users?|orders?|files?|notes?|invoices?)/\d+",
                                r"user_?id|account_?id|object_?id", r"[0-9a-f]{8}-[0-9a-f]{4}-",
                                r"(?:chang|increment|modif|tamper)\w*[^\n]{0,30}\bid\b",
                                r"another (?:user|account|customer|person)'?s?\b"],
        "source_signals": [r"findById\s*\(\s*req\.params|WHERE id\s*=\s*\$?\{?(?:req|params)",
                           r"get_object_or_404\s*\([^,]+,\s*(?:pk|id)\s*="],
        "first_probe": "create an object as one identity, then request its identifier as a second identity",
        "falsifier": "the handler scopes the lookup by the authenticated owner",
        "depth_refs": ["skills/web-idor/references/README.md",
                        "skills/web-idor/references/sequential-enumeration.md",
                        "skills/web-idor/references/uuid-analysis.md",
                        "skills/web-idor/references/api-idor.md",
                        "skills/web-idor/references/file-idor.md",
                        "skills/web-idor/references/enumeration.md"],
        "confusable_with": ["web-logic-flaw", "web-auth-session"],
    },
    # ------------------------------------------------------------ file surface
    {
        "id": "file-read-primitives", "name": "Arbitrary file read / source disclosure", "skill_dir": "file-read-primitives",
        "evidence_level": "verified",
        "verified_by": ["htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli",
                        "htb-red-island-ssrf-gopher-redis-lua-rce"],
        "observation_signals": [r"\.\./|%2e%2e|traversal|\blfi\b", r"\bfile://",
                                r"\?(?:file|page|path|download|doc|template)=", r"/proc/self",
                                r"\balias\b|/assets\.\.", r"\.env\b|source (?:leak|disclosure)|leaked source",
                                r"php://filter",
                                r"\bfilename\b[^\n]{0,30}param|param\w*[^\n]{0,20}\bfilename\b",
                                r"download (?:endpoint|route|handler)|serves? (?:a |the )?file",
                                r"(?:error|exception|traceback|stack trace|debug|\b50[03]\b[^\n]{0,12}(?:page|error|response))[^\n]{0,45}(?:environment|config\w*|settings|\.env\b|secret)",
                                r"environment table|unhandled exception[^\n]{0,40}(?:print|show|reveal|leak|dump)"],
        "source_signals": [r"(?:include|require)(?:_once)?\s*\(\s*\$_(?:GET|POST|REQUEST|COOKIE)",
                           r"file_get_contents\s*\(\s*\$_|readfile\s*\(\s*\$",
                           r"(?<![a-z])open\s*\(\s*(?:os\.path\.join\s*\()?\s*[^,)\n]*(?:req|request|params)",
                           r"(?:send_file|sendFile|res\.download|sendfile)\s*\([^)\n]*(?:req|request|params|\$\{)",
                           r"path\.join\s*\([^)\n]*(?:req\.|request\.|params)",
                           r"php://filter|\.\./\.\./"],
        "first_probe": "an absolute path to a file the target certainly has, before trying any traversal",
        "falsifier": "the path is resolved and confined to a fixed directory",
        "depth_refs": ["skills/file-read-primitives/references/traversal-and-wrappers.md"],
        "confusable_with": ["web-ssrf", "web-xxe"],
    },
    {
        "id": "web-file-upload", "name": "Unrestricted file upload", "skill_dir": "web-file-upload",
        "evidence_level": "verified",
        "verified_by": ["htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce",
                        "htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce"],
        "observation_signals": [r"upload|multipart/form-data|filename=",
                                r"\bavatars?\b|\battachments?\b|\bimports?\b|\bplugins?\b|\.tar\b|\.zip\b",
                                r"image/|mime|magic byte"],
        "source_signals": [r"multer|move_uploaded_file|request\.files|\.save\s*\(\s*(?:os\.path\.join|path)",
                           r"os\.path\.join\s*\([^,]+,\s*(?:file|filename)"],
        "first_probe": "a benign marker file first; the question is where it is stored and what later reads or executes it",
        "falsifier": "the stored file is renamed, served with a fixed type, and never parsed again",
        "depth_refs": ["skills/web-file-upload/references/content-bypass.md"],
        "confusable_with": ["file-read-primitives"],
    },
    # ------------------------------------------------------------------- other
    {
        "id": "web-graphql", "name": "GraphQL abuse", "skill_dir": "web-graphql",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [r"graphql|/gql\b", r"__schema|__typename|introspection",
                                r"\bquery\s*\{|\bmutation\s*\{"],
        "source_signals": [r"graphql|apollo|graphene|strawberry", r"introspection\s*[=:]\s*True"],
        "first_probe": "one introspection query; if it is disabled, one field-suggestion error to recover names",
        "falsifier": "introspection is off and errors reveal no field names",
        "depth_refs": ["skills/ctf-web/server-side-2.md"],
        "confusable_with": ["web-idor", "web-logic-flaw"],
    },
    {
        "id": "web-web3", "name": "Smart contract / web3", "skill_dir": "web-web3",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [r"solidity|\.sol\b|ethereum|web3|rpc endpoint|foundry|hardhat",
                                r"0x[0-9a-f]{40}\b", r"setup\(\)|isSolved\(\)"],
        "source_signals": [r"pragma solidity|contract \w+\s*\{", r"delegatecall|selfdestruct|tx\.origin"],
        "first_probe": "read the setup contract and the solved condition first; that names the exact state you must reach",
        "falsifier": "the solved condition depends on state no external caller can change",
        "depth_refs": ["skills/web-web3/references/extended.md"],
        "confusable_with": [],
    },
    {
        "id": "web-xs-leaks", "name": "Cross-site leak / browser side channel",
        "skill_dir": "web-xs-leaks",
        "evidence_level": "verified",
        "verified_by": ["htb-stylish-css-unicode-range-token-leak-bot-selforigin-approve-sqlite-limit-blind"],
        "observation_signals": [r"admin bot|report to admin|visit.{0,20}url|headless",
                                r"xs-?leak|side.?channel",
                                r"window\.length|frame count|cache probe",
                                r"script-src\s+'none'",
                                # Stylish: the leak was a font load, and the CSP
                                # directive that allowed it named the channel.
                                r"@font-face|unicode-range",
                                r"font-src[^\n;]*\*"],
        "source_signals": [r"puppeteer|playwright|selenium|chromedriver|google-chrome",
                           r"script-src\s+'none'",
                           r"font-src[^\n;\"']*\*",
                           r"URLBlocklist|URLAllowlist|policies/managed",
                           r"setCookie[\s\S]{0,120}sameSite",
                           r"maxmemory-policy\s+(?:allkeys|volatile)-lru"],
        "first_probe": "decide first where attacker code may run: if CSP or a URL allowlist keeps you from executing script on any origin the bot can reach, enumerate every piece of server state a plain GET from the bot can change, and use that as the read-back channel",
        "falsifier": "the bot can reach no attacker-influenced state at all, and no observable on the target changes as a function of what the victim's browser loaded",
        "depth_refs": ["skills/ctf-web/client-side.md"],
        "confusable_with": ["web-xss", "web-cache-poisoning", "web-csrf"],
        "blast_radius": "the read-back channel is often a shared cache or store; filling it to force eviction destroys every other key, so never run it against an instance someone else is using",
    },

    # ------------------------------------------------------- DFIR evidence families
    # Not vulnerability classes. Each one is a family of artifacts that answers one
    # kind of investigation question in an artifact-bundle lab (HTB Sherlocks), and
    # each is a mechanism layer that tools/decide.py can force a switch between -
    # which is the whole reason they are classes and not just router table rows.
    # category is "dfir", which is why main() uses setdefault rather than assignment.
    # source_signals is empty on purpose: a Sherlock ships no application source, so
    # there is nothing for a source scan to match. Every observation_signal below was
    # measured to match ZERO of the five tools/system_eval.py classification case
    # texts and ZERO handout files under challenges/.
    {
        "id": "dfir-authentication-trace", "name": "Authentication and logon trace",
        "skill_dir": "dfir-authentication-trace", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\b(?:4624|4625|4634|4647|4648|4672|4776)\b",
            r"logon type\s*\d{1,2}|\blogon types?\b",
            r"\b(?:4768|4769|4771)\b",
            r"auth\.log|\bwtmp\b|\bbtmp\b|\blastlog\b",
            r"failed logon|successful logon|logon session|logonid",
            r"terminalservices-localsessionmanager|remoteconnectionmanager|rdpcorets",
        ],
        "source_signals": [],
        "first_probe": "filter the event set to 4624 and read the LogonType and IpAddress fields of the first match",
        "falsifier": "no authentication record names a source address or an account outside the host's own service accounts, and every logon is type 5 service or type 0 system",
        "depth_refs": ["skills/dfir-sherlock-triage/windows-event-logs.md",
                       "skills/ctf-forensics/linux-forensics.md"],
        "confusable_with": ["dfir-execution-trace", "dfir-network-exfil-trace"],
    },
    {
        "id": "dfir-execution-trace", "name": "Process execution trace",
        "skill_dir": "dfir-execution-trace", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\bsysmon\b",
            r"\b(?:4688|4103|4104)\b",
            r"processguid|parentimage|parentcommandline|newprocessname",
            r"\.pf\b|prefetch (?:file|director|hash|run)",
            r"amcache|shimcache|appcompatcache|userassist",
            r"consolehost_history|psreadline|encodedcommand|script block logging",
        ],
        "source_signals": [],
        "first_probe": "filter to Sysmon event 1 or Security 4688 and read the CommandLine and ParentImage of the first match",
        "falsifier": "no event 1, 4688, 4103 or 4104 exists in the set, and every process artifact present names a signed binary under the system directory with no command line carrying a URL or an encoded run",
        "depth_refs": ["skills/dfir-sherlock-triage/windows-event-logs.md",
                       "skills/dfir-sherlock-triage/registry-and-execution.md"],
        "confusable_with": ["dfir-persistence-trace", "dfir-authentication-trace"],
    },
    {
        "id": "dfir-persistence-trace", "name": "Host persistence trace",
        "skill_dir": "dfir-persistence-trace", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\brunonce\b|\brunonceex\b|\brun key\b|\brun keys\b",
            r"currentversion\\+run|currentcontrolset\\+services",
            r"\b(?:7045|4697|4698|4699|4702)\b",
            r"taskcache|schtasks|scheduled task xml",
            r"__eventfilter|commandlineeventconsumer|filtertoconsumerbinding",
            r"systemd timer|authorized_keys|ld\.so\.preload|/etc/cron\.d|launchdaemons",
        ],
        "source_signals": [],
        "first_probe": "read the Run and RunOnce values and the Services subkeys from the SOFTWARE and SYSTEM hives, and compare each image path against the intrusion window",
        "falsifier": "every autostart entry and service image path resolves to a signed vendor binary whose file creation time predates the intrusion window",
        "depth_refs": ["skills/dfir-sherlock-triage/registry-and-execution.md",
                       "skills/ctf-forensics/linux-forensics.md"],
        "confusable_with": ["dfir-execution-trace", "dfir-antiforensics-trace"],
    },
    {
        "id": "dfir-filesystem-timeline", "name": "Filesystem metadata timeline",
        "skill_dir": "dfir-filesystem-timeline", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\$mft\b|\$usnjrnl\b|\$extend\b|\$boot\b",
            r"usn journal|usn_record|usnjrnl",
            r"standard_information|\$file_name\b|timestomp",
            r"\$recycle\.bin|jump ?list|automaticdestinations",
            r"\bshellbags?\b|usrclass\.dat",
            r"\bmactime\b|\bbodyfile\b|tsk_gettimes|fls -m",
        ],
        "source_signals": [],
        "first_probe": "build a bodyfile from the filesystem metadata and read the entries inside the intrusion window in chronological order",
        "falsifier": "no file was created, renamed or deleted inside the intrusion window outside routine operating-system paths, and the $STANDARD_INFORMATION and $FILE_NAME timestamps agree on every candidate",
        "depth_refs": ["skills/dfir-sherlock-triage/filesystem-timeline.md",
                       "skills/ctf-forensics/windows.md"],
        "confusable_with": ["dfir-antiforensics-trace", "dfir-execution-trace"],
    },
    {
        "id": "dfir-network-exfil-trace", "name": "Network and exfiltration trace",
        "skill_dir": "dfir-network-exfil-trace", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\bdestinationip\b|\bdestinationhostname\b|dns query name",
            r"io,phs|conv,tcp|--export-objects",
            r"srudb\.dat|qmgr\.db|pfirewall\.log",
            r"beacon(?:ing)? interval|\bc2 beacon",
            r"conn\.log|eve\.json|\bzeek\b|\bsuricata\b",
            r"dns tunnel(?:ling|ing)?|dns exfil",
        ],
        "source_signals": [],
        "first_probe": "read the per-peer byte counts in each direction and identify the peer with the largest outbound volume, then join it to the owning process",
        "falsifier": "every outbound conversation resolves to a vendor update or telemetry endpoint, and the largest outbound volume in the window is smaller than a routine update",
        "depth_refs": ["skills/dfir-sherlock-triage/network-and-cloud.md"],
        "confusable_with": ["dfir-execution-trace", "dfir-cloud-audit-trace"],
    },
    {
        "id": "dfir-cloud-audit-trace", "name": "Cloud audit trail",
        "skill_dir": "dfir-cloud-audit-trace", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\bcloudtrail\b",
            r"useridentity\.(?:type|arn)|\bsessioncontext\b|\bassumedrole\b",
            r"getcalleridentity|createaccesskey|putbucketpolicy|attachuserpolicy|createloginprofile",
            r"vpc flow log|\bguardduty\b",
            r"unified audit log|sign-?in logs|userprincipalname|conditionalaccess",
            r"s3 (?:server )?access log|\bconsolelogin\b",
        ],
        "source_signals": [],
        "first_probe": "extract eventTime, eventName, sourceIPAddress and userIdentity.arn from every record, sort by time, and read the first action that is not a read",
        "falsifier": "every recorded action belongs to a service principal or an automation role whose behaviour is unchanged across the whole window, and no credential or policy object was created or modified",
        "depth_refs": ["skills/dfir-sherlock-triage/network-and-cloud.md"],
        "confusable_with": ["dfir-authentication-trace", "dfir-network-exfil-trace"],
    },
    {
        "id": "dfir-antiforensics-trace", "name": "Anti-forensics and log tampering trace",
        "skill_dir": "dfir-antiforensics-trace", "category": "dfir",
        "evidence_level": "catalogue", "verified_by": [],
        "observation_signals": [
            r"\b1102\b|audit log (?:was )?cleared|log clearing",
            r"timestomp|setfiletime",
            r"vssadmin delete shadows|volume shadow cop",
            r"usn deletejournal|fsutil usn",
            r"detectionhistory|\bmplog\b|defender quarantine",
            r"\b4719\b|auditpol /clear|\befstmpwp\b",
        ],
        "source_signals": [],
        "first_probe": "look for Security 1102 and, whether or not it is present, read the event record identifiers in order and report the largest discontinuity",
        "falsifier": "record identifiers are contiguous across the whole window, no 1102 or 104 exists, and the $STANDARD_INFORMATION and $FILE_NAME timestamps agree on every file created in the window",
        "depth_refs": ["skills/dfir-sherlock-triage/windows-event-logs.md",
                       "skills/ctf-forensics/windows.md"],
        "confusable_with": ["dfir-filesystem-timeline", "dfir-persistence-trace"],
    },
]


def self_name_signal(entry):
    """The names a person actually types for this class, as one anchored pattern.

    classify.py is the first command AGENTS.md tells the agent to run, and it
    returned nothing at all for `sqli in a login form`. Measured across fifteen
    classes, four did not match their own name — sqli, ssti, xxe and nosqli —
    while xss, ssrf, csrf and cors did, purely because those letters happened to
    appear inside an unrelated pattern. The taxonomy knew how to recognise the
    evidence for a class and not the name of it.

    Derived rather than hand-listed so a renamed class cannot drift from the
    word that finds it. Anchored on both sides so `sqli` does not fire inside
    `nosqli`, and `sql injection` does not fire inside `nosql injection`.
    """
    words = {entry["id"].split("-", 1)[-1]}          # web-sqli -> sqli
    words.add(entry["id"].replace("-", " "))          # web-sqli -> web sqli
    words.add(entry["id"].split("-", 1)[-1].replace("-", " "))
    words.add(entry["name"].lower())                  # SQL injection
    for extra in entry.get("aka", []):
        words.add(extra.lower())
    # A one- or two-letter token is noise, and a name with a slash is two names.
    parts = set()
    for word in words:
        for piece in word.split(" / "):
            piece = piece.strip()
            if len(piece) >= 3:
                parts.add(re.escape(piece))
    # Longest first so the alternation prefers the most specific name, then
    # alphabetical: a set iterates in hash order, so sorting on length alone
    # made the generator emit a different file on every run.
    ordered = sorted(parts, key=lambda piece: (-len(piece), piece))
    return r"(?<![a-z0-9])(?:%s)(?![a-z0-9])" % "|".join(ordered)


def main():
    seen = set()
    for entry in CLASSES:
        assert entry["id"] not in seen, "duplicate class id: " + entry["id"]
        seen.add(entry["id"])
        # setdefault, not assignment: the tree gained DFIR evidence-family classes
        # whose category is "dfir", and an unconditional assignment relabelled every
        # one of them "web". Output-neutral for the 25 web classes, which carry no
        # category key in the literal below.
        entry.setdefault("category", "web")
        entry["observation_signals"] = (list(entry.get("observation_signals", []))
                                        + [self_name_signal(entry)])
        entry["skill"] = "skills/%s/SKILL.md" % entry["skill_dir"]
        entry.setdefault("blast_radius", None)
        if entry["evidence_level"] == "verified":
            assert entry["verified_by"], entry["id"] + " claims verified with no chain card"
        else:
            assert not entry["verified_by"], entry["id"] + " is catalogue but names chain cards"
    document = {
        "schema_version": 1,
        "description": (
            "Bug-class taxonomy. observation_signals match black-box evidence; "
            "source_signals match code. evidence_level is verified only when a chain "
            "card in knowledge/chains/ proves the class was solved here."),
        "evidence_levels": {
            "verified": "at least one verified chain card names this class; verified_by lists them",
            "catalogue": "standard published class, no local solve yet; the skill is a starting point, not proven local knowledge",
        },
        "rules": [
            "A signal match is a candidate, never proof. Run the class's first_probe.",
            "A class whose falsifier is observed is closed for this challenge, with the observation recorded.",
            "evidence_level is raised to verified only by tools/classify_solve.py after a flag is verified.",
            "confusable_with names classes that share signals; check those before committing to one.",
        ],
        "classes": CLASSES,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    verified = sum(1 for c in CLASSES if c["evidence_level"] == "verified")
    print(json.dumps({"written": os.path.relpath(OUT, ROOT), "classes": len(CLASSES),
                      "verified": verified, "catalogue": len(CLASSES) - verified}))


if __name__ == "__main__":
    main()
