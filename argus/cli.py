"""argus — one command in front of the four planes.

    argus open      start an engagement: objective, scope, risk tiers, authorisation
    argus target    admit a target (refused unless the scope covers it)
    argus status    the ledger, compactly
    argus next      what the controller says happens next
    argus plan      write a plan: a workflow template, deterministic, or by the strongest model
    argus workflows the plan templates on the shelf
    argus run       execute the plan across the fleet
    argus agent     one model, one loop, one task
    argus verify    have another family read the evidence behind each finding
    argus report    render the report
    argus metrics   probes, refusals and cost per confirmed finding
    argus mcp       serve the tool plane over MCP stdio
    argus tools     the tool table, with risk tiers
    argus fleet     what can run here, and what each task kind would route to
    argus proof     what a class must produce before it can be recorded
    argus gate      run the test suite
"""
from __future__ import annotations

import argparse
import json
import sys

from . import config
from .ledger import decide as decide_mod
from .ledger import hooks
from .ledger import proof as matrix
from .ledger import report as report_mod
from .ledger.state import State


def _print(data, as_json: bool, text: str = "") -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        print(text or json.dumps(data, ensure_ascii=False, indent=2, default=str))


# --- commands ----------------------------------------------------------------

def cmd_open(args) -> int:
    scope = {"in_scope": args.in_scope or [], "out_of_scope": args.out_of_scope or [],
             "allowed_ports": [int(p) for p in (args.ports or [])], "resolve": args.resolve}
    outcome = hooks.open_engagement(args.engagement, args.objective, scope,
                                    tiers=args.tiers, authorisation=args.authorisation)
    _print(outcome.to_dict(), args.json, outcome.message)
    if outcome.ok:
        print(f"\nnext: argus target {args.engagement} <url>")
    return 0 if outcome.ok else 1


def cmd_target(args) -> int:
    outcome = hooks.add_target(args.engagement, args.target, args.note or "")
    _print(outcome.to_dict(), args.json, outcome.message)
    return 0 if outcome.ok else 1


def cmd_status(args) -> int:
    state = State.load(args.engagement)
    digest = state.digest()
    if args.json:
        _print(digest, True)
        return 0
    print(f"{digest['engagement']}: {digest['objective'] or '(no objective)'}  [{digest['status']}]")
    print(f"tiers: {', '.join(digest['tiers'])}   targets: {', '.join(digest['targets']) or 'none'}")
    print(f"surface: {digest['surface_counts'] or 'nothing mapped'}")
    print(f"probes: {digest['probes']['total']} {digest['probes']['by_class'] or ''}")
    budget = digest["budget"]
    print(f"budget: {budget['probes']}/{budget['probe_limit']} probes, "
          f"{budget['minutes']}/{budget['minute_limit']} active minutes")
    if digest["hypotheses"]["open"]:
        print("\nopen hypotheses:")
        for hypothesis in digest["hypotheses"]["open"]:
            print(f"  {hypothesis['id']}  p{hypothesis['priority']:<3} {hypothesis['class']:14} "
                  f"{hypothesis['probes']} probe(s)  {hypothesis['statement']}")
    if digest["findings"]:
        print("\nfindings:")
        for finding in digest["findings"]:
            print(f"  {finding['id']}  {finding['class']:14} {finding['grade']:10} {finding['title']}")
    print(f"\nstrategies spent: {', '.join(digest['strategies_used']) or 'none'}"
          f"   next rung: {digest['next_strategy'] or 'ladder exhausted'}")
    return 0


def cmd_next(args) -> int:
    action = decide_mod.decide(args.engagement)
    _print(action.to_dict(), args.json, action.render())
    return 0


def cmd_workflows(args) -> int:
    from .orchestrator import workflows as workflows_mod
    rows = workflows_mod.available()
    if args.json:
        _print(rows, True)
        return 0
    for workflow in rows:
        print(f"{workflow['name']:16} {workflow['tasks']:>2} tasks  needs {workflow['variables']}")
        print(f"{'':16} {workflow['description'][:96]}")
    print(f"\n{len(rows)} workflow(s) in {workflows_mod.directory()}")
    print("use one: argus plan <engagement> --workflow <name> --var target=http://...")
    return 0


