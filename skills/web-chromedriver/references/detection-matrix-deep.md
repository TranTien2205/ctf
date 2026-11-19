# Detection matrix deep — the full signal grid

## The endpoint-detection grid

```
                 sessionId   JSON error   refused/404   timeout
9515 POST /sess    bare drv    cfg/auth     no driver      filter
4444 POST /sess    Grid node   Grid cap     no Grid        filter
4444 GET /status   Grid inv    Grid4 hub    no hub         filter
/wd/hub/session    Grid3       old Grid     not Grid3      filter
/session (app)     proxied     app route    not proxied    filter
9222 GET /json     CDP         CDP hub      no CDP         filter
4723 POST /sess    Appium      mobile drv   not Appium     filter
9516 POST /sess    alt drv     cfg/auth     no alt         filter
```

Any `sessionId`/`json` column -> the surface is live at that endpoint.

## The bot-detection grid

```
                 supplied      observed      inferred      absent
bot source       copy spec     —             —             —
report/admin     —             bot flow      —             —
"admin visits"   —             bot flow      —             —
flag-by-render   —             bot flow      —             —
server fetch     —             NOT a bot     SSRF not aid   —
no flow          —             —             assume none    dead
```

## The primitive grid

```
                 live probe                        passes when
file read        nav file:///etc/passwd + source    "root:x:0:0" in body
js file read     execute fetch("file:///...")       the file text returns
js exec          execute return 1+1                 returns 2
loopback         nav localhost/admin + source       differs from external
cookie jar       GET /cookies                       cookie list returns
dom              GET /source                        rendered tree returns
screenshot       GET /screenshot                    non-blank PNG
cdp              GET :9222/json                     target list returns
```

## The reproduction grid

```
                 read from source      observe        assume (weakest)
URL              the goto arg          your input       your URL
credential       setCookie/login       —               a flag cookie
wait             the timeout/wait      response delay   5 s
flags            the args array        headers/behav    --headless --no-sandbox
version          package.json/Docker   —               local latest
viewport         setViewport           —               default
```

The "assume" column is the risk — every assumed property weakens the
transfer of a locally-confirmed payload.

## The channel grid

```
                 live probe                    passes when
tunnel           goto/fetch own tunnel         your body, not interstitial
same-origin      a write then a read-back      the store updates
beacon           sendBeacon to listener        listener hit
subresource      Image/script src              listener hit
dns              a resolver query              resolver log hit
```

## The decision matrix

```
                          endpoint answers?    bot flow?
                              /    \              /    \
                           yes      no          yes     no
                          /          \          /        \
                       surface      aid?      aid       dead
                    (primitive       (if no    (repro-  (record)
                     map)            surface)  duce)
```

Run the surface test first — it is the cheaper single probe; run the
bot test second if the surface is dead.
