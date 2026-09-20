# BonechewerCon — SOLVED (self-solved)

- Platform: HackTheBox (web). Laravel on nginx, `X-Powered-By: PHP/7.4.12`.
- Date: 2026-09-18
- Target supplied: `http://154.57.164.82:31182` (black-box)
- Flag: redacted; verified live in the error page returned by `POST /`
- Cost: 2 probes, ~2 minutes.

## Chain

1. `GET /` → 200, a single registration form and the line
   *"Due to heavy server workload ... the website is currently under maintenance"*.
   Cookie is `laravel_session` as a **plain 40-character id**, not the
   `{"iv","value","mac"}` envelope, so `SESSION_DRIVER` is not the cookie driver.
2. The form is `<form method="POST">` with an empty action. Submitting it
   (`POST /` with `name=PROBE123`) does not register anything — it returns a
   **Whoops debug page**, 209560 bytes:
   `Symfony\Component\HttpKernel\Exception\MethodNotAllowedHttpException`
   — *"The POST method is not supported for this route. Supported methods: GET, HEAD."*
   The form's own method is the bug trigger: the route was never wired for POST.
3. `APP_DEBUG` is on, so Whoops renders its detail tables. The labels present are
   `GET Data`, `POST Data`, `Files`, `Cookies`, `Session`, `Server/Request Data`,
   **`Environment Variables`**, `Registered Handlers`.
4. The `Environment Variables` table is the whole `.env`, and the flag is the
   value of **`APP_KEY`**. Also disclosed: `APP_ENV=local`, `DB_CONNECTION=mysql`,
   `DB_USERNAME=root`, `DB_PASSWORD=""` (empty), `SESSION_DRIVER=file`,
   `REDIS_HOST=127.0.0.1`.

## What did not work, and why it was the wrong instinct

`GET /?name=PROBE123` is byte-for-byte identical to `GET /` (diff empty) — the
parameter is never reflected, so there is no SSTI and no injection surface on the
GET route. The "under maintenance" copy and `PreventRequestsDuringMaintenance` in
the stack trace both suggest a Laravel maintenance-mode bypass; neither is the
bug. The application is not in maintenance mode at all — it returns 200.
Both are flavour text.

## Reusable lessons

- **Submit the form with the method it declares, even when the route may not
  support it.** The unsupported method is what produced the debug page; a
  "correct" GET produced nothing at all. A 405 on a framework with debug on is a
  full configuration read.
- **Whoops `Environment Variables` is the `.env`**, verbatim and unredacted. When
  a Laravel error page renders, go to that table before reading the stack trace.
- **Read the session cookie's shape to learn the session driver.** A plain
  40-character id means a server-side driver, so no APP_KEY session forge applies
  here even though APP_KEY leaked — the key was the objective, not a pivot.
- The stack trace also disclosed the deployment layout without any file read:
  root `/www`, entry `/www/public/index.php`, and the vendor middleware chain.