def cmd_plan(args) -> int:
    from .orchestrator import planner as planner_mod
    from .orchestrator.router import Router
    if args.workflow:
        from .orchestrator import workflows as workflows_mod
        variables = dict(item.split("=", 1) for item in (args.var or []) if "=" in item)
        plan = workflows_mod.instantiate(args.engagement, args.workflow, variables)
        _print(plan, args.json, planner_mod.render(plan))
        return 0
    if args.deterministic:
        plan = planner_mod.deterministic_plan(args.engagement)
        _print(plan, args.json, planner_mod.render(plan))
        return 0
    from .runtime import credentials, profile as profile_mod, providers
    router = Router(policy=args.policy)
    route = router.route({"id": "plan", "kind": "plan", "model": args.model or ""})
    if not route.model:
        print(f"no planner model is reachable: {route.reason}\n"
              f"falling back to the deterministic plan, which is the baseline anyway.")
        plan = planner_mod.deterministic_plan(args.engagement, note="no planner model reachable")
        _print(plan, args.json, planner_mod.render(plan))
        return 0
    model_profile = route.profile or profile_mod.load(route.model)
    provider_name = model_profile.provider
    kwargs: dict = {}
    if provider_name == "opencode":
        kwargs = {"model_prefix": (model_profile.opencode_name or "").split("/")[0]}
    elif model_profile.family == "claude" and not credentials.get("anthropic"):
        provider_name = "claude_cli"
    provider = providers.get(provider_name, **kwargs)
    print(f"planning with {route.model} via {provider_name} ({route.reason})", file=sys.stderr)
    outcome = planner_mod.plan_with_model(args.engagement, provider, route.model,
                                          profile=model_profile, extra=args.notes or "")
    for problem in outcome.problems:
        print(f"  validation: {problem}", file=sys.stderr)
    if not outcome.ok:
        print("the model plan did not survive validation; writing the deterministic plan instead",
              file=sys.stderr)
        plan = planner_mod.deterministic_plan(args.engagement,
                                              note=f"model plan rejected: {outcome.problems[:2]}")
        _print(plan, args.json, planner_mod.render(plan))
        return 1
    print(f"plan cost ${outcome.cost_usd:.4f}", file=sys.stderr)
    _print(outcome.plan, args.json, planner_mod.render(outcome.plan))
    return 0


def cmd_run(args) -> int:
    from .orchestrator.scheduler import Scheduler
    scheduler = Scheduler(args.engagement, policy=args.policy, parallelism=args.parallelism,
                          dry_run=args.dry_run, max_tasks=args.max_tasks,
                          task_timeout=args.task_timeout)
    summary = scheduler.run(expand=not args.no_expand)
    _print(summary.to_dict(), args.json, summary.render())
    return 0


def cmd_agent(args) -> int:
    from .runtime import profile as profile_mod
    from .runtime.loop import Harness
    model_profile = profile_mod.load(args.model)
    provider = args.provider or model_profile.provider
    # The billing route is in the profile; deriving it here means `argus agent`
    # does not need the prefix spelled out, the way the orchestrator's runner
    # already does not.
    prefix = args.opencode_prefix or (model_profile.opencode_name or "").split("/")[0]
    kwargs = {"model_prefix": prefix} if provider == "opencode" and prefix else None
    harness = Harness(args.engagement, args.model, provider=provider,
                      provider_kwargs=kwargs)
    result = harness.run(task=args.task or "", max_steps=args.max_steps)
    _print(result.to_dict(), args.json, result.render())
    return 0


def cmd_verify(args) -> int:
    from .orchestrator import verify as verify_mod
    results = ([verify_mod.verify_finding(args.engagement, args.finding, policy=args.policy)]
               if args.finding else verify_mod.verify_all(args.engagement, policy=args.policy))
    if not results:
        print("nothing to verify: no confirmed finding is missing a cross-check")
        return 0
    for verification in results:
        if args.json:
            print(json.dumps(verification.to_dict(), ensure_ascii=False))
        else:
            mark = "agrees" if verification.agrees else "DISAGREES"
            print(f"{verification.finding_id} — {verification.verifier}: {mark}")
            print(f"  {verification.reason or verification.error}")
            if verification.missing:
                print(f"  would settle it: {verification.missing}")
    return 0


