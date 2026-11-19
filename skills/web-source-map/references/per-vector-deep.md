# Per-vector (deep) — each recon vector in detail

## The endpoint vector

The bundle names server paths the UI may hide — `/api/internal`,
`/admin/export`, `/v2/debug`. Each is a real target once verified.
**Mechanism**: the client ships its own route table; mining it replaces
brute force. **Yield**: the endpoint surface. **Route**: the endpoint's
class.

## The secret vector

A key, token, JWT, or credential baked into client source — `apiKey`,
`token`, `secret`, `process.env.SECRET`. If it verifies, it unlocks the
gated surface. **Mechanism**: the build inlines config; devs ship real
credentials under "config". **Yield**: a live auth path. **Route**:
`web-auth-session`.

## The flag/gate vector

`feature.X`, `config.debug`, `meta.requiresAuth` — a client-side gate
whose endpoint the server may not check. **Mechanism**: the gate is
client-side; the code+endpoint are shipped anyway. **Yield**: a gated
surface that may be public. **Route**: `web-logic-flaw`/`web-idor`.

## The source vector

`sourcesContent` — the original commented source; sinks, logic, keys,
the flag. **Mechanism**: the map discloses the real source. **Yield**:
the code, not the strings. **Route**: the sink's class.

## The internal-host vector

`http://internal.svc`, `api.internal.*`, `postgres://`, a webhook URL —
a host the client calls but the browser cannot reach. **Mechanism**:
the client knows the internal host; an SSRF surface reaches it.
**Yield**: an internal target. **Route**: `web-ssrf`.

## The structure vector

`sources` file names — `src/config/`, `src/admin/` — map the layout;
the names are probe targets (hosted `/src/` paths) and a `file-read`
hint. **Mechanism**: the map leaks the layout even without content.
**Yield**: probe targets + a file-read lead.

## The manifest vector

`_buildManifest`/`asset-manifest`/`precache`/`sw.js` — the build's own
asset+route inventory. **Mechanism**: the manifest enumerates lazy and
hidden chunks `main` misses. **Yield**: the complete surface.

## The adjacent-disclosure vector

`.map` presence signals a lax deployment → `.git`, `.env`, backups,
`src/`, `static/maps/` are likely shipped too. **Mechanism**: the map
is the lax signal. **Yield**: the bigger server-side leak. **Route**:
`web-info-disclosure`/`file-read-primitives`.

## The route-guard vector

`requiresAuth`/`canActivate`/`PrivateRoute` — a client gate on a
shipped route. **Mechanism**: the guard hides the page, not the
endpoint. **Yield**: a gated endpoint that may be public.

## The env/config vector

`process.env`, `DefinePlugin`, env prefixes, `__NEXT_DATA__` —
build-inlined config. **Mechanism**: the build bakes env into the
bundle; devs ship real values. **Yield**: keys, flags, internal hosts.

## The dead-code vector

`if(false)` blocks, commented routes, dev-only endpoints — shipped but
unreachable in the UI. **Mechanism**: dead code still ships; a server
endpoint it names may still be live. **Yield**: a hidden endpoint.
