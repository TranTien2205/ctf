# Smuggle workflow — the operational sequence

## The 10-step ladder

```text
1. recon — is a proxy in the path?
2. fold — does %0d%0a survive?
3. CL.TE — does it hang?
4. TE.CL — does the next request 404?
5. TE.TE — which obfuscation lands?
6. CL.CL — the dup-CL differential?
7. CL.0 — the body-ignored?
8. upgrade/h2 — the tunnel/downgrade?
9. exploit — the internal-route/cookie/cache?
10. readback — the smuggle's output?
```

`workflow.md` / `desync-workflow.md`.

## The byte-count — the discipline

```text
Content-Length = bytes between \r\n\r\n and end-of-body
chunk-size = hex
trailing \r\n required
```

`cl-te-desync.md` — the #1 failure.

## The Host — the vhost

```text
Host: t — the back-end's vhost
Host: internal — the internal vhost
Host: t:9000 — the internal port
```

`virtual-host.md`.

## The trailing fragment — the clean close

```text
GET / HTTP/1.1
```

appended after the smuggle — `cl-te-desync.md`.

## The readback — the channel

```text
self-poison → stored-param → echo → OOB → deferred
```

`smuggle-readback.md`.

## The evidence — the verbatim excerpt

```bash
python3 tools/hooks.py post-probe <name> --request "..." \
  --verdict confirms --evidence-kind class --class web-request-smuggling \
  --hypothesis-id h1 --evidence "<excerpt>" --response "<raw>"
```

`evidence-rules.md`.

## The budget — 5/15/25/45

`AGENTS.md` — the escalation order.

## The escalation — budget exhausted

```text
chain_match → reclassify → writeup_search → novel_plan → fanout_sweep → solver_handoff
```

each `state.py --strategy-used <rung>` — `AGENTS.md`.