def cmd_report(args) -> int:
    if args.write:
        path = report_mod.write(args.engagement)
        print(path)
    else:
        print(report_mod.render(args.engagement))
    return 0


def cmd_mcp(args) -> int:
    from .broker.serve import main as serve_main
    argv = list(args.servers or ["all"])
    if args.engagement:
        argv += ["--engagement", args.engagement]
    if args.list:
        argv += ["--list"]
    return serve_main(argv)


def cmd_tools(args) -> int:
    from .broker.serve import merge
    from .broker.servers import SERVER_NAMES
    server = merge(list(SERVER_NAMES))
    rows = [{"name": spec.name, "tier": spec.tier,
             "touches_target": spec.touches_target, "proves": spec.proves,
             "step": spec.step, "requires": list(spec.requires),
             "summary": spec.description.strip().splitlines()[0]}
            for spec in server.tools.values()]
    if args.json:
        _print(rows, True)
        return 0
    print(f"{'tool':26} {'tier':10} {'where':7} {'proves':18} summary")
    for row in rows:
        print(f"{row['name']:26} {row['tier']:10} "
              f"{'target' if row['touches_target'] else 'local':7} "
              f"{(row['proves'] or '-'):18} {row['summary'][:64]}")
    print(f"\n{len(rows)} tools")
    return 0


def cmd_fleet(args) -> int:
    from .orchestrator.router import ROLE_FOR_KIND, Router
    from .runtime import profile as profile_mod
    router = Router(policy=args.policy)
    availability = router.availability.to_dict()
    if args.json:
        _print({"availability": availability,
                "routes": {kind: router.route({"id": kind, "kind": kind}).to_dict()
                           for kind in ROLE_FOR_KIND},
                "profiles": {model: profile_mod.load(model).to_dict()
                             for model in profile_mod.known()}}, True)
        return 0
    print("what can run here:")
    for key, value in availability.items():
        print(f"  {key}: {value}")
    from .orchestrator import openbot as openbot_mod
    print("\nopenbot, the coordination plane:")
    ready, why = openbot_mod.automation_ready()
    print(f"  control server: {'up at ' + why if ready else 'down — ' + why}")
    registered = openbot_mod.mcp_servers_in_db()
    argus_server = [row for row in registered if "argus" in row["name"].lower()]
    print(f"  argus registered as an mcp server: "
          f"{'yes, enabled' if argus_server and argus_server[0]['enabled'] else 'no'}"
          f"{'' if registered else ' (no mcp server is registered at all)'}")
    known = openbot_mod.agents_in_db()
    dispatchable = {agent.id for agent in openbot_mod.Fleet().list_agents()} if ready else set()
    if not known:
        print("  agents: none in the app's store")
    for agent in known:
        print(f"  agent {agent.name:22} {agent.model:34} "
              f"argus={agent.argus_model or '(no profile)':16} "
              f"{'dispatchable' if agent.id in dispatchable else 'Local scripts off'} "
              f"roles={','.join(agent.roles()) or '-'}")
    print(f"\nrouting under the {args.policy} policy:")
    print(f"  {'kind':10} {'runner':9} {'model':24} {'family':9} est.$")
    for kind in ROLE_FOR_KIND:
        route = router.route({"id": kind, "kind": kind})
        print(f"  {kind:10} {route.runner:9} {route.model or '-':24} {route.family or '-':9} "
              f"{route.estimated_cost_usd:6.3f}")
    return 0


