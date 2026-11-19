# Library drivers — Selenium and Playwright

## Which to reach for

- **curl** — no library installed, or you want the raw protocol. Always works.
- **Selenium** — you already have a Python env and want a session quickly.
- **Playwright** — you want console/network capture built in, auto-waiting, or a bundled Chromium.

`which chromedriver` before relying on any of them. A missing driver
fails at session creation, not at the payload — check first.

## Selenium — Python

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

o = Options()
o.add_argument("--headless=new")
o.add_argument("--no-sandbox")
o.add_argument("--disable-gpu")
o.add_argument("--disable-dev-shm-usage")
# o.binary_location = "/usr/bin/chromium"   # when needed

driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=o)
driver.get("http://challenge/")
print(driver.page_source[:500])
driver.quit()
```

`driver.quit()` is the `DELETE /session` — leaking it leaks the browser.

### Reading the console

Selenium can pull browser logs when the capability is enabled:

```python
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
caps = DesiredCapabilities.CHROME
caps["goog:loggingPrefs"] = {"browser": "ALL"}
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
driver = webdriver.Chrome(options=o)
driver.get(url)
for e in driver.get_log("browser"):
    print(e["level"], e["message"])
```

### Running script

```python
result = driver.execute_script("return document.body.innerText")
driver.execute_async_script(
    "var d=arguments[0];fetch('/api/me').then(r=>r.text()).then(d)")
```

### Cookies

```python
driver.add_cookie({"name": "session", "value": "abc", "path": "/"})
print(driver.get_cookies())
```

## Playwright — Python

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page()
    page.on("console", lambda m: print("CONSOLE:", m.text))
    page.on("pageerror", lambda e: print("PAGEERROR:", e))
    page.goto("http://challenge/")
    print(page.content()[:500])
    browser.close()
```

Playwright's console/pageerror/network hooks are the reason to reach
for it over Selenium — the observability the live bot lacks is a
one-liner.

### Network capture

```python
page.on("request", lambda r: print("REQ:", r.method, r.url))
page.on("response", lambda r: print("RESP:", r.status, r.url))
```

The request hook answers the exfiltration question directly — did the
payload's `fetch("https://your-tunnel/...")` actually leave.

### Playwright — Node

```javascript
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ["--no-sandbox"] });
  const page = await browser.newPage();
  page.on('console', m => console.log('CONSOLE:', m.text()));
  await page.goto('http://challenge/');
  console.log((await page.content()).slice(0, 500));
  await browser.close();
})();
```

## The bot-reproduction flags

Match the challenge's bot on the flags that change behaviour. The
common ones and what they do:

| Flag | Effect | When the bot likely has it |
|---|---|---|
| `--headless` / `--headless=new` | no window | nearly always |
| `--no-sandbox` | run as root in a container | inside Docker, almost always |
| `--disable-gpu` | no GPU | nearly always in containers |
| `--disable-dev-shm-usage` | use /tmp instead of /dev/shm | small `/dev/shm` containers |
| `--user-agent=...` | a specific UA | when the bot spoofs one |
| `--disable-web-security` | no same-origin policy | when the challenge intends cross-origin reads |
| `--ignore-certificate-errors` | accept self-signed | when the challenge uses a self-signed cert |

Read the bot's own source for the exact list — do not guess.

## Timeouts

```python
# selenium
driver.set_page_load_timeout(15)
driver.implicitly_wait(3)

# playwright
page.set_default_timeout(15000)
page.goto(url, wait_until="networkidle")   # wait for network quiet
```

A bot that waits five seconds on the page is reproduced with an
explicit `page.wait_for_timeout(5000)` or an `execute_async_script`
setTimeout — match its wait, not your preference.
