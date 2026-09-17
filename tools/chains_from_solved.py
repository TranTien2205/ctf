#!/usr/bin/env python3
"""Convert the verified notes in solved/ into structured, matchable chain cards.

Every field is taken from the corresponding solved/*.md file. Flags are redacted:
these cards exist to match preconditions, not to carry answers.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "chains")

CHAINS = [
    {
        "id": "htb-tornadoservice-bot-csrf-class-pollution",
        "source_note": "solved/tornadoservice.md",
        "challenge": {"name": "TornadoService", "platform": "HackTheBox", "event": None,
                      "category": "web", "solved_at": "2026-09-06", "assistance": "writeup-assisted"},
        "stack": ["python", "tornado 6.4.1"],
        "preconditions": {
            "all_of": ["a write endpoint refuses non-local requests",
                       "a bot or renderer visits an attacker-supplied address"],
            "any_of": ["python framework holds a module-level app object",
                       "the update handler merges request JSON into an object"]
        },
        "signals": ["tornado", "only localhost", "remote_ip", "report", "bot", "cookie_secret",
                    "__class__", "__init__", "__globals__", "signed cookie", "class pollution", "csrf"],
        "chain": [
            {"step": 1, "stage": "recon", "action": "enumerate /get_tornados, /update_tornado, /report_tornado?ip=, /login, /stats",
             "why": "the write endpoint answers 403 'Only localhost' and the report endpoint drives a headless browser"},
            {"step": 2, "stage": "falsified", "action": "header IP spoofing via XFF, X-Real-IP, Forwarded, Host",
             "why": "remote_ip is the socket peer, so header spoofing does not pass the local check"},
            {"step": 3, "stage": "primitive", "action": "host a page on a tunnel and submit it to the bot; the page posts a text/plain CSRF form to http://127.0.0.1:1337/update_tornado",
             "why": "the bot is the only client whose socket peer is local"},
            {"step": 4, "stage": "pivot", "action": "body carries Python class pollution: machine_id plus __class__.__init__.__globals__.APP.settings.cookie_secret",
             "why": "a recursive setattr merge reaches the module-level APP object"},
            {"step": 5, "stage": "flag", "action": "forge a Tornado v2 signed cookie with the new secret and request /stats",
             "why": "the flag is behind the signed-cookie identity check"}
        ],
        "first_confirming_probe": {
            "request": "fetch a public read endpoint to obtain a valid object id, then confirm the write endpoint answers 403 for a direct request",
            "expected": "403 that names a local-only restriction, and a readable object id",
            "falsifier": "the write endpoint accepts a direct request, so no bot relay is needed"
        },
        "blast_radius": "the pollution changes a global application setting; other players on a shared instance lose their sessions",
        "verification": {"status": "verified_live", "evidence": "HTTP 200 from /stats with the forged cookie"},
        "reuse_when": ["a trust check reads a value the request cannot set, and some other client can",
                       "a Python merge routine accepts attacker-shaped keys"],
        "known_traps": ["ngrok inserts an interstitial that headless bots cannot pass; a plain SSH reverse tunnel does not",
                        "firing two payload routes at once makes the success unattributable: fire one, wait, then the other"],
        "flag": None
    },
    {
        "id": "htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli",
        "source_note": "solved/nginxatsu.md",
        "challenge": {"name": "nginxatsu", "platform": "HackTheBox", "event": None,
                      "category": "web", "solved_at": "2026-09-06", "assistance": "writeup-assisted"},
        "stack": ["nginx", "php 7.4", "laravel", "mysql"],
        "preconditions": {
            "all_of": ["a static path is served through an nginx alias",
                       "the session driver stores state in an encrypted cookie"],
            "any_of": ["a controller passes a session value into orderBy or another query fragment",
                       "the response status differs between a true and a false condition"]
        },
        "signals": ["nginx", "laravel", "alias", "traversal", "assets", ".env", "APP_KEY",
                    "session cookie", "orderBy", "direction", "blind sqli", "500", "php"],
        "chain": [
            {"step": 1, "stage": "recon", "action": "fingerprint nginx, PHP 7.4 and Laravel error pages",
             "why": "the app generates nginx configs, so an alias misconfiguration is plausible"},
            {"step": 2, "stage": "primitive", "action": "read source through the alias traversal path /assets../.env and /assets../app/Http/Controllers/API/ConfigController.php",
             "why": "an alias without a trailing slash lets the prefix be escaped"},
            {"step": 3, "stage": "pivot", "action": "use the leaked APP_KEY to forge the AES-CBC session cookie; the payload is a JSON envelope containing a PHP-serialized session",
             "why": "SESSION_DRIVER=cookie means the whole session is attacker-controlled once the key is known"},
            {"step": 4, "stage": "sink", "action": "set the session order key to a query fragment and read the boolean oracle on GET /api/configs",
             "why": "orderBy takes the session value, and a true condition returns 200 while a false one returns 500"},
            {"step": 5, "stage": "flag", "action": "binary-search the flag column ASCII value by value, then verify with a HEX comparison",
             "why": "there is no echo channel, only the status-code oracle"}
        ],
        "first_confirming_probe": {
            "request": "request the static prefix with a single trailing dot-dot segment and compare the response with the normal static path",
            "expected": "a file outside the static root is returned",
            "falsifier": "the traversal path 404s or is normalised away"
        },
        "blast_radius": "read-only extraction; the forged session affects only the attacker's own requests",
        "verification": {"status": "verified_live", "evidence": "extracted value confirmed by a HEX equality probe against the database row"},
        "reuse_when": ["a framework key leaks and the session lives client-side",
                       "a query fragment such as a sort column comes from session state"],
        "known_traps": ["MySQL case-insensitive collations make 't' equal 'T'; case-exact extraction needs a binary comparison",
                        "a linear charset scan is far too slow; binary search costs about seven probes per character",
                        "a string replace applied after formatting cannot match the placeholder it was meant to replace"],
        "flag": None
    },
    {
        "id": "htb-red-island-ssrf-gopher-redis-lua-rce",
        "source_note": "solved/red-island.md",
        "challenge": {"name": "Red Island", "platform": "HackTheBox", "event": "Cyber Apocalypse 2022",
                      "category": "web", "solved_at": "2026-09-07", "assistance": "writeup-assisted"},
        "stack": ["node", "express", "redis", "connect-redis"],
        "preconditions": {
            "all_of": ["a request field supplies a URL the server fetches"],
            "any_of": ["the fetch result or error body is echoed back to the client",
                       "an internal service listens on a loopback port"]
        },
        "signals": ["express", "x-powered-by", "picture url", "convert", "ssrf", "file://",
                    "gopher", "redis", "6379", "lua", "loadlib", "readflag"],
        "chain": [
            {"step": 1, "stage": "recon", "action": "fingerprint Express and the login/register flow, then search writeups by challenge name",
             "why": "a named platform challenge usually has a published chain"},
            {"step": 2, "stage": "primitive", "action": "POST the URL field and confirm the fetch with a loopback address and with a file scheme",
             "why": "the fetched content is echoed inside the error message, which makes a read channel"},
            {"step": 3, "stage": "pivot", "action": "read the application source through the file scheme to learn the session store is Redis on loopback",
             "why": "the next hop must be evidenced, not guessed"},
            {"step": 4, "stage": "sink", "action": "use a gopher URL to write raw RESP commands to Redis, calling eval with a Lua payload whose length prefix matches the exact byte length",
             "why": "gopher lets an HTTP client speak a line protocol"},
            {"step": 5, "stage": "flag", "action": "escape the Lua sandbox with package.loadlib to reach io.popen, list the filesystem, then run the flag-reading helper",
             "why": "the flag is only readable through a setuid helper"}
        ],
        "first_confirming_probe": {
            "request": "submit a loopback URL in the fetch field and read the full response body, including error text",
            "expected": "content or an error that proves the server performed the fetch",
            "falsifier": "the field is validated to an allowlist and never reaches a client"
        },
        "blast_radius": "eval on the shared Redis instance affects every player's session; prefer read-only Lua first",
        "verification": {"status": "verified_live", "evidence": "flag returned by the helper binary through the Lua channel"},
        "reuse_when": ["an SSRF exists and a line-protocol service listens on loopback",
                       "an error body echoes fetched content"],
        "known_traps": ["the gopher payload length prefix must equal the exact byte length of the Lua string",
                        "always read error bodies: this app leaked the fetched file inside a non-200 message"],
        "flag": None
    },
    {
        "id": "htb-red-island-2-json-unicode-waf-bypass-time-blind-sqli",
        "source_note": "solved/red-island-2.md",
        "challenge": {"name": "red-island-2", "platform": "HTB-style", "event": None,
                      "category": "web", "solved_at": "2026-09-07", "assistance": "self-solved"},
        "stack": ["php", "mysql"],
        "preconditions": {
            "all_of": ["a filter inspects the raw request body",
                       "the body is JSON-decoded after that filter runs"],
            "any_of": ["the decoded value reaches a query", "responses are identical so only timing can answer"]
        },
        "signals": ["waf", "json_decode", "vsprintf", "blocked words", "sleep", "time-based",
                    "blind sqli", "\\u", "unicode escape", "php"],
        "chain": [
            {"step": 1, "stage": "recon", "action": "read the source published on the index page: body passes through a filter, then JSON decoding, then a formatted SQL string",
             "why": "the order of filter and decode is the whole bug"},
            {"step": 2, "stage": "primitive", "action": "escape every character of the payload as a unicode escape so no blocked character or keyword appears in the raw body",
             "why": "the filter scans bytes before decoding, so escaped text passes and decodes back to the blocked text"},
            {"step": 3, "stage": "sink", "action": "confirm a timing oracle with a conditional sleep and compare against a measured baseline",
             "why": "the response body never changes, so timing is the only channel"},
            {"step": 4, "stage": "flag", "action": "binary-search each character sequentially, ordering any grouped output explicitly",
             "why": "unordered results across queries corrupt the extraction"}
        ],
        "first_confirming_probe": {
            "request": "send one blocked keyword as unicode escapes and compare the response with the same keyword sent literally",
            "expected": "the escaped form is accepted while the literal form is rejected",
            "falsifier": "both forms are rejected, so the filter runs after decoding"
        },
        "blast_radius": "conditional sleeps hold a worker per matching row; keep the row count and the sleep short on a shared instance",
        "verification": {"status": "verified_live", "evidence": "extracted value confirmed by a HEX equality probe"},
        "reuse_when": ["any filter scans a raw body before a decoder normalises it",
                       "a blind oracle is the only available channel"],
        "known_traps": ["grouped concatenation needs an explicit ordering or rows arrive in a different order each query",
                        "parallel timing probes contend on the worker pool and corrupt the oracle; extract sequentially",
                        "measure the baseline before choosing a threshold; jitter can cross a threshold set too close",
                        "end of string reads as a space in a numeric binary search; test for a non-zero character code before appending",
                        "compare hex strings as strings, not as a numeric literal, or the comparison silently fails"],
        "flag": None
    },
    {
        "id": "htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce",
        "source_note": "solved/apexsurvive.md",
        "challenge": {"name": "ApexSurvive", "platform": "HackTheBox", "event": "Cyber Apocalypse 2024",
                      "category": "web", "solved_at": "2026-09-07", "assistance": "writeup-assisted"},
        "stack": ["python", "flask", "jinja2", "uwsgi"],
        "preconditions": {
            "all_of": ["a profile update commits before a second function re-reads the stored value"],
            "any_of": ["a stored field is rendered inside a template literal",
                       "an admin file-write accepts a validated file type and a joined path"]
        },
        "signals": ["race condition", "profile", "verification token", "sendEmail", "stored xss",
                    "template literal", "dompurify", "bleach", "admin bot", "uwsgi", "jinja",
                    "arbitrary file write", "pdf", "polyglot"],
        "chain": [
            {"step": 1, "stage": "primitive", "action": "race the profile update so an interleaved commit lands between the update and the token re-read, delivering another address's token to a mailbox you can read",
             "why": "the token is fetched after the profile is committed, in a different function"},
            {"step": 2, "stage": "pivot", "action": "store a note whose value is rendered inside a template literal; a single interpolation expression plus a closing backtick runs before the sanitiser",
             "why": "the sanitiser operates on the DOM after the literal has already been evaluated"},
            {"step": 3, "stage": "exfil", "action": "have the bot's script create an item whose note field carries the admin cookie, then read that item back as a normal user",
             "why": "the application itself is the exfiltration channel when outbound access is unavailable"},
            {"step": 4, "stage": "sink", "action": "use the admin file write with a joined path; the validator requires a parseable PDF, so carry the payload bytes inside the content stream",
             "why": "a dirty write must still satisfy the validator"},
            {"step": 5, "stage": "flag", "action": "overwrite an already-cached template with one containing a template-injection expression, then add a new module file that is not imported to force a worker reload and reset the template cache",
             "why": "the reload resets the cache without bricking the service"}
        ],
        "first_confirming_probe": {
            "request": "send two interleaved profile updates and observe which address receives which token",
            "expected": "a token belonging to one address arrives at the other",
            "falsifier": "the token is read inside the same transaction as the update"
        },
        "blast_radius": "overwriting server configuration or an imported module can permanently break the instance",
        "verification": {"status": "verified_live", "evidence": "flag rendered in the page by the overwritten template"},
        "reuse_when": ["a commit and a dependent read are split across functions",
                       "stored content is interpolated into JavaScript before sanitisation"],
        "known_traps": ["a partial configuration overwrite loses the socket and bricks the instance permanently",
                        "a trigger file that gets imported on reload must be valid code; a PDF placed there bricks the worker",
                        "the HTML sanitiser escapes ampersands in stored text, so query strings must be built at runtime",
                        "base64url decoding in the browser fails without manual padding",
                        "the bot re-logs in per visit, so stolen cookies expire quickly; verify immediately"],
        "flag": None
    },
    {
        "id": "htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce",
        "source_note": "solved/novacore.md",
        "challenge": {"name": "NovaCore", "platform": "HackTheBox", "event": "Business CTF 2025",
                      "category": "web", "solved_at": "2026-09-07", "assistance": "writeup-assisted"},
        "stack": ["traefik 2.10.4", "python", "flask", "c"],
        "preconditions": {
            "all_of": ["a reverse proxy adds a header the application trusts"],
            "any_of": ["a missing header is treated as a local request",
                       "a custom daemon copies request data into a fixed-size buffer"]
        },
        "signals": ["traefik", "x-real-ip", "hop-by-hop", "connection header", "token_required",
                    "strcpy", "cache", "csp", "nonce", "dom clobbering", "prototype pollution",
                    "eval", "exiftool", "tar", "elf", "polyglot", "plugin"],
        "chain": [
            {"step": 1, "stage": "primitive", "action": "list the proxy-added header in the Connection header so the proxy strips its own header before forwarding",
             "why": "the application treats a request with no proxy header as local and skips the token check"},
            {"step": 2, "stage": "pivot", "action": "overflow a fixed-size value in the cache daemon so the write lands in the next entry's key, letting another user's record be addressed",
             "why": "the API exposes the set operation, so no exploit code is needed"},
            {"step": 3, "stage": "sink", "action": "poison the admin's feed with markup, then bypass the content policy using the site's own nonce-bearing script: clobber the DOM lookups it uses, redirect its fetch to an attacker-writable store, and pollute the prototype so the value it passes to eval is attacker-controlled",
             "why": "the policy allows only the site's own scripts, so the site's script must be steered"},
            {"step": 4, "stage": "exfil", "action": "post the admin cookie into the same same-site store and read it back",
             "why": "the store is simultaneously the pollution source, the fetch target and the exfiltration channel"},
            {"step": 5, "stage": "flag", "action": "upload a plugin whose joined filename escapes the upload directory, built as an archive/executable polyglot so the content scanner sees an archive while the loader sees an executable, then run it",
             "why": "the scanner and the loader read different offsets of the same file"}
        ],
        "first_confirming_probe": {
            "request": "send the same authenticated-only request twice, once normally and once with the proxy header named in the Connection header",
            "expected": "the second request is accepted without a token",
            "falsifier": "both requests are rejected, so the trust check does not depend on that header"
        },
        "blast_radius": "overwriting a neighbouring cache entry corrupts another user's record; plugin execution runs code on the instance",
        "verification": {"status": "verified_live", "evidence": "flag file read by the executed plugin"},
        "reuse_when": ["an application trusts a header a proxy is expected to set",
                       "a content policy allows the site's own script and that script calls eval on merged JSON"],
        "known_traps": ["the bot runs on a fixed schedule; place the poisoned state first, then poll",
                        "the polyglot only works when the archive bytes are overlaid at the offset the scanner reads"],
        "flag": None
    },
    {
        "id": "htb-secnotes-mongoose-rename-prototype-pollution-local-gate",
        "source_note": "solved/secnotes.md",
        "challenge": {"name": "Secure Notes", "platform": "HackTheBox", "event": None,
                      "category": "web", "solved_at": "2026-09-10", "assistance": "writeup-assisted"},
        "stack": ["node", "express", "mongoose", "mongodb"],
        "preconditions": {
            "all_of": ["an update endpoint places request keys into the update document",
                       "a gate reads a value that normally comes from the connection, not from the request"],
            "any_of": ["the filter argument accepts an object from the request body",
                       "a document is loaded and cloned after the update"]
        },
        "signals": ["express", "mongoose", "mongodb", "noteId", "$rename", "$ne", "update",
                    "prototype pollution", "__proto__", "_peername", "403", "access denied", "/flag"],
        "chain": [
            {"step": 1, "stage": "setup", "action": "create a note whose title and content hold the values the polluted fields should take",
             "why": "the rename operator moves existing values, so the values must already exist"},
            {"step": 2, "stage": "primitive", "action": "send an update whose filter selects only your own note and whose rename targets are dotted paths under __proto__",
             "why": "the rename targets are not validated the way direct assignment paths are"},
            {"step": 3, "stage": "trigger", "action": "read the note back so the loaded document is materialised and the prototype setter fires",
             "why": "the pollution only takes effect when the document is cloned"},
            {"step": 4, "stage": "flag", "action": "request the gated endpoint, which now inherits the polluted address value",
             "why": "the gate falls through to the polluted prototype when the real property is absent"}
        ],
        "first_confirming_probe": {
            "request": "send an update containing only your own note's filter and no content fields, and read the response",
            "expected": "the matched documents are returned unchanged, proving the filter is attacker-shaped and the call is read-safe",
            "falsifier": "the filter is coerced to a string, so no object reaches the query"
        },
        "blast_radius": "a broad filter with content fields overwrites every document in the collection and destroys other players' data; always pin the filter to your own object id",
        "verification": {"status": "verified_live", "evidence": "HTTP 200 from the gated flag endpoint"},
        "reuse_when": ["an update object is attacker-shaped and strict mode blocks only direct assignment",
                       "a trust check reads an optional property with a fallback"],
        "known_traps": ["a broad filter fired before the update semantics are understood mass-updates the collection and can cost the instance",
                        "test update semantics on your own object with the content fields omitted first"],
        "flag": None
    },
    {
        "id": "htb-weather-app-ssrf-crlf-request-smuggling-upsert",
        "source_note": "solved/weather_app.md",
        "challenge": {"name": "Weather App", "platform": "HackTheBox", "event": None,
                      "category": "web", "solved_at": "2026-09-11", "assistance": "self-solved"},
        "stack": ["node", "express", "sqlite"],
        "preconditions": {
            "all_of": ["a request field is interpolated into a URL the server fetches",
                       "a privileged route is restricted to the loopback address"],
            "any_of": ["the interpolated field is not encoded",
                       "a registration query concatenates values into SQL"]
        },
        "signals": ["express", "ssrf", "endpoint", "http.get", "template literal url", "127.0.0.1",
                    "remoteAddress", "register", "crlf", "request smuggling", "INSERT INTO",
                    "ON CONFLICT", "upsert", "sqlite"],
        "chain": [
            {"step": 1, "stage": "recon", "action": "read the routes: registration is loopback-only, the weather route interpolates a request field into a fetched URL, and the login route returns the flag file for one username",
             "why": "the flag path is a privileged account, not a file read"},
            {"step": 2, "stage": "primitive", "action": "place unicode characters that the URL parser folds into space, carriage return and line feed inside the interpolated field",
             "why": "the field is not encoded, so the request line can be terminated and a second request appended"},
            {"step": 3, "stage": "pivot", "action": "append a full registration request to the loopback origin with an exact content length, then a trailing request fragment so the second request is closed",
             "why": "the backend calls itself, so the loopback restriction is satisfied"},
            {"step": 4, "stage": "sink", "action": "carry an upsert payload in the registration password so the existing privileged row's password is replaced instead of inserting a duplicate",
             "why": "the registration query concatenates values, and the username is unique"},
            {"step": 5, "stage": "flag", "action": "log in as the privileged account with the password just set",
             "why": "that route returns the flag file"}
        ],
        "first_confirming_probe": {
            "request": "put a harmless marker with one folded space character into the interpolated field and compare the error with an ordinary hostname",
            "expected": "the parser accepts the folded character, showing the field is not encoded",
            "falsifier": "the field is encoded or validated, so no control characters survive"
        },
        "blast_radius": "the upsert changes an existing account's password on a shared instance; other players lose access to that account",
        "verification": {"status": "verified_live", "evidence": "flag returned in the login response"},
        "reuse_when": ["a loopback-only route exists and the backend can be made to call itself",
                       "a fetched URL is built by interpolation without encoding"],
        "known_traps": ["the injected content length must count the body bytes exactly",
                        "a trailing request fragment is needed so the smuggled request is terminated"],
        "flag": None
    },
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for card in CHAINS:
        card["schema_version"] = 1
        path = os.path.join(OUT, card["id"] + ".json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(card, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    print(json.dumps({"written": len(CHAINS), "directory": OUT}))


if __name__ == "__main__":
    main()
