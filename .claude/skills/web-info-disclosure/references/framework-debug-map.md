# Framework-specific debug surfaces — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Werkzeug 'DEBUG MODE' banner | Flask debug console | /console PIN exploit |
| Django yellow error page | DEBUG=True | settings values, SQL in trace |
| Laravel Ignition/Whoops | debug on | env vars in error page |
| Rails /rails/info/routes or console | dev endpoints | route map |
| Next.js /_next/data or dev errors | dev overlay | route data |
| Spring Whitelabel error page | Spring stack | actuator family |

## Falsifier

Falsifier — the framework's debug paths all 404 and error pages are generic production pages: debug surface off.
