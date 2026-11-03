"""http — one request, two requests, and the comparison between them.

This is the server a model spends most of its calls on. `http.probe` issues one
request and reports status, length, timing and where any token it sent landed.
`http.differential` issues a baseline and a variant and says whether the
difference is real, which is the only honest way to read an injection signal.
"""
from __future__ import annotations

from .. import httpkit
from ..mcp import Server, ToolContext

SERVER = Server("http", "single requests and response differentials")

_COMMON = {
    "url": {"type": "string", "description": "absolute URL; must be in scope"},
    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]},
    "headers": {"type": "object", "description": "extra request headers"},
    "params": {"type": "object", "description": "query parameters merged into the URL"},
    "body": {"type": "string", "description": "raw request body"},
    "json_body": {"type": "object", "description": "body sent as application/json"},
    "cookies": {"type": "string", "description": "Cookie header value"},
    "follow": {"type": "boolean", "description": "follow redirects (default false: the Location is the measurement)"},
    "timeout": {"type": "integer", "description": "seconds, default 15"},
    "token": {"type": "string", "description": "a token to look for in the response, for reflection context"},
    "actor": {"type": "string", "description": "which identity issued this, for differential classes"},
    "note": {"type": "string", "description": "why this request was issued"},
}


def _issue(url: str, method: str = "GET", headers: dict | None = None, params: dict | None = None,
           body: str | None = None, json_body: dict | None = None, cookies: str | None = None,
           follow: bool = False, timeout: int = 15) -> httpkit.HttpResponse:
    return httpkit.request(method, url, headers=headers, params=params, data=body,
                           json_body=json_body, cookies=cookies, timeout=timeout, follow=follow)


@SERVER.tool(
    "http.probe",
    "Issue one HTTP request and report status, length, timing, headers and, if `token` is given, "
    "the parse context the token was reflected into. Redirects are not followed by default because "
    "the Location header is usually the measurement you wanted.",
    {"properties": {"target": {"type": "string", "description": "alias for url"}, **_COMMON},
     "required": []},
)
def probe(context: ToolContext, url: str = "", target: str = "", method: str = "GET",
          headers: dict | None = None, params: dict | None = None, body: str | None = None,
          json_body: dict | None = None, cookies: str | None = None, follow: bool = False,
          timeout: int = 15, token: str = "", actor: str = "", note: str = "") -> dict:
    url = url or target
    if not url:
        return {"ok": False, "error": "bad-arguments", "message": "url is required"}
    response = _issue(url, method, headers, params, body, json_body, cookies, follow, timeout)
    contexts = httpkit.reflection_context(response.body, token) if token else []
    evidence = response.to_evidence()
    evidence.update({"kind": "probe", "target": url, "nonce": token or None,
                     "payload": token or None, "note": note})
    if contexts:
        evidence["reflected_context"] = ",".join(contexts)
    if actor:
        evidence["actor"] = actor
    return {
        "summary": response.summary() + (f" | reflected in: {','.join(contexts)}" if contexts else ""),
        "result": "signal" if response.status is not None else "error",
        "data": {"status": response.status, "length": response.length, "time_ms": response.time_ms,
                 "server": response.header("server"), "content_type": response.header("content-type"),
                 "location": response.header("location"), "reflected_context": contexts},
        "output": response.body[:6000],
        "evidence": evidence,
    }


@SERVER.tool(
    "http.differential",
    "Issue a baseline request and a variant, then report whether the difference is real: status "
    "change, length delta, timing delta, body similarity and the changed lines. Use this for every "
    "injection signal — a difference under the noise floor is reported as noise, not as a finding.",
    {"properties": {
        "url": {"type": "string", "description": "baseline URL"},
        "variant_url": {"type": "string", "description": "variant URL (default: same as url)"},
        "method": _COMMON["method"],
        "headers": _COMMON["headers"],
        "baseline_params": {"type": "object", "description": "query parameters for the baseline"},
        "variant_params": {"type": "object", "description": "query parameters for the variant"},
        "baseline_body": {"type": "string"}, "variant_body": {"type": "string"},
        "cookies": _COMMON["cookies"], "timeout": _COMMON["timeout"],
        "repeat": {"type": "integer", "description": "issue each side N times and use the median timing (default 1)"},
        "note": _COMMON["note"], "actor": _COMMON["actor"],
    }, "required": ["url"]},
)
def differential(context: ToolContext, url: str, variant_url: str = "", method: str = "GET",
                 headers: dict | None = None, baseline_params: dict | None = None,
                 variant_params: dict | None = None, baseline_body: str | None = None,
                 variant_body: str | None = None, cookies: str | None = None, timeout: int = 15,
                 repeat: int = 1, note: str = "", actor: str = "") -> dict:
    repeat = max(1, min(int(repeat), 5))
    baselines = [_issue(url, method, headers, baseline_params, baseline_body, None, cookies, False, timeout)
                 for _ in range(repeat)]
    variants = [_issue(variant_url or url, method, headers, variant_params, variant_body, None,
                       cookies, False, timeout) for _ in range(repeat)]
    baseline, variant = _median(baselines), _median(variants)
    diff = httpkit.compare(baseline, variant)
    # A second baseline against itself: if the page differs from itself, no
    # single-request differential means anything.
    self_noise = httpkit.compare(baselines[0], baselines[-1]) if repeat > 1 else None
    stable = self_noise is None or self_noise.body_similarity >= 0.995
    evidence = {"kind": "probe", "target": url, "note": note,
                "baseline": baseline.to_evidence()["response"],
                "variant": variant.to_evidence()["response"],
                "request": variant.to_evidence()["request"],
                "response": variant.to_evidence()["response"],
                "extracted": {"differential": diff.to_dict(),
                              "baseline_stable": stable,
                              "self_similarity": None if self_noise is None
                              else round(self_noise.body_similarity, 4)}}
    if actor:
        evidence["actor"] = actor
    signal = diff.status_changed or (diff.body_similarity < 0.98 and abs(diff.length_delta) >= 24)
    return {
        "summary": (f"baseline {baseline.status}/{baseline.length}B vs variant "
                    f"{variant.status}/{variant.length}B — {diff.verdict}"
                    + ("" if stable else " | WARNING: the page differs from itself, so this "
                                         "differential proves nothing")),
        "result": "signal" if (signal and stable) else "no-signal",
        "data": diff.to_dict() | {"baseline_stable": stable},
        "output": "\n".join(diff.changed_lines[:40]),
        "evidence": evidence,
        "next": ("record this as the discriminating observation and move to the proof step"
                 if signal and stable else
                 "no usable difference: change the hypothesis or the input, not the payload"),
    }


def _median(responses: list[httpkit.HttpResponse]) -> httpkit.HttpResponse:
    ordered = sorted(responses, key=lambda r: r.time_ms)
    return ordered[len(ordered) // 2]
