# Stack playbook: fastapi

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

FastAPI fingerprints: uvicorn/h11 Server header,
auto-docs at /docs /redoc /openapi.json, JSON {detail: ...}
error shape.

Recon checks:
- GET /openapi.json -> complete route+param+schema map in one
  request; recon is done when this returns 200
- /docs Swagger UI -> same endpoints clickable
- {detail: ...} 422 -> pydantic validation surface
- uvicorn header -> ASGI stack confirmed
- WebSocket routes in openapi.json

Predicts: idor on path ids, massassign on pydantic models,
nosqli on MongoBeanie filters, injection via raw queries.
## Pivot

Signal harvested -> out-*; route named -> that skill.
