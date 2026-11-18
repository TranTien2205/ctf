# The Initial Read — the first ten minutes on a deser challenge

## The intake order — what to read first

```
1. is there source?              → whitebox-hunt.md, grep-first
2. is there a blob?              → decode → fingerprint → detection.md
3. is there an endpoint?         → corrupt-diff the blob field
4. what's the stack?             → headers/page/framework → framework-sinks.md
```

## The fingerprint reflex — the byte-level ID

```bash
# every opaque field — decode and fingerprint in 5 seconds:
echo -n "$BLOB" | base64 -d | xxd | head -4

rO0 / aced        → java-deser.md
O: / a: / Tzo     → php-deser.md
gAN / gAR / 80 03 → python-deser.md
BAh / \x04\x08    → ruby-deser.md
AAEAAAD / /wEP    → dotnet-deser.md
{"$type" / __type → dotnet-deser.md (Json.NET/JavaScriptSerializer)
_$$ND_FUNC$$_     → nodejs-deser.md
!! / !ruby/       → yaml-deser.md
```

## The corrupt-diff — the 30-second confirm

```bash
# take the real blob, flip one byte, send it:
python3 tools/web/http_probe.py --challenge "$C" --class web-deserialization \
  --url "$BASE/endpoint" --header "Cookie: u=$CORRUPTED" \
  --evidence-regex 'unserialize|Unpickling|InvalidClass|SerializationException|dump format|Incomplete_Class' \
  --evidence-kind class --on-match confirms --on-miss inconclusive
```

A parser signature on your corrupted bytes = the class confirmed — that is
the whole first proof, and it costs one request.

## The "is it signed" check — before crafting

```bash
# the blob is signed if:
#   - a sibling field is a signature (sig=, mac=, .hmac)
#   - the blob has a fixed-length tail that changes with content
#   - the framework is Rails/Laravel/Django/Flask/ASP.NET (default-signed)
#   - tampering the blob returns a "signature" error, not a parser error
```

`signature-bypass.md` → the key-hunt. Sign first, gadget second.

## The "is the classpath visible" check — gadget feasibility

```bash
# does the source/handout show the libs?
cat composer.lock package-lock.json Gemfile.lock pom.xml 2>/dev/null
ls vendor/ WEB-INF/lib/ 2>/dev/null
# → the version picks the chain — phpggc/ysoserial/-l
```

## The "what's the stack" fingerprint

```
X-Powered-By: PHP/7.x        → PHP serialize
Server: Werkzeug + Flask      → itsdangerous (pickle? JSON?)
Server: IIS + .aspx           → ViewState/Json.NET
Server: Apache-Coyote/Tomcat  → Java OIS
X-Runtime: Ruby/Rails         → Marshal
Server: Express/node          → node-serialize / plain JSON
```

## The "first hypothesis" — the cheapest probe to run

```
the blob fingerprint known    → corrupt-diff (this module)
the format + a marker path     → marker/URLDNS (blind-deser.md)
the classpath + lib known      → the matching chain
source visible                 → whitebox-hunt.md, grep the sink
```

## The ten-minute boundary — what "done" looks like at minute ten

```
□ the format fingerprinted (or ruled out)
□ the corrupt-diff run — confirmed or falsified
□ the signature question answered (signed? key reachable?)
□ the classpath measured or the chain picked
□ the first gadget either built or the reason it can't be stated
```

Ten minutes gets you to "I know whether this is a deserialization challenge
and roughly which path" — anything past that without the fingerprint+
confirm is the budget-burning mistake `common-mistakes.md` warns about.

## Output to record

- The fingerprint + the module it routes to
- The corrupt-diff result (confirmed/falsified/inconclusive)
- The signature answer + the classpath answer