def cmd_proof(args) -> int:
    if not args.vuln_class:
        rows = [(name, matrix.spec_for(name)) for name in matrix.classes()]
        if args.json:
            _print([{"vuln_class": name, "kind": spec.kind, "severity": spec.severity,
                     "requirement": spec.requirement,
                     "required_checks": list(spec.required_checks)} for name, spec in rows], True)
            return 0
        for name, spec in rows:
            print(f"{name:18} {spec.kind:18} {spec.requirement}")
        return 0
    spec = matrix.spec_for(args.vuln_class)
    if spec is None:
        print(f"{args.vuln_class!r} is not in the proof matrix. Known: {matrix.classes()}")
        return 1
    from .knowledge import playbook
    print(f"{spec.vuln_class} ({spec.kind}, default severity {spec.severity})\n")
    print(f"requirement: {spec.requirement}\n")
    print("required checks:")
    for check in spec.required_checks:
        print(f"  - {check}")
    if spec.benign_proof:
        print(f"\nproof command: {spec.benign_proof}")
    if spec.notes:
        print(f"\nnote: {spec.notes}")
    if spec.refusal:
        print(f"\nREFUSED: {spec.refusal}")
    ladder = playbook.ladder(spec.vuln_class)
    if ladder:
        print("\nladder:")
        for index, step in enumerate(ladder, 1):
            print(f"  {index}. {step['step']:22} [{step['tier']:9}] {step['tool']:22} {step['why']}")
    return 0


def cmd_metrics(args) -> int:
    from .orchestrator import metrics as metrics_mod
    data = metrics_mod.collect(args.engagement)
    _print(data, args.json, metrics_mod.render(data))
    return 0


def cmd_engagements(args) -> int:
    rows = []
    for directory in sorted(config.ENGAGEMENTS.glob("*/state.json")):
        try:
            state = State.load(directory.parent.name)
        except (FileNotFoundError, ValueError):
            continue
        digest = state.digest()
        rows.append({"engagement": digest["engagement"], "status": digest["status"],
                     "targets": len(digest["targets"]), "probes": digest["probes"]["total"],
                     "findings": len(digest["findings"]),
                     "confirmed": len([f for f in state.data["findings"]
                                       if f.get("status") == "confirmed"]),
                     "updated": state.data["updated"]})
    if args.json:
        _print(rows, True)
        return 0
    print(f"{'engagement':24} {'status':8} {'targets':>7} {'probes':>6} "
          f"{'findings':>8} {'confirmed':>9}  updated")
    for row in rows:
        print(f"{row['engagement']:24} {row['status']:8} {row['targets']:>7} {row['probes']:>6} "
              f"{row['findings']:>8} {row['confirmed']:>9}  {row['updated']}")
    return 0


def cmd_gate(args) -> int:
    from .broker import exec as ex
    result = ex.run(["bash", str(config.ROOT / "test" / "run_all.sh")], timeout=1800)
    print(result.stdout)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr)
    return result.exit_code or 0


