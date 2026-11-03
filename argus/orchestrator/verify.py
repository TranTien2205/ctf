"""Cross-family verification: a second model reads the evidence, not the claim.

Why a different family and not simply a second pass: two models from the same
family share a prior, so they tend to accept the same weak inference. The
disagreement worth having comes from a model that was not trained to find that
argument convincing.

What the verifier is shown: the finding, the class's proof requirement, and the
evidence records themselves — never the first model's reasoning. What it returns
is one JSON object. A disagreement demotes the finding to a candidate, which is
the correct outcome and the point of the exercise.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from ..ledger import hooks
from ..ledger import proof as matrix
from ..ledger.state import State
from ..runtime import profile as profile_mod, providers
from ..runtime.providers.base import Message
from ..util import bound
from .bus import Bus
from .router import Router

PROMPT = """\
You are reviewing another model's finding from an authorized penetration test.
You are from a different model family on purpose: the useful disagreement is the
one the first model's own reasoning would not have produced.

You are shown the finding, the proof requirement for its class, and the raw
evidence records. You are NOT shown the first model's reasoning, and you should
not reconstruct it.

Answer this and nothing else: **does the evidence, on its own, establish the
claim?**

Reject it if any of these is true:
- the observation could have happened with the vulnerability absent
- a control is missing, so an asymmetry has no baseline
- the proof requirement's checks are met only in appearance (a nonce that does
  not appear, a table with no rows, a reflected payload treated as execution, a
  scanner label treated as evidence)
- the claim is broader than the evidence (one readable record reported as "every
  record", a single endpoint reported as "the application")

Return exactly one JSON object:

{"agrees": true|false,
 "reason": "<one or two sentences, pointing at the specific record or missing control>",
 "severity": "critical|high|medium|low|info",
 "missing": ["<what would settle it, if anything>"]}"""


@dataclass
class Verification:
    finding_id: str
    verifier: str
    agrees: bool
    reason: str
    severity: str = ""
    missing: list | None = None
    cost_usd: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def render_evidence(state: State, finding: dict, limit: int = 6) -> str:
    records = state.load_evidence(finding.get("evidence_ids") or [])[:limit]
    spec = matrix.spec_for(finding.get("vuln_class") or "")
    parts = [f"## Finding {finding['id']}", "",
             f"- class: {finding.get('vuln_class')}",
             f"- title: {finding.get('title')}",
             f"- target: {finding.get('target')}",
             f"- entry point: {json.dumps(finding.get('entry_point') or {})}",
             f"- claimed severity: {finding.get('severity')}",
             f"- impact as claimed: {finding.get('impact') or '(none stated)'}", "",
             "## The requirement for this class", ""]
    if spec:
        parts += [spec.requirement, "",
                  "Required checks: " + ", ".join(spec.required_checks), ""]
    parts += ["## The grading the ledger already applied", "",
              "```json", json.dumps(finding.get("proof") or {}, ensure_ascii=False, indent=1),
              "```", "", "## The evidence, as recorded", ""]
    for record in records:
        trimmed = {key: bound(str(value), 2500) for key, value in record.items()
                   if key not in ("sha256",)}
        parts += [f"### {record.get('id')} ({record.get('kind')})", "```json",
                  json.dumps(trimmed, ensure_ascii=False, indent=1)[:6000], "```", ""]
    return "\n".join(parts)


def verify_finding(engagement: str, finding_id: str, router: Router | None = None,
                   policy: str = "balanced", record: bool = True) -> Verification:
    state = State.load(engagement)
    finding = state.finding(finding_id)
    if finding is None:
        return Verification(finding_id, "", False, "", error=f"no finding {finding_id!r}")
    producing_family = _family_of(finding.get("recorded_by"))
    router = router or Router(policy=policy)
    route = router.route({"id": f"verify-{finding_id}", "kind": "review"},
                         exclude_families=(producing_family,) if producing_family else ())
    if not route.model:
        return Verification(finding_id, "", False, "", error=route.reason)
    model_profile = route.profile or profile_mod.load(route.model)
    provider_name = model_profile.provider
    kwargs: dict = {}
    if provider_name == "opencode":
        kwargs = {"model_prefix": (model_profile.opencode_name or "").split("/")[0]}
    elif model_profile.family == "claude":
        from ..runtime import credentials
        if not credentials.get("anthropic"):
            provider_name, kwargs = "claude_cli", {}
    provider = providers.get(provider_name, **kwargs)
    ok, reason = provider.available()
    if not ok:
        return Verification(finding_id, route.model, False, "", error=reason)
    completion = provider.complete(PROMPT, [Message("user", render_evidence(state, finding))],
                                   [], model_profile)
    if not completion.ok:
        return Verification(finding_id, route.model, False, "", error=completion.error)
    parsed = _extract(completion.text)
    cost = model_profile.cost(completion.input_tokens, completion.output_tokens)
    if parsed is None:
        return Verification(finding_id, route.model, False,
                            bound(completion.text, 400), cost_usd=cost,
                            error="the verifier did not return JSON")
    verification = Verification(finding_id, f"{route.model}({model_profile.family})",
                                bool(parsed.get("agrees")), str(parsed.get("reason") or ""),
                                str(parsed.get("severity") or ""), parsed.get("missing") or [],
                                cost)
    if record:
        hooks.cross_verify(engagement, finding_id, verification.verifier, verification.agrees,
                           bound(verification.reason, 600))
        Bus(engagement).emit("finding.verified", verification.to_dict())
    return verification


def verify_all(engagement: str, policy: str = "balanced", only_confirmed: bool = True,
               router: Router | None = None) -> list[Verification]:
    state = State.load(engagement)
    router = router or Router(policy=policy)
    out = []
    for finding in state.data["findings"]:
        if only_confirmed and finding.get("status") != "confirmed":
            continue
        if finding.get("verified_by"):
            continue
        out.append(verify_finding(engagement, finding["id"], router=router))
    return out


def _family_of(actor: str | None) -> str:
    model = str(actor or "").split(":")[-1]
    if not model:
        return ""
    family = profile_mod.load(model).family
    return "" if family == "unknown" else family


def _extract(text: str):
    text = (text or "").strip()
    for start in [index for index, char in enumerate(text) if char == "{"]:
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        parsed = json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        break
                    if isinstance(parsed, dict) and "agrees" in parsed:
                        return parsed
                    break
    return None


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-verify", description=__doc__.splitlines()[0])
    parser.add_argument("engagement")
    parser.add_argument("--finding", default=None)
    parser.add_argument("--policy", default="balanced")
    parser.add_argument("--show-prompt", action="store_true",
                        help="print what the verifier would be shown, and make no model call")
    args = parser.parse_args(argv)
    if args.show_prompt:
        state = State.load(args.engagement)
        for finding in state.data["findings"]:
            if args.finding and finding["id"] != args.finding:
                continue
            print(render_evidence(state, finding))
            print("-" * 72)
        return 0
    results = ([verify_finding(args.engagement, args.finding, policy=args.policy)]
               if args.finding else verify_all(args.engagement, policy=args.policy))
    for verification in results:
        print(json.dumps(verification.to_dict(), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
