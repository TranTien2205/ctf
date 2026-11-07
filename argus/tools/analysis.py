"""Analysis + bookkeeping tools: jwt, skills, notes, findings, external, finish."""
from __future__ import annotations

import base64
import hashlib
import hmac as _hmac
import json
import os
import re
import shutil
import subprocess
import urllib.parse
from pathlib import Path

from ..scope import ScopeError
from .registry import Context

# ---------------------------------------------------------------- jwt

_COMMON_SECRETS = [
    "secret", "secret123", "password", "changeme", "key", "private", "admin",
    "test", "dev", "12345", "jwtsecret", "your-256-bit-secret", "supersecret",
    "HS256", "hmac", "default", "letmein", "qwerty", "argus",
]


def _b64url(part: str) -> bytes:
    pad = "=" * (-len(part) % 4)
    return base64.urlsafe_b64decode(part + pad)


def jwt_decode(ctx: Context, token: str) -> dict:
    token = token.strip().strip('"\'')
    parts = token.split(".")
    if len(parts) not in (2, 3):
        return {"error": "not a JWT (expected 2 or 3 segments)"}
    try:
        header = json.loads(_b64url(parts[0]))
        payload = json.loads(_b64url(parts[1]))
    except (ValueError, json.JSONDecodeError) as exc:
        return {"error": f"decode failed: {exc}"}
    out: dict = {"header": header, "payload": payload}
    alg = (header.get("alg") or "").lower()
    issues = []
    if alg == "none":
        issues.append("alg=none token presented - try dropping the signature")
    if alg.startswith("hs") and len(parts) == 3:
        signing_input = f"{parts[0]}.{parts[1]}".encode()
        sig = _b64url(parts[2])
        algo = {"hs256": hashlib.sha256, "hs384": hashlib.sha384,
                "hs512": hashlib.sha512}[alg]
        for secret in _COMMON_SECRETS:
            cand = _hmac.new(secret.encode(), signing_input, algo).digest()
            if _hmac.compare_digest(cand, sig):
                issues.append(f"weak HMAC secret recovered offline: {secret!r}")
                out["recovered_secret"] = secret
                break
    if alg.startswith("rs") or alg.startswith("es"):
        issues.append(f"{alg}: check for alg-confusion (RS256->HS256 with public key) and jku/kid injection")
    exp = payload.get("exp")
    if exp:
        import time
        out["expired"] = exp < time.time()
    out["issues"] = issues or ["no obvious weakness; need the signing key or a confused verifier"]
    return out


# ---------------------------------------------------------------- skills

