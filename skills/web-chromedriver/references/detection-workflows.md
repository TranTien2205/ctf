# Detection workflows — the hunt, end to end

## Workflow A: the handout-first hunt

```
1. grep the source: webdriver|chromedriver|geckodriver|selenium|
                    puppeteer|playwright|headless|remote-debugging|bot
2. a bot script?  -> read its URL/cookie/wait/flags -> debugging aid
3. a driver spawn?-> read the port + flags -> attack surface at that port
4. a compose bot service? -> the bot's container -> aid
5. nothing? -> black-box probe next
```

The handout answers both questions in one read — do it first.

## Workflow B: the port sweep

```
1. POST :9515/session   -> bare chromedriver?
2. POST :4444/session   -> Grid?
3. GET  :9222/json      -> CDP?
4. POST :9516/session   -> alternate driver
5. POST /session        -> proxied on the app port?
6. GET  :4444/status    -> Grid inventory
```

A `sessionId` on any -> attack surface live; all refused -> surface dead.

## Workflow C: the bot-flow hunt

```
1. report/flag/contact form that "admin reviews"?  -> bot flow
2. a /admin or /visit endpoint you trigger?         -> bot flow
3. "admin will check" in the challenge text?        -> bot flow
4. a stored/reflected field the admin sees?         -> bot flow
```

Any -> debugging aid; none -> no bot, no aid.

## Workflow D: the primitive map (once a session exists)

```
file?   nav file:///etc/passwd -> source
js?     execute return 1+1
loop?   nav localhost/admin -> source
jar?    GET /cookies
dom?    GET /source
shot?   GET /screenshot
cdp?    GET :9222/json
```

## Workflow E: the reproduction-fidelity check

```
1. local driver, same flags/version as the bot
2. set the bot's cookie, navigate to its URL, wait its wait
3. page.content() vs the live view — same DOM axes?
4. divergence -> the reproduction is the bug, fix before developing
```

## Workflow F: the channel check

```
1. inside the driver: goto your tunnel URL
2. page.content() shows YOUR body?  -> channel live
3. shows an interstitial/refused?   -> channel dead for headless
```

## The combined decision

```
handout -> bot flow? -> aid (reproduce)
        -> driver port? -> surface (primitive map)
        -> neither -> class dead, record why
```
