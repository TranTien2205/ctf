# White-box hunt — finding the driver and the bot in source

## The grep set

```
# the driver / endpoint
webdriver|chromedriver|geckodriver|msedgedriver|selenium|webdriverio
remote-debugging-port|--remote-debugging|debuggerAddress
new webdriver|webdriver.Chrome|webdriver.Remote|launch\(|newPage

# the bot
puppeteer|playwright|admin.?bot|visit|report|browse|headless
bot\.js|admin\.py|visit\.js|browser\.newPage|page\.goto

# the surface
file://|localhost|127\.0\.0\.1|/flag|proc/self/environ
```

## What each find names

| Find | Names |
|---|---|
| `chromedriver`/`webdriver` spawn | the endpoint's port + flags |
| `puppeteer`/`playwright` `launch` | the bot — its args are the spec |
| `page.goto(url)` | the bot's URL — how your input reaches it |
| `setCookie`/`page.setCookie` | the bot's credential — name/domain/path |
| `setTimeout`/`wait_for` | the bot's wait — the payload's budget |
| `--remote-debugging-port` | a CDP endpoint on that port |
| `docker-compose` `bot`/`admin` service | the bot container + its port |
| `file://` in a bot/visit path | a `file://` read the challenge exposes |

## Reading the bot source as a spec

```javascript
// bot.js — read each line as a property to copy
const browser = await puppeteer.launch({args:['--no-sandbox','--disable-gpu']});
const page = await browser.newPage();
await page.setCookie({name:'flag',value:FLAG,domain:'challenge',path:'/'});
await page.goto(userControlledUrl, {timeout:10000});
await new Promise(r=>setTimeout(r,5000));
await browser.close();
```

Each line is a reproduction property: flags, cookie, URL, wait.

## Reading the driver spawn

```python
# the spawn names the port and the flags
chromedriver --port=9515 --whitelisted-ips="" --verbose
# or a selenium Grid hub
java -jar selenium-server.jar hub --port 4444
```

The spawn names the endpoint's port and its access control — an empty
`--whitelisted-ips` or an open Grid is the exposed surface.

## The compose read

```yaml
services:
  bot:
    build: ./bot        # <- the bot's Dockerfile = the spec
    ports: ["9515:9515"] # <- the exposed driver port
  app:
    build: ./app
```

A `bot`/`admin`/`browser` service names the container; its `ports:`
names the exposed endpoint; its Dockerfile names the bot's flags and
version.

## The intended-path read

A challenge that exposes a driver usually intends it as the surface —
read *which* surface it points at:

- a bot that visits your URL -> the XSS/exfil path
- a driver port -> the file-read/loopback path
- a bot that reads a flag page -> the screenshot/DOM read

The handout names the intended surface; the skill is the means to it.
