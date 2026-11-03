"""Default-deny scope.

Every command the broker runs passes through here first, so an LLM that
hallucinates a hostname cannot reach it. Three properties matter:

* **default deny** — an empty allowlist allows nothing, not everything.
* **deny wins** — an out-of-scope rule beats any in-scope rule that also matches.
* **no silent widening** — a redirect, a rewritten Host header or a resolved
  CNAME is a new target and is checked again, not inherited from the first.

Rule forms, in both lists:

    example.com            exact host
    *.example.com          host and any subdomain
    10.0.0.0/24            CIDR, v4 or v6
    192.168.1.10           literal address
    http://host/app/       URL prefix (scheme+host+path prefix)
    host:8080              host with one port

Known limit, stated rather than hidden: a rule names what was written, not what
DNS answers. `resolve=True` additionally checks the resolved addresses, and an
engagement that cares about rebinding must enable it.
"""
from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    target: str
    reason: str
    rule: str | None = None

    def __bool__(self) -> bool:
        return self.allowed


@dataclass
class Target:
    raw: str
    scheme: str = ""
    host: str = ""
    port: int | None = None
    path: str = "/"
    ip: ipaddress._BaseAddress | None = None

    @property
    def is_ip(self) -> bool:
        return self.ip is not None


def parse_target(raw: str) -> Target:
    """Accept a URL, host, host:port or bare address. One parser, used by all."""
    text = (raw or "").strip()
    if not text:
        raise ValueError("empty target")
    if "://" in text:
        parts = urlsplit(text)
        scheme, host, path = parts.scheme.lower(), (parts.hostname or "").lower(), parts.path or "/"
        port = parts.port
    else:
        scheme, path = "", "/"
        head = text.split("/", 1)
        if len(head) == 2 and head[1]:
            path = "/" + head[1]
        hostport = head[0]
        if hostport.startswith("["):                       # [::1]:8080
            closing = hostport.find("]")
            host = hostport[1:closing].lower()
            rest = hostport[closing + 1:]
            port = int(rest[1:]) if rest.startswith(":") and rest[1:].isdigit() else None
        elif hostport.count(":") == 1:
            host, _, tail = hostport.partition(":")
            host = host.lower()
            port = int(tail) if tail.isdigit() else None
        else:
            host, port = hostport.lower(), None
    if not host:
        raise ValueError(f"no host in target {raw!r}")
    address = None
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    if port is None and scheme in ("http", "https"):
        port = 80 if scheme == "http" else 443
    return Target(raw=text, scheme=scheme, host=host, port=port, path=path, ip=address)


def _rule_matches(rule: str, target: Target) -> bool:
    rule = rule.strip()
    if not rule:
        return False
    if "://" in rule:                                      # URL prefix
        parsed = urlsplit(rule)
        if (parsed.hostname or "").lower() != target.host:
            return False
        if parsed.port and target.port and parsed.port != target.port:
            return False
        prefix = parsed.path or "/"
        return target.path.startswith(prefix) or prefix == "/"
    if "/" in rule:                                        # CIDR
        try:
            network = ipaddress.ip_network(rule, strict=False)
        except ValueError:
            return False
        if target.ip is not None:
            return target.ip in network
        return False
    port_rule = None
    host_rule = rule.lower()
    if host_rule.count(":") == 1 and host_rule.rsplit(":", 1)[1].isdigit():
        host_rule, _, tail = host_rule.rpartition(":")
        port_rule = int(tail)
    if port_rule is not None and target.port is not None and port_rule != target.port:
        return False
    try:                                                   # literal address rule
        if ipaddress.ip_address(host_rule) and target.ip is not None:
            return ipaddress.ip_address(host_rule) == target.ip
    except ValueError:
        pass
    if host_rule.startswith("*."):
        suffix = host_rule[1:]                             # ".example.com"
        return target.host == host_rule[2:] or target.host.endswith(suffix)
    return target.host == host_rule


def origin_of(raw: str) -> str:
    """scheme://host:port, which is the unit a probe budget is counted against.

    Budgets used to key on the target string the tool was called with. Every
    payload variant carries a different query string, so a sixth variant of the
    same idea looked like a first probe against a new target and the brake never
    engaged. The origin is what the tester is actually spending time on.
    """
    try:
        target = parse_target(raw)
    except ValueError:
        return str(raw)
    scheme = target.scheme or ("https" if target.port == 443 else "http")
    return f"{scheme}://{target.host}" + (f":{target.port}" if target.port else "")


@dataclass
class Scope:
    in_scope: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    allowed_ports: list[int] = field(default_factory=list)
    resolve: bool = False

    @classmethod
    def from_dict(cls, data: dict | None) -> "Scope":
        data = data or {}
        return cls(
            in_scope=[str(x) for x in data.get("in_scope", [])],
            out_of_scope=[str(x) for x in data.get("out_of_scope", [])],
            allowed_ports=[int(x) for x in data.get("allowed_ports", [])],
            resolve=bool(data.get("resolve", False)),
        )

    def to_dict(self) -> dict:
        return {
            "in_scope": self.in_scope,
            "out_of_scope": self.out_of_scope,
            "allowed_ports": self.allowed_ports,
            "resolve": self.resolve,
        }

    def check(self, raw: str) -> Verdict:
        try:
            target = parse_target(raw)
        except ValueError as error:
            return Verdict(False, str(raw), f"unparsable target: {error}")
        if not self.in_scope:
            return Verdict(False, target.raw, "scope is empty, and an empty scope allows nothing")
        for rule in self.out_of_scope:
            if _rule_matches(rule, target):
                return Verdict(False, target.raw, "matched an out-of-scope rule", rule)
        if self.allowed_ports and target.port is not None and target.port not in self.allowed_ports:
            return Verdict(False, target.raw, f"port {target.port} is not in allowed_ports")
        hit = next((rule for rule in self.in_scope if _rule_matches(rule, target)), None)
        if hit is None:
            return Verdict(False, target.raw, "matched no in-scope rule")
        if self.resolve and not target.is_ip:
            for address in self._resolve(target.host):
                probe = Target(raw=address, host=address, port=target.port, path=target.path,
                               ip=ipaddress.ip_address(address))
                for rule in self.out_of_scope:
                    if _rule_matches(rule, probe):
                        return Verdict(False, target.raw,
                                       f"host resolves to {address}, which an out-of-scope rule covers", rule)
                if not any(_rule_matches(rule, probe) for rule in self.in_scope):
                    return Verdict(False, target.raw,
                                   f"host resolves to {address}, which no in-scope rule covers")
        return Verdict(True, target.raw, "matched an in-scope rule", hit)

    @staticmethod
    def _resolve(host: str) -> list[str]:
        try:
            infos = socket.getaddrinfo(host, None)
        except OSError:
            return []
        return sorted({info[4][0] for info in infos})