# --- parser ------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="argus", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    open_parser = subparsers.add_parser("open", help="start an engagement")
    open_parser.add_argument("engagement")
    open_parser.add_argument("--objective", default="")
    open_parser.add_argument("--in-scope", nargs="*", dest="in_scope",
                             help="hosts, CIDRs, *.wildcards or URL prefixes")
    open_parser.add_argument("--out-of-scope", nargs="*", dest="out_of_scope")
    open_parser.add_argument("--ports", nargs="*")
    open_parser.add_argument("--tiers", nargs="*", default=["passive", "active"],
                             choices=list(config.TIERS))
    open_parser.add_argument("--authorisation", default=None,
                             help="who authorised this, and over what window")
    open_parser.add_argument("--resolve", action="store_true",
                             help="also check resolved addresses against the scope")
    open_parser.set_defaults(func=cmd_open)

    target_parser = subparsers.add_parser("target", help="admit a target")
    target_parser.add_argument("engagement")
    target_parser.add_argument("target")
    target_parser.add_argument("--note", default="")
    target_parser.set_defaults(func=cmd_target)

    status_parser = subparsers.add_parser("status", help="the ledger, compactly")
    status_parser.add_argument("engagement")
    status_parser.set_defaults(func=cmd_status)

    next_parser = subparsers.add_parser("next", help="the controller's next action")
    next_parser.add_argument("engagement")
    next_parser.set_defaults(func=cmd_next)

    plan_parser = subparsers.add_parser("plan", help="write a plan")
    plan_parser.add_argument("engagement")
    plan_parser.add_argument("--deterministic", action="store_true",
                             help="the baseline plan, no model consulted")
    plan_parser.add_argument("--model", default=None, help="pin the planner model")
    plan_parser.add_argument("--policy", default="balanced",
                             choices=("quality", "balanced", "cheap"))
    plan_parser.add_argument("--workflow", default=None,
                             help="instantiate a shipped workflow instead of planning")
    plan_parser.add_argument("--var", action="append", default=[],
                             help="workflow variable, k=v, repeatable")
    plan_parser.add_argument("--notes", default="", help="operator notes for the planner")
    plan_parser.set_defaults(func=cmd_plan)

    run_parser = subparsers.add_parser("run", help="execute the plan across the fleet")
    run_parser.add_argument("engagement")
    run_parser.add_argument("--policy", default="balanced",
                            choices=("quality", "balanced", "cheap"))
    run_parser.add_argument("--parallelism", type=int, default=3)
    run_parser.add_argument("--max-tasks", type=int, default=40)
    run_parser.add_argument("--task-timeout", type=int, default=1800)
    run_parser.add_argument("--dry-run", action="store_true",
                            help="route and brief every task, call no model")
    run_parser.add_argument("--no-expand", action="store_true")
    run_parser.set_defaults(func=cmd_run)

    agent_parser = subparsers.add_parser("agent", help="one model, one loop")
    agent_parser.add_argument("engagement")
    agent_parser.add_argument("--model", required=True)
    agent_parser.add_argument("--provider", default=None)
    agent_parser.add_argument("--opencode-prefix", default=None,
                              help="e.g. deepseek, google, opencode-go")
    agent_parser.add_argument("--task", default="")
    agent_parser.add_argument("--max-steps", type=int, default=None)
    agent_parser.set_defaults(func=cmd_agent)

    verify_parser = subparsers.add_parser("verify", help="cross-family verification")
    verify_parser.add_argument("engagement")
    verify_parser.add_argument("--finding", default=None)
    verify_parser.add_argument("--policy", default="balanced")
    verify_parser.set_defaults(func=cmd_verify)

    report_parser = subparsers.add_parser("report", help="render the report")
    report_parser.add_argument("engagement")
    report_parser.add_argument("--write", action="store_true")
    report_parser.set_defaults(func=cmd_report)

    mcp_parser = subparsers.add_parser("mcp", help="serve the tool plane over MCP stdio")
    mcp_parser.add_argument("servers", nargs="*", default=["all"])
    mcp_parser.add_argument("--engagement", default=None)
    mcp_parser.add_argument("--list", action="store_true")
    mcp_parser.set_defaults(func=cmd_mcp)

    tools_parser = subparsers.add_parser("tools", help="the tool table")
    tools_parser.set_defaults(func=cmd_tools)

    fleet_parser = subparsers.add_parser("fleet", help="what can run here, and the routing table")
    fleet_parser.add_argument("--policy", default="balanced",
                              choices=("quality", "balanced", "cheap"))
    fleet_parser.set_defaults(func=cmd_fleet)

    proof_parser = subparsers.add_parser("proof", help="what a class must produce")
    proof_parser.add_argument("vuln_class", nargs="?", default=None)
    proof_parser.set_defaults(func=cmd_proof)

    metrics_parser = subparsers.add_parser("metrics",
                                           help="what the engagement cost and what it bought")
    metrics_parser.add_argument("engagement")
    metrics_parser.set_defaults(func=cmd_metrics)

    workflows_parser = subparsers.add_parser("workflows", help="list the shipped workflows")
    workflows_parser.set_defaults(func=cmd_workflows)

    engagements_parser = subparsers.add_parser("engagements", help="list engagements")
    engagements_parser.set_defaults(func=cmd_engagements)

    gate_parser = subparsers.add_parser("gate", help="run the test suite")
    gate_parser.set_defaults(func=cmd_gate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as error:
        print(f"{error}", file=sys.stderr)
        return 2
    except (ValueError, KeyError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted; the ledger is on disk and the engagement can be resumed",
              file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