def load_skill(ctx: Context, name: str) -> dict:
    skills_dir = Path(ctx.skills_dir)
    if name.strip().lower() in ("index", "list", ""):
        index = skills_dir / "INDEX.md"
        listing = sorted(p.stem for p in skills_dir.glob("*.md") if p.name != "INDEX.md")
        return {"available": listing,
                "index": index.read_text(encoding="utf-8") if index.exists() else ""}
    safe = re.sub(r"[^a-z0-9_-]", "", name.lower())
    path = skills_dir / f"{safe}.md"
    if not path.exists():
        return {"error": f"no skill named {name!r}; call load_skill('index')"}
    return {"skill": safe, "content": path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- notes

def note(ctx: Context, text: str) -> dict:
    ctx.session.note(text)
    return {"ok": True}


def read_notes(ctx: Context) -> dict:
    return {"notes": ctx.session.notes_path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- findings

def record_finding(ctx: Context, title: str, severity: str, category: str,
                   url: str, evidence_excerpt: str,
                   description: str, remediation: str,
                   evidence_ids: list[str] | None = None) -> dict:
    finding = ctx.session.add_finding(
        title=title, severity=severity, category=category, url=url,
        evidence_ids=list(evidence_ids or []),
        evidence_excerpt=evidence_excerpt, description=description,
        remediation=remediation, agent=ctx.agent_name,
    )
    return {"recorded": finding["id"], "title": finding["title"],
            "severity": finding["severity"]}


# ---------------------------------------------------------------- external

_ALLOWED_TOOLS = {"sqlmap", "nuclei", "nmap", "ffuf", "curl"}
_URL_RE = re.compile(r"https?://[^\s'\"]+")
_HOST_RE = re.compile(
    r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?")


def run_external(ctx: Context, tool: str, args: str, timeout_s: int = 120) -> dict:
    if not ctx.cfg.external_tools:
        return {"error": "external tools disabled (--no-external)"}
    tool = tool.strip().lower()
    if tool not in _ALLOWED_TOOLS:
        return {"error": f"tool {tool!r} not allowed; allowed: {sorted(_ALLOWED_TOOLS)}"}
    binary = shutil.which(tool)
    if not binary:
        return {"error": f"{tool} is not installed on this host"}
    for u in _URL_RE.findall(args):
        ctx.scope.check(u)  # raises ScopeError -> returned as error
    # bare hostnames/IPs as arguments (e.g. `nmap evil.com`) must also be
    # in scope; flags and existing filenames are skipped
    for tok in _split_args(args):
        if tok.startswith("-") or Path(tok).exists() or os.sep in tok:
            continue
        host_part = tok.split(":")[0]
        if re.search(r"\.(?:txt|xml|json|html?|list|lst|md|csv|out|log|yaml|yml|py|sh|gz|zip)$",
                     host_part, re.I):
            continue  # file-like, not a hostname
        if _HOST_RE.fullmatch(host_part):
            ctx.scope.check("http://" + host_part)
    toks = _split_args(args)
    check = _ARG_CHECKS.get(tool)
    if check:
        bad = check(ctx, toks)
        if bad:
            return {"error": bad}
    timeout_s = max(5, min(int(timeout_s or 120), 600))
    cmd = [binary] + _split_args(args)
    rid = ctx.session.record_event("external_cmd", {"cmd": cmd})
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_s, errors="replace")
        output = (proc.stdout or "") + ("\n[stderr]\n" + proc.stderr if proc.stderr else "")
        ctx.session.record_event("external_result", {
            "cmd_id": rid, "returncode": proc.returncode,
            "output": output[:50_000]})
        return {"cmd_id": rid, "returncode": proc.returncode,
                "output": output[-20_000:],
                "note": "scanner output is a lead; verify with http_request before record_finding"}
    except subprocess.TimeoutExpired:
        ctx.session.record_event("external_result", {"cmd_id": rid, "timeout": timeout_s})
        return {"cmd_id": rid, "error": f"timed out after {timeout_s}s"}


# ---------------------------------------------------------------- arg guards
# The URL/host scan above only sees ARGUMENTS. Each allowlisted tool has
# flags that pull data from other channels - local files (exfil to the
# target or into the transcript), files full of targets (scope bypass),
# connection redirection (--resolve/--connect-to/proxies), and local code
# execution (sqlmap --eval, nmap --script ./x.nse). Close them per tool.


def _flag_value(toks: list[str], i: int) -> str:
    """value of toks[i]: inline after '=' or the next token."""
    _, eq, inline = toks[i].partition("=")
    return inline if eq else (toks[i + 1] if i + 1 < len(toks) else "")


def _bare_filename(val: str) -> bool:
    """only a plain filename is a safe write destination: '/x' is relative
    on Windows' Path but absolute on POSIX, 'C:\\x' the reverse - a name
    equal to itself under both parsers has no separators and no drive."""
    from pathlib import PurePosixPath, PureWindowsPath
    return bool(val) and PurePosixPath(val).name == val \
        and PureWindowsPath(val).name == val


def _rel_path_ok(val: str) -> bool:
    """relative path with no '..' escape under either platform's rules."""
    from pathlib import PurePosixPath, PureWindowsPath
    for pure in (PurePosixPath, PureWindowsPath):
        p = pure(val)
        if p.is_absolute() or getattr(p, "drive", "") or ".." in p.parts:
            return False
    return bool(val)


def _file_target_hosts(path: Path) -> set[str]:
    """host-like tokens inside a local file: URLs, Host: headers of raw
    requests (sqlmap -r), and bare host lines (nmap -iL, nuclei -l)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    hosts = set(_URL_RE.findall(text))
    for m in re.findall(r"(?im)^\s*host:\s*(\S+)", text):
        hosts.add("http://" + m.rsplit(":", 1)[0].strip("[]"))
    for line in text.splitlines():
        first = line.strip().split()[0] if line.strip() else ""
        host = first.split(":")[0]
        if host and not host.startswith("#") and _HOST_RE.fullmatch(host):
            hosts.add("http://" + host)
    return hosts


def _file_target_check(ctx: Context, toks: list[str],
                       flags: set[str]) -> str | None:
    """flags that name a FILE OF TARGETS (nmap -iL, sqlmap -r/-l/-m,
    nuclei -l) bypass the arg scan - verify every host inside the file."""
    for i, tok in enumerate(toks):
        if tok.partition("=")[0] not in flags:
            continue
        val = _flag_value(toks, i)
        path = Path(val)
        if not path.exists():
            return f"{tok.partition('=')[0]} file not found: {val}"
        for h in _file_target_hosts(path):
            try:
                ctx.scope.check(h)
            except Exception as exc:
                return f"target file host out of scope: {h} ({exc})"
    return None


# curl ---------------------------------------------------------------------
# value semantics per flag:
#   -d @file  |  -F name=@file or name=<file  |  --data-urlencode name@file
#   -b <file> |  -w @file  |  -K <file with any options>
# (--form-string never interprets @, so it is left out deliberately.)
_CURL_DATA_FLAGS = {"-d", "--data", "--data-raw", "--data-binary",
                    "--data-ascii"}
_CURL_FORM_FLAGS = {"-F", "--form"}
_CURL_URLENC_FLAGS = {"--data-urlencode"}
# option injection, connection redirection out of scope, credential reads
_CURL_BLOCK = {
    "-K", "--config", "-n", "--netrc", "--netrc-file", "--netrc-optional",
    "-T", "--upload-file",
    "-x", "--proxy", "--proxy-user", "--proxy-header", "--proxytunnel",
    "-p", "--preproxy", "--socks4", "--socks4a", "--socks5",
    "--socks5-hostname", "--socks5-gssapi",
    "--resolve", "--connect-to", "--interface",
    "--unix-socket", "--abstract-unix-socket",
    "--alt-svc", "--hsts",
}
# write a file: confined to a bare filename in cwd
_CURL_WRITE = {
    "-o", "--output", "-D", "--dump-header", "-c", "--cookie-jar",
    "--trace", "--trace-ascii", "--stderr", "--etag-save",
}
# short options that consume a value - everything after the letter inside
# a bundle is its value, not more flags; no-arg toggles keep parsing.
_CURL_TAKES_VALUE = set("AbCcdDeEFHKmoQrTtuUwxXyz")
# no-arg toggles that are dangerous wherever they appear in a bundle:
# -n reads ~/.netrc, -p is --proxytunnel.
_CURL_BAD_TOGGLE = set("np")


def _curl_arg_check(ctx: Context, toks: list[str]) -> str | None:
    """curl can smuggle LOCAL FILES to the target: -d @/etc/passwd,
    -F f=@config, -T secret, -b cookiejar. It can also redirect the
    connection while the URL looks in-scope (--resolve/--connect-to/-x)
    and read option files that re-enable everything above (-K).
    Bundled shorts like '-sK cfg' are parsed flag by flag."""
    for i, tok in enumerate(toks):
        if not tok.startswith("-") or tok == "-":
            continue
        flag = tok.partition("=")[0]
        if flag in _CURL_BLOCK:
            return f"curl {flag} is disabled"
        val = _flag_value(toks, i)
        if flag in _CURL_WRITE and not _bare_filename(val):
            return f"curl {flag} must be a plain filename inside cwd"
        if flag in _CURL_DATA_FLAGS and val.startswith("@"):
            return f"curl {flag} @file is disabled (local file exfil)"
        if flag in _CURL_FORM_FLAGS:
            content = val.split("=", 1)[1] if "=" in val else val
            if content.startswith(("@", "<")):
                return f"curl {flag} file reference is disabled " \
                       "(local file exfil)"
        if flag in _CURL_URLENC_FLAGS and "@" in val:
            return "curl --data-urlencode @file is disabled " \
                   "(local file exfil)"
        if flag in ("-b", "--cookie") and "=" not in val:
            return "curl -b reads a cookie FILE unless the value " \
                   "contains '='; use -b name=value"
        if flag in ("-w", "--write-out") and val.startswith("@"):
            return "curl -w @file is disabled (local file read)"
        if tok.startswith("--") or len(tok) < 2:
            continue
        # bundled/attached short options: '-sd@x' is -s + -d with value
        # '@x'; a letter that takes a value swallows the rest of the tok
        j = 1
        while j < len(tok):
            c = tok[j]
            if c in _CURL_BAD_TOGGLE:
                return f"curl -{c} is disabled"
            if c not in _CURL_TAKES_VALUE:
                j += 1
                continue
            rest = tok[j + 1:] or val
            if c in "KTxU":
                return f"curl -{c} is disabled"
            if c == "d" and rest.startswith("@"):
                return "curl -d @file is disabled (local file exfil)"
            if c == "F":
                content = rest.split("=", 1)[1] if "=" in rest else rest
                if content.startswith(("@", "<")):
                    return "curl -F file reference is disabled " \
                           "(local file exfil)"
            if c == "b" and "=" not in rest:
                return "curl -b file is disabled (local file read)"
            if c == "w" and rest.startswith("@"):
                return "curl -w @file is disabled (local file read)"
            if c in "oDc" and not _bare_filename(rest):
                return f"curl -{c} must be a plain filename inside cwd"
            break  # the value consumed the remainder of this token
    return None


# nmap ---------------------------------------------------------------------
def _nmap_arg_check(ctx: Context, toks: list[str]) -> str | None:
    """-iL reads targets from a file (scope-check its contents); --script
    with a path runs arbitrary Lua (local code exec); -o* writes must not
    leave cwd; -iR scans random internet hosts by definition."""
    bad = _file_target_check(ctx, toks, {"-iL"})
    if bad:
        return bad
    for i, tok in enumerate(toks):
        flag = tok.partition("=")[0]
        if tok.startswith("-iR") or flag in {
                "--resume", "--datadir", "--servicedb", "--versiondb",
                "--stylesheet", "--proxies"}:
            return f"nmap {flag if flag.startswith('--') else '-iR'} " \
                   "is disabled"
        if flag in {"-oN", "-oX", "-oS", "-oG", "-oA"} and \
                not _bare_filename(_flag_value(toks, i)):
            return f"nmap {flag} must be a plain filename inside cwd"
        if flag == "--script":
            val = _flag_value(toks, i)
            for piece in val.split(","):
                if "/" in piece or "\\" in piece or ".." in piece \
                        or Path(piece).exists():
                    return "nmap --script only accepts built-in " \
                           "script names/categories, not paths"
    return None


# ffuf ---------------------------------------------------------------------
def _ffuf_arg_check(ctx: Context, toks: list[str]) -> str | None:
    """-w list:FUZZ sends every line of the file to the target - a local
    file is exfiltrated word by word. Confine wordlists to
    resources/wordlists/ or files inside cwd."""
    wroot = (Path(__file__).resolve().parents[2]
             / "resources" / "wordlists")
    for i, tok in enumerate(toks):
        flag = tok.partition("=")[0]
        if flag in {"-x", "--proxy", "-replay-proxy"}:
            return f"ffuf {flag} is disabled (proxy leaves scope)"
        if flag in {"-w", "--wordlist"}:
            val = _flag_value(toks, i)
            p = Path(val.split(":")[0])
            if not p.exists():  # may be file:KEYWORD with a drive letter
                p = Path(val.rsplit(":", 1)[0])
            ok = False
            if p.exists():
                real = p.resolve()
                ok = wroot.exists() and real.is_relative_to(wroot.resolve()) \
                    or real.is_relative_to(Path.cwd().resolve())
            if not ok:
                return "ffuf -w must point inside resources/wordlists " \
                       "or the working directory (local file exfil)"
        if flag in {"-of", "-o", "-od", "-or"} and \
                not _rel_path_ok(_flag_value(toks, i)):
            return f"ffuf {flag} must stay inside the working directory"
    return None


# sqlmap -------------------------------------------------------------------
def _sqlmap_arg_check(ctx: Context, toks: list[str]) -> str | None:
    """--eval runs Python on THIS machine; -d connects to an arbitrary
    DBMS host outside scope; -r/-l/-m read targets from files; --tamper
    loads scripts by path; -c injects options like curl -K."""
    bad = _file_target_check(
        ctx, toks, {"-r", "-l", "-m", "-x", "--bulk-file"})
    if bad:
        return bad
    for i, tok in enumerate(toks):
        flag = tok.partition("=")[0]
        if flag in {"--eval", "-c", "--config-file", "--dependencies",
                    "--update", "--purge", "--sqlmap-shell", "--msf-path",
                    "-d", "--direct", "--proxy", "--tor", "--check-tor"}:
            return f"sqlmap {flag} is disabled"
        if flag == "--tamper":
            val = _flag_value(toks, i)
            if "/" in val or "\\" in val or ".." in val:
                return "sqlmap --tamper takes script names, not paths"
    return None


# nuclei -------------------------------------------------------------------
def _nuclei_arg_check(ctx: Context, toks: list[str]) -> str | None:
    """-l reads target lists from files; -t pointing at a local FILE runs
    a hand-made template (arbitrary requests/code) - built-in template
    names and directories stay allowed; -code enables code templates."""
    bad = _file_target_check(ctx, toks, {"-l", "-list", "--list", "-resume"})
    if bad:
        return bad
    for i, tok in enumerate(toks):
        flag = tok.partition("=")[0]
        if flag in {"-code", "-p", "--proxy"}:
            return f"nuclei {flag} is disabled"
        if flag in {"-t", "--templates", "-turl", "--template-url",
                    "-w", "--workflows"}:
            val = _flag_value(toks, i)
            for piece in val.split(","):
                piece = piece.strip()
                if piece and Path(piece).is_file():
                    return "nuclei templates must come from template " \
                           "names or directories, not local files"
        if flag in {"-o", "-se", "-je", "-jle", "-me", "-rd", "-srd"} \
                and not _rel_path_ok(_flag_value(toks, i)):
            return f"nuclei {flag} must stay inside the working directory"
    return None


_ARG_CHECKS = {
    "curl": _curl_arg_check,
    "nmap": _nmap_arg_check,
    "ffuf": _ffuf_arg_check,
    "sqlmap": _sqlmap_arg_check,
    "nuclei": _nuclei_arg_check,
}


def _split_args(args: str) -> list[str]:
    import shlex
    try:
        return shlex.split(args, posix=False) if _is_windows() else shlex.split(args)
    except ValueError:
        return args.split()


def _is_windows() -> bool:
    import os
    return os.name == "nt"


# ---------------------------------------------------------------- finish

def finish(ctx: Context, summary: str) -> dict:
    ctx.finished = True
    ctx.finish_summary = summary
    ctx.session.note(f"## Agent summary\n\n{summary}")
    return {"finished": True, "stats": ctx.session.stats()}
