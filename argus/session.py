"""Session store: transcript, findings, notes - the evidence layer.

Everything the agent observes is written to disk under sessions/<id>/ so a
run is auditable and resumable. Findings are only accepted when their evidence
excerpt is a verbatim substring of a recorded response - the quote is checked,
not trusted.
"""
from __future__ import annotations

import hashlib
import hmac as _hmac
import json
import re
import sys
import threading
import time
import urllib.parse
from pathlib import Path

from . import __version__
from . import proof

SEVERITIES = ("critical", "high", "medium", "low", "info")
_CVSS_RE = re.compile(
    r"^CVSS:3\.[01]/AV:[NALP]/AC:[LH]/PR:[NLH]/UI:[NR]/S:[UC]"
    r"/C:[NLH]/I:[NLH]/A:[NLH]$")


def _slug(host: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.-]+", "_", host)[:60]


def _atomic_write(path: Path, text: str) -> None:
    """Write-rename so a crash mid-write cannot leave a truncated artifact
    (findings.json / summary.json are the deliverable, not scratch data)."""
    import os
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    # newline="": artifact bytes must be platform-stable - a digest
    # computed on Windows must verify on Linux, so writes pin LF
    try:
        with tmp.open("w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        tmp.replace(path)  # os.replace: atomic on POSIX and Windows alike
    finally:
        tmp.unlink(missing_ok=True)   # a failed write leaves no litter


def _chain(prev: str, entry: dict, key: str = "") -> str:
    """Hash-chain link over the canonical entry.

    Unkeyed (the default) this is sha256(prev + entry): it makes silent edits,
    insertions and mid-deletions detectable, which is what "tamper-evident"
    means and all it means. It does NOT resist forgery - anyone with this code
    can build a self-consistent session from nothing, because the chain is
    computable by anyone.

    With a key it is HMAC-SHA256, and then only a holder of the key can
    produce a chain that verifies. That is the difference between "this file
    was not edited after the run" and "this run happened", and an engagement
    whose report will be read by someone who did not watch it run wants the
    second. `--seal-key` supplies one; it is never written to any artifact.
    """
    payload = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    if key:
        return _hmac.new(key.encode("utf-8"), (prev + payload).encode("utf-8"),
                         hashlib.sha256).hexdigest()
    return hashlib.sha256((prev + payload).encode("utf-8")).hexdigest()


_REDACTED = "•••redacted•••"
_EVENT_VALUE_CAP = 60_000


def _bound_value(v):
    if isinstance(v, str):
        return v if len(v) <= _EVENT_VALUE_CAP else v[:_EVENT_VALUE_CAP] + "…[truncated]"
    try:
        s = json.dumps(v, ensure_ascii=False)
    except (TypeError, ValueError):
        # not natively JSON-safe - the transcript writer uses plain
        # json.dumps, so this would crash record_event without a string
        return str(v)[:_EVENT_VALUE_CAP]
    if len(s) <= _EVENT_VALUE_CAP:
        return v
    return s[:_EVENT_VALUE_CAP] + "…[truncated]"


def _redact_url(url):
    """http://user:pass@host -> http://<marker>@host - basic-auth
    credentials embedded in a URL persist nowhere; the scope guard only
    ever needed the host."""
    if not isinstance(url, str) or "@" not in url:
        return url
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return url
    if parts.username is None and parts.password is None:
        return url
    host = parts.hostname or ""
    try:
        if parts.port:
            host += f":{parts.port}"
    except ValueError:
        pass  # 'host:abc' - still strip the userinfo, just drop the port
    return urllib.parse.urlunsplit(
        (parts.scheme, f"{_REDACTED}@{host}" if host else _REDACTED,
         parts.path, parts.query, parts.fragment))


def _redact_obj(obj, secrets: set[str]):
    """Deep-copy an artifact structure replacing every occurrence of a
    declared operator secret with the redaction marker. Applied to request
    bodies, response bodies, event output and notes - the model sees the
    real bytes (it needs them to work); only persisted artifacts redact.
    A finding that must cite a secret to prove itself cannot be written -
    by design."""
    if not secrets:
        return obj
    if isinstance(obj, str):
        for v in secrets:
            if v and v in obj:
                obj = obj.replace(v, _REDACTED)
        return obj
    if isinstance(obj, dict):
        return {k: _redact_obj(v, secrets) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_redact_obj(v, secrets) for v in obj]
    return obj


def verify_transcript(sdir: Path, seal_key: str = "") -> dict:
    """Recompute the hash chain over transcript.jsonl. Detects edited,
    inserted or mid-deleted entries, and tail truncation when
    summary.json still anchors the recorded chain head."""
    tpath = Path(sdir) / "transcript.jsonl"
    out = {"entries": 0, "bad_lines": [], "chained": False}
    if not tpath.exists():
        out["error"] = "no transcript.jsonl"
        return out
    if not tpath.is_file():
        out["error"] = "transcript.jsonl is not a regular file"
        return out
    try:
        lines = tpath.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        out["error"] = f"transcript unreadable: {exc}"
        return out
    prev = ""
    entries: dict[str, dict] = {}
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            out["bad_lines"].append(i)
            continue
        if not isinstance(entry, dict):
            out["bad_lines"].append(i)
            continue
        stored = entry.pop("chain", None)
        if stored is None:
            if out["chained"]:
                # unchained line inside a chained run = insertion/corruption
                out["bad_lines"].append(i)
            continue  # legacy pre-chain prefix: excluded from verification
        out["chained"] = True
        expect = _chain(prev, entry, seal_key)
        if expect != stored:
            out["bad_lines"].append(i)
        prev = stored
        out["entries"] += 1
        entries[entry.get("id", "")] = entry
    # A keyed run cannot be verified without the key, and verifying it
    # unkeyed would report every line as tampered - say which it is rather
    # than producing a confident wrong answer.
    mpath = Path(sdir) / "meta.json"
    if mpath.is_file():
        try:
            meta = json.loads(mpath.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            meta = None
        if isinstance(meta, dict) and meta.get("chain_keyed") and not seal_key:
            out["key_required"] = True
    # summary.json anchors the last link - if present, a tail-truncated
    # transcript no longer reaches the recorded head
    spath = Path(sdir) / "summary.json"
    if spath.exists() and out["chained"]:
        try:
            sdata = json.loads(spath.read_text(encoding="utf-8"))
            head = sdata.get("transcript_chain_head") \
                if isinstance(sdata, dict) else None
        except (ValueError, OSError):
            head = None
        out["head_anchor"] = head
        if head and prev != head:
            out["tail_truncated"] = True
        elif not head:
            # a summary without its anchor is itself a tamper signal: with
            # nothing to compare, a truncated tail would verify clean
            out["anchor_missing"] = True
    # findings.json itself is not chained - but every claim in it must cite
    # chained transcript evidence verbatim. Re-validating here makes an
    # edited findings.json (fake finding, inflated severity) detectable.
    fpath = Path(sdir) / "findings.json"
    if fpath.exists() and out["chained"]:
        try:
            stored_findings = json.loads(fpath.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            stored_findings = []
        if not isinstance(stored_findings, list):
            stored_findings = []
        out["findings_checked"] = len(stored_findings)
        bad = findings_bad(entries, stored_findings)
        if bad:
            out["findings_bad"] = bad
        inflated = findings_overgraded(entries, stored_findings)
        if inflated:
            out["findings_overgraded"] = inflated
    # a run sealed with artifacts_digest anchors every un-chained file:
    # meta.json, findings.json and summary.json (minus the mutable head/
    # duration fields). Any post-run edit surfaces as a digest mismatch.
    dig = next((e for e in reversed(list(entries.values()))
                if e.get("kind") == "artifacts_digest"), None)
    if dig and out["chained"]:
        files_dig = dig.get("files")
        files_dig = files_dig if isinstance(files_dig, dict) else {}
        out["sealed"] = sorted(files_dig.keys())
        mismatched = []
        for name, want in files_dig.items():
            p = Path(sdir) / name
            if not p.is_file():
                # missing - or swapped for a directory: either way the
                # sealed bytes are gone, which is itself a tamper signal
                mismatched.append(name)
                continue
            if name == "summary.json":
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    if not isinstance(data, dict):
                        raise ValueError("summary.json is not an object")
                    for k in ("transcript_chain_head", "duration_s"):
                        data.pop(k, None)
                    got = hashlib.sha256(json.dumps(
                        data, sort_keys=True, ensure_ascii=False
                    ).encode()).hexdigest()
                except (ValueError, OSError):
                    mismatched.append(name)
                    continue
            else:
                try:
                    got = hashlib.sha256(p.read_bytes()).hexdigest()
                except OSError:
                    mismatched.append(name)
                    continue
            if got != want:
                mismatched.append(name)
        if mismatched:
            out["artifact_mismatch"] = mismatched
    return out


def findings_overgraded(entries: dict, findings: list) -> list[dict]:
    """Findings claiming a proof grade the cited evidence does not support.

    `argus verify` already re-validates that every excerpt is verbatim bytes
    from a chained exchange. That catches an invented finding and leaves the
    next edit open: raise `"grade"` from candidate to proven in findings.json
    and the claim gets stronger with no new evidence. The grade is recomputed
    here from the chained entries, so the claim has to hold against the
    transcript rather than against the file it is written in.

    Only an INFLATED grade is reported. A stored grade weaker than the
    recomputed one means the matrix grew more permissive since the run, which
    is benign - failing a verify on that would make every requirement change
    retroactively condemn old sessions.
    """
    out = []
    entries = entries if isinstance(entries, dict) else {}
    rows = [f for f in (findings or []) if isinstance(f, dict)]
    # Does this file grade at all? If any row carries a grade, a row without
    # one had it removed - deleting the grade AND the proof block together
    # otherwise looked exactly like a session recorded before grading existed.
    graded_file = any(str(f.get("grade") or "").strip() for f in rows)
    for f in rows:
        stored = str(f.get("grade") or "").strip().lower()
        if not stored and graded_file:
            out.append({"id": f.get("id", "?"), "claimed": "(removed)",
                        "evidence_supports": "unknown",
                        "missing": ["the grade is missing from a row in a "
                                    "graded findings file"]})
            continue
        if not stored:
            # no grade at all: recorded before grading existed, or by a tool
            # that does not grade. Only flag it when the row carries a proof
            # block, which means it WAS graded and the grade was removed.
            if isinstance(f.get("proof"), dict) and f["proof"].get("checks"):
                out.append({"id": f.get("id", "?"), "claimed": "(removed)",
                            "evidence_supports": "unknown",
                            "missing": ["the grade was deleted from a graded "
                                        "finding"]})
            continue
        if stored not in _GRADE_RANK:
            # `Proven`, `proven `, `PROVEN`, `prooven` - normalizing catches
            # the first three, and anything still unrecognized is an edit, not
            # a legacy row. Skipping it let a one-word change defeat the whole
            # control.
            out.append({"id": f.get("id", "?"), "claimed": str(f.get("grade")),
                        "evidence_supports": "not a grade",
                        "missing": [f"{f.get('grade')!r} is not one of "
                                    f"{sorted(_GRADE_RANK)}"]})
            continue
        ids = f.get("evidence_ids")
        cited = [entries.get(r) for r in ids if isinstance(r, str)] \
            if isinstance(ids, list) else []
        verdict = proof.grade(f.get("vuln_class") or f.get("category") or "",
                              str(f.get("evidence_excerpt") or ""),
                              [e for e in cited if isinstance(e, dict)])
        if _GRADE_RANK.get(stored, 0) > _GRADE_RANK.get(verdict.grade, 0):
            out.append({"id": f.get("id", "?"), "claimed": stored,
                        "evidence_supports": verdict.grade,
                        "missing": verdict.missing})
    return out


def findings_bad(entries: dict, findings: list) -> list[str]:
    """Finding ids whose evidence no longer verifies against the transcript:
    invented request ids, empty excerpts, or a quote that is not a verbatim
    substring of any cited response/event. Used by `argus verify` and by
    `argus report` (a re-render must not silently carry tampered claims)."""
    bad = []
    entries = entries if isinstance(entries, dict) else {}
    for f in findings if isinstance(findings, list) else []:
        if not isinstance(f, dict):
            bad.append("?")
            continue
        excerpt = str(f.get("evidence_excerpt") or "").strip()
        ids = f.get("evidence_ids") or []
        if not isinstance(ids, list):
            ids = []
        # ids are transcript keys - a tampered finding can carry
        # unhashable members ([1,2]) which must fail as "bad",
        # not crash the verifier
        cited = [entries.get(r) if isinstance(r, str) else None
                 for r in ids]
        if f.get("severity") not in SEVERITIES or \
                not excerpt or not cited or None in cited or \
                not any(excerpt in _evidence_text_of_entry(e)
                        for e in cited):
            bad.append(f.get("id", "?"))
    return bad


def _evidence_text_of_entry(entry: dict | None) -> str:
    if not isinstance(entry, dict):
        return ""
    resp = entry.get("response") or {}
    body = resp.get("body") if isinstance(resp, dict) else None
    # response headers carry the proof for header-class findings (CRLF
    # injection, security headers, server disclosure) - the recorded
    # headers are already redacted, so serializing them into the
    # citable text lets a finding quote its real evidence. Both the
    # JSON shape the model saw and wire-style 'k: v' lines are included
    # so either quotation form matches.
    hdrs = resp.get("headers") if isinstance(resp, dict) else None
    parts = []
    if isinstance(hdrs, dict) and hdrs:
        parts.append(json.dumps(hdrs, ensure_ascii=False))
        parts.extend(f"{k}: {v}" for k, v in hdrs.items())
    parts.append(str(body or "") or str(entry.get("output") or ""))
    return "\n".join(p for p in parts if p)


_GRADE_RANK = {"proven": 3, "candidate": 2, "unproven": 1, "refused": 0}


def _finding_key(category: str, url: str) -> tuple:
    """Dedup key: same bug class on the same endpoint+params is one finding."""
    cat = re.sub(r"[^a-z0-9]", "", str(category or "").lower())
    url = str(url or "")
    try:
        p = urllib.parse.urlparse(url if "://" in url else "http://" + url)
    except ValueError:
        # unparseable (e.g. 'http://[bad') - keep a stable key rather
        # than crashing dedup/diff on a tampered or mangled url
        return (cat, "", url, ())
    params = tuple(sorted(k for k, _ in urllib.parse.parse_qsl(p.query)))
    return (cat, p.netloc.lower(), p.path or "/", params)


# Audit-grade reports carry standard identifiers; the category the model
# names maps to the canonical CWE automatically (normalized: strip
# non-alphanumerics, so "info-disclosure" == "infodisclosure").
_CWE = {
    # rce is the canonical class the matrix normalizes command injection to,
    # and it was the one class with no mapping - so the project's headline
    # finding carried no CWE and no OWASP row in the report.
    "rce": "CWE-78", "sqli": "CWE-89", "nosqli": "CWE-943", "ssti": "CWE-1336",
    "time": "CWE-78", "cmdinjection": "CWE-78", "lfi": "CWE-22",
    "rfi": "CWE-98", "xss": "CWE-79", "reflection": "CWE-79",
    "idor": "CWE-639", "enum": "CWE-204", "enumeration": "CWE-204",
    "lockout": "CWE-307", "massassign": "CWE-915",
    "massassignment": "CWE-915", "ssrf": "CWE-918", "xxe": "CWE-611",
    # CWE-444 is request smuggling; an X-Forwarded-Host ACL bypass is header
    # neutralization, and the two are separate classes in the matrix now.
    "csrf": "CWE-352", "xfh": "CWE-290", "hostheader": "CWE-290",
    "upload": "CWE-434",
    "race": "CWE-362", "deserialize": "CWE-502",
    "deserialization": "CWE-502", "cache": "CWE-525", "massassign": "CWE-915",
    "ppoll": "CWE-1321", "race": "CWE-362",
    "cachepoisoning": "CWE-525", "ppoll": "CWE-1321",
    "prototypepollution": "CWE-1321", "smuggle": "CWE-444",
    "requestsmuggling": "CWE-444", "disclosure": "CWE-200",
    "infodisclosure": "CWE-200", "websocket": "CWE-1385",
    "crlf": "CWE-113", "redirect": "CWE-601", "openredirect": "CWE-601",
    "cors": "CWE-942", "jwt": "CWE-347", "method": "CWE-749",
    "graphql": "CWE-639", "dos": "CWE-400",
}


def _cwe_of(category: str) -> str:
    return _CWE.get(
        re.sub(r"[^a-z0-9]", "", str(category or "").lower()), "")


# CWE -> OWASP Top 10 (2021) bucket. This is the taxonomy audit reports
# are actually summarized in; findings carry both labels.
_OWASP = {
    "CWE-639": "A01 Broken Access Control",
    "CWE-22": "A01 Broken Access Control",
    "CWE-601": "A01 Broken Access Control",
    "CWE-352": "A01 Broken Access Control",
    "CWE-200": "A01 Broken Access Control",
    "CWE-1385": "A01 Broken Access Control",
    "CWE-347": "A02 Cryptographic Failures",
    "CWE-89": "A03 Injection",
    "CWE-943": "A03 Injection",
    "CWE-78": "A03 Injection",
    "CWE-1336": "A03 Injection",
    "CWE-79": "A03 Injection",
    "CWE-113": "A03 Injection",
    "CWE-915": "A04 Insecure Design",
    "CWE-362": "A04 Insecure Design",
    "CWE-611": "A05 Security Misconfiguration",
    "CWE-434": "A05 Security Misconfiguration",
    "CWE-525": "A05 Security Misconfiguration",
    "CWE-444": "A05 Security Misconfiguration",
    "CWE-942": "A05 Security Misconfiguration",
    "CWE-749": "A05 Security Misconfiguration",
    "CWE-204": "A07 AuthN Failures",
    "CWE-307": "A07 AuthN Failures",
    "CWE-502": "A08 Integrity Failures",
    "CWE-918": "A10 SSRF",
    "CWE-98": "A08 Integrity Failures",
    "CWE-290": "A01 Broken Access Control",
}


def _owasp_of(cwe: str) -> str:
    return _OWASP.get(cwe or "", "")


def sanitized_findings(rows) -> list[dict]:
    """Findings view safe for renderers: every row a dict, every field a
    str. findings.json is operator-editable - a hand-edited file must not
    crash report/sarif/html rendering (verify still flags bad rows)."""
    out = []
    for f in rows or []:
        if not isinstance(f, dict):
            continue
        g = dict(f)
        for k in ("id", "severity", "title", "category", "url",
                  "description", "remediation", "cvss", "cwe", "owasp",
                  "agent", "evidence_excerpt", "vuln_class", "grade"):
            g[k] = str(g.get(k) or "")
        # the report renders the proof block from this; an edited file may
        # carry anything at all under those keys
        verdict = g.get("proof")
        if not isinstance(verdict, dict):
            g["proof"] = {}
        else:
            checks = verdict.get("checks")
            verdict = dict(verdict)
            verdict["checks"] = [c for c in checks
                                 if isinstance(c, dict)] \
                if isinstance(checks, list) else []
            missing = verdict.get("missing")
            verdict["missing"] = [str(x) for x in missing] \
                if isinstance(missing, list) else []
            for k in ("vuln_class", "requirement"):
                verdict[k] = str(verdict.get(k) or "")
            g["proof"] = verdict
        ids = g.get("evidence_ids")
        g["evidence_ids"] = [str(i) for i in ids] \
            if isinstance(ids, list) else []
        try:
            g["ts"] = float(g.get("ts") or 0)
        except (ValueError, TypeError):
            g["ts"] = 0.0
        out.append(g)
    return out


class Session:
    def __init__(self, base_dir: Path, target: str, meta: dict,
                 resume: Path | None = None,
                 secrets: list[str] | None = None,
                 require_proof: bool = False,
                 seal_key: str = ""):
        self._lock = threading.Lock()
        self.require_proof = bool(require_proof)
        # never persisted: meta.json records that the chain is keyed, never
        # the key, or the artifact would carry its own forging material
        self.seal_key = str(seal_key or "")
        # >=4 chars: a shorter 'secret' would redact innocent bytes across
        # the whole transcript - enforce the floor here, not just in CLI
        secrets = {s for s in (secrets or []) if len(s) >= 4}
        if resume is not None:
            self.secret_values: set[str] = secrets
            self._resume(Path(resume), target, meta)
            return
        host = urllib.parse.urlparse(target).hostname or "target"
        self.id = time.strftime("%Y%m%d-%H%M%S") + "-" + _slug(host)
        self.dir = Path(base_dir) / self.id
        if self.dir.exists():
            # same-second parallel runs name the same dir - bump a suffix
            # or both runs interleave one transcript chain and overwrite
            # each other's meta.json/findings.json
            for n in range(2, 100):
                cand = Path(base_dir) / f"{self.id}-{n}"
                if not cand.exists():
                    self.id, self.dir = f"{self.id}-{n}", cand
                    break
        self.dir.mkdir(parents=True, exist_ok=True)
        self.started = time.time()
        self._seq = 0
        self._transcript: dict[str, dict] = {}
        self.findings: list[dict] = []
        self.resumed = False
        self._last_chain = ""
        # operator-declared credential values, populated by GuardedClient
        # from --secret/--header - every artifact write redacts them
        self.secret_values: set[str] = secrets
        _atomic_write(
            self.dir / "meta.json",
            json.dumps({"id": self.id, "target": target,
                        "started": self.started,
                        # which build produced this session - a reviewer
                        # re-validating artifacts needs to know which
                        # evidence rules applied
                        "argus_version": __version__,
                        **_redact_obj(meta, self.secret_values)},
                       indent=2, ensure_ascii=False))
        with (self.dir / "notes.md").open("w", encoding="utf-8",
                                          newline="") as fh:
            fh.write(f"# Working notes - {target}\n\n")

    def _resume(self, sdir: Path, target: str, meta: dict) -> None:
        """Continue an existing session dir: transcript, findings and request
        ids all carry over, so the evidence chain and dedup stay intact."""
        if not sdir.is_dir():
            raise FileNotFoundError(f"cannot resume: {sdir} is not a session dir")
        if not (sdir / "meta.json").exists() and \
                not (sdir / "transcript.jsonl").exists():
            # an arbitrary dir (e.g. the sessions/ parent) "resumed"
            # would get artifacts written into it - refuse: a session
            # dir carries meta.json and/or transcript.jsonl
            raise FileNotFoundError(
                f"cannot resume: {sdir} has no meta.json/transcript.jsonl "
                "- not a session dir")
        self.dir = sdir
        self.id = sdir.name
        self.resumed = True
        self.started = time.time()
        self._seq = 0
        self._transcript = {}
        self.findings = []
        self._last_chain = ""
        mpath = sdir / "meta.json"
        old: dict = {}
        if mpath.exists():
            try:
                old = json.loads(mpath.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                old = {}
            try:
                self.started = float(old.get("started") or self.started)
            except (TypeError, ValueError):
                pass  # malformed started - keep the fresh timestamp
            old_target = old.get("target")
            # resuming against a different target would conflate two
            # engagements' evidence and findings - refuse loudly
            if old_target and old_target != target:
                raise ValueError(
                    f"cannot resume {sdir.name}: session target "
                    f"{old_target!r} != current target {target!r}")
        tpath = sdir / "transcript.jsonl"
        if tpath.is_file():
            try:
                tlines = tpath.read_text(encoding="utf-8").splitlines()
            except OSError:
                tlines = []
            for line in tlines:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(entry, dict) \
                        or not isinstance(entry.get("id"), str):
                    continue
                self._transcript[entry["id"]] = entry
                if entry.get("chain"):
                    self._last_chain = entry["chain"]
                suffix = entry["id"][1:]
                if suffix.isdigit():
                    self._seq = max(self._seq, int(suffix))
        # meta.json gone means old_target is unknown - fall back to the
        # evidence itself: the first recorded request's host must match
        # the current target or this is the wrong session dir
        if not old.get("target"):
            first_url = next(
                (e.get("request", {}).get("url", "")
                 for e in self._transcript.values()
                 if isinstance(e.get("request"), dict)
                 and e["request"].get("url")), "")
            if first_url:
                try:
                    old_host = urllib.parse.urlparse(first_url).hostname
                    new_host = urllib.parse.urlparse(target).hostname
                except ValueError:
                    old_host = new_host = None
                if old_host and new_host and \
                        old_host.lower() != new_host.lower():
                    raise ValueError(
                        f"cannot resume {sdir.name}: transcript "
                        f"evidence targets {old_host!r} != current "
                        f"target host {new_host!r}")
        fpath = sdir / "findings.json"
        if fpath.is_file():
            try:
                rows = json.loads(fpath.read_text(encoding="utf-8"))
                # rows must be finding objects - stray scalars would crash
                # dedup/render downstream
                self.findings = [r for r in rows if isinstance(r, dict)] \
                    if isinstance(rows, list) else []
            except (ValueError, OSError):
                self.findings = []
        if not (sdir / "notes.md").exists():
            with (sdir / "notes.md").open("w", encoding="utf-8",
                                          newline="") as fh:
                fh.write(f"# Working notes - {target}\n\n")
        # the resumed run may carry different budgets/flags - meta.json must
        # reflect the CURRENT engagement constraints, marked as resumed
        try:
            merged = dict(old)
            merged.update(meta)
            merged["resumed"] = True
            # keep the producing version; flag when a different build
            # continued the session
            if merged.get("argus_version") != __version__:
                merged["resumed_by"] = __version__
            _atomic_write(mpath, json.dumps(
                {"id": self.id, "target": target, "started": self.started,
                 **merged}, indent=2, ensure_ascii=False))
        except OSError:
            pass
        self.note(f"> session resumed ({len(self._transcript)} prior exchanges, "
                  f"{len(self.findings)} prior findings)")

    @property
    def transcript_path(self) -> Path:
        return self.dir / "transcript.jsonl"

    @property
    def findings_path(self) -> Path:
        return self.dir / "findings.json"

    @property
    def notes_path(self) -> Path:
        return self.dir / "notes.md"

    # ------------------------------------------------------------------
    # Transcript
    # ------------------------------------------------------------------
    def record_exchange(
        self,
        tool: str,
        request: dict,
        response: dict,
        note: str = "",
        agent: str = "",
    ) -> str:
        """Append one request/response pair. Returns its request id (r<n>)."""
        with self._lock:
            self._seq += 1
            rid = f"r{self._seq}"
            req = _redact_obj(request, self.secret_values)
            resp = _redact_obj(response, self.secret_values)
            # basic-auth credentials embedded in URLs (user:pass@host)
            # are operator secrets too - strip userinfo before persisting
            for container in (req, resp):
                if not isinstance(container, dict):
                    continue
                for k in ("url", "final_url", "blocked_to"):
                    if k in container:
                        container[k] = _redact_url(container[k])
                for hop in container.get("redirects") or []:
                    if isinstance(hop, dict):
                        for k in ("from", "to"):
                            if k in hop:
                                hop[k] = _redact_url(hop[k])
            entry = {
                "id": rid,
                "ts": round(time.time(), 3),
                "tool": tool,
                # operator secrets persist nowhere: redact declared values
                # out of bodies/request_text before the bytes hit disk
                "request": req,
                "response": resp,
            }
            if agent:
                entry["agent"] = agent
            if note:
                entry["note"] = note
            entry["chain"] = _chain(self._last_chain, entry,
                                    getattr(self, "seal_key", ""))
            # serialize BEFORE committing in-memory state: a non-JSON leaf
            # in a caller-built request dict must fail without leaving
            # _transcript/_last_chain ahead of the file (chain gap)
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            self._last_chain = entry["chain"]
            self._transcript[rid] = entry
            with self.transcript_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(line)
            return rid

    def record_event(self, kind: str, detail: dict, agent: str = "") -> str:
        """Record a non-HTTP event (external tool run, error). Returns r<n>."""
        with self._lock:
            self._seq += 1
            rid = f"r{self._seq}"
            entry = {"id": rid, "ts": round(time.time(), 3), "kind": kind,
                     **{k: _bound_value(v) for k, v in
                        _redact_obj(detail, self.secret_values).items()}}
            if agent:
                entry["agent"] = agent
            entry["chain"] = _chain(self._last_chain, entry,
                                    getattr(self, "seal_key", ""))
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            self._last_chain = entry["chain"]
            self._transcript[rid] = entry
            with self.transcript_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(line)
            return rid

    def seal_artifacts(self) -> str | None:
        """Record sha256 digests of the un-chained artifacts (meta.json,
        findings.json, summary.json) as a transcript event, then re-anchor
        summary.json to the new chain head. Called once at run end after
        render - afterwards ANY edit to those files is detectable by
        `argus verify`. The summary digest skips transcript_chain_head and
        duration_s: both are legitimately rewritten by `argus report`
        re-renders."""
        files: dict[str, str] = {}
        for name in ("meta.json", "findings.json", "notes.md",
                     "report.md", "report.html", "report.sarif"):
            p = self.dir / name
            if p.exists():
                files[name] = hashlib.sha256(p.read_bytes()).hexdigest()
        # agent.log / agent-<role>.log are diagnostic, but they are still
        # session artifacts an auditor may read - seal them too
        for p in sorted(self.dir.glob("agent*.log")):
            files[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        sp = self.dir / "summary.json"
        if sp.exists():
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data["sealed"] = sorted(set(files) | {"summary.json"})
                    # cheap surface for `sessions`/report readers that skip
                    # the transcript - set BEFORE the digest so the stored
                    # value itself is covered
                    for k in ("transcript_chain_head", "duration_s"):
                        data.pop(k, None)
                    files["summary.json"] = hashlib.sha256(json.dumps(
                        data, sort_keys=True, ensure_ascii=False).encode()
                    ).hexdigest()
            except (ValueError, OSError):
                pass
        if not files:
            return None
        # fixed id, not an r<n>: the seal must not consume a sequence number
        # or `requests` in summary.json changes on every re-render and the
        # digest would flag its own bookkeeping
        with self._lock:
            entry = {"id": "seal", "ts": round(time.time(), 3),
                     "kind": "artifacts_digest", "files": files}
            entry["chain"] = _chain(self._last_chain, entry,
                                    getattr(self, "seal_key", ""))
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            self._last_chain = entry["chain"]
            self._transcript["seal"] = entry
            with self.transcript_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(line)
        rid = "seal"
        if sp.exists():
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data["transcript_chain_head"] = self._last_chain
                    data["sealed"] = sorted(set(files) | {"summary.json"})
                    _atomic_write(sp, json.dumps(data, indent=2,
                                                 ensure_ascii=False))
            except (ValueError, OSError):
                pass
        return rid

    def get_exchange(self, rid: str) -> dict | None:
        return self._transcript.get(rid)

    def response_body(self, rid: str) -> str:
        entry = self._transcript.get(rid)
        if not entry:
            return ""
        resp = entry.get("response") or {}
        return resp.get("body", "") or ""

    @staticmethod
    def _evidence_text_of(entry: dict | None) -> str:
        return _evidence_text_of_entry(entry)

    def evidence_text(self, rid: str) -> str:
        """Verbatim bytes a finding may quote: response headers + body,
        or event output."""
        return self._evidence_text_of(self._transcript.get(rid))

    # ------------------------------------------------------------------
    # Findings
    # ------------------------------------------------------------------
    def add_finding(
        self,
        title: str,
        severity: str,
        category: str,
        url: str,
        evidence_ids: list[str],
        evidence_excerpt: str,
        description: str,
        remediation: str,
        agent: str = "",
        cvss: str = "",
    ) -> dict:
        severity = str(severity or "").lower()
        if severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        cvss = str(cvss or "").strip()
        if cvss and not _CVSS_RE.match(cvss):
            raise ValueError(
                "cvss must be a base vector like "
                "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        excerpt = str(evidence_excerpt or "").strip()
        if not excerpt:
            raise ValueError("evidence_excerpt must quote the proving bytes")
        with self._lock:  # snapshot: other workers keep appending mid-check
            transcript_snapshot = dict(self._transcript)
        if not evidence_ids:
            # Resolve the proving exchange from the excerpt itself - the
            # verbatim gate is unchanged: the quote must exist in a recorded
            # response/event. Cite the MOST RECENT entry that contains it.
            #
            # It used to cite the first, and that is how the checked-in sample
            # session came to carry a critical "forged admin token accepted"
            # whose evidence is `GET /api/user/1`: the demo sent the forged
            # token, got `"role": "admin"` back, and the auto-resolution
            # reached past it to an earlier IDOR response that happened to
            # contain the same bytes. The proving exchange is the one just
            # sent, not the first one that ever matched.
            matches = [r for r in reversed(list(transcript_snapshot))
                       if excerpt in self._evidence_text_of(
                           transcript_snapshot.get(r))]
            # Prefer a real request/response over a non-HTTP event. The most
            # recent match can be a scanner's output line, and citing that
            # fails the proof matrix's wire check for every class - so a
            # provable finding came back unproven because an `external_result`
            # happened to quote the same bytes.
            exchanges = [r for r in matches
                         if isinstance((transcript_snapshot.get(r) or {})
                                       .get("response"), dict)]
            evidence_ids = (exchanges or matches)[:1]
            if not evidence_ids:
                raise ValueError(
                    "evidence_excerpt is not a verbatim substring of any "
                    "recorded response or event")
        unknown = [r for r in evidence_ids if r not in transcript_snapshot]
        if unknown:
            raise ValueError(f"unknown evidence request ids: {unknown}")
        if not any(excerpt in self._evidence_text_of(
                transcript_snapshot.get(r)) for r in evidence_ids):
            raise ValueError(
                "evidence_excerpt is not a verbatim substring of any cited response"
            )
        vuln_class = proof.canonical(category)
        cited = [transcript_snapshot.get(r) for r in evidence_ids]
        verdict = proof.grade(category, excerpt, cited)
        if verdict.grade == "refused":
            # Not gated on require_proof: the matrix does not say this evidence
            # is thin, it says the system does not prove this class at all.
            # Recording it anyway - the old behaviour kept a `critical` dos
            # finding on file - is the exact assertion-instead-of-proof the
            # gate exists to stop.
            spec = proof.spec_for(category)
            raise ValueError(
                f"{vuln_class} is a refused class: "
                f"{(spec.refusal if spec else '') or verdict.requirement}. "
                "Describe the mechanism in note() instead - there is no "
                "evidence that would make this a finding here")
        if getattr(self, "require_proof", False) and not verdict.proven:
            raise ValueError(
                f"--require-proof: {vuln_class} graded {verdict.grade}, not proven. "
                f"Requirement: {verdict.requirement or 'class not in the proof matrix'}. "
                f"Missing: {', '.join(verdict.missing) or 'n/a'}. "
                "Collect those and record again, or keep it in note()")
        # The class, not the author's spelling. `SQLi`, `sql-injection` and
        # `sqlinjection` normalized to three different keys, so two workers
        # could record one bug three times - the dedup the docs promised.
        key = _finding_key(vuln_class, _redact_url(url))
        with self._lock:
            for existing in self.findings:
                if _finding_key(existing.get("vuln_class") or existing.get("category"),
                                existing.get("url")) != key:
                    continue
                # Better evidence for a bug already on record is an UPGRADE,
                # not a duplicate. Refusing it was a trap the grading itself
                # created: the agent is told which checks a candidate is
                # missing, goes and collects them, and then had nowhere to put
                # them. The finding keeps its id so earlier references and the
                # transcript still resolve.
                if _GRADE_RANK.get(verdict.grade, 0) > \
                        _GRADE_RANK.get(existing.get("grade", ""), 0):
                    fields = {
                        "title": str(title or "").strip() or existing.get("title"),
                        "severity": severity,
                        "evidence_ids": evidence_ids,
                        "evidence_excerpt": excerpt[:2000],
                        "grade": verdict.grade,
                        "proof": verdict.to_dict(),
                        "upgraded_from": existing.get("grade", ""),
                        # the ORIGINAL citation stays readable: the upgrade
                        # replaced evidence_ids wholesale, so a second worker
                        # grading higher erased the first worker's reference
                        # and the report could no longer show what it had.
                        "superseded_evidence_ids": [
                            *(existing.get("superseded_evidence_ids") or []),
                            *[i for i in (existing.get("evidence_ids") or [])
                              if i not in evidence_ids]],
                        # `ts` is when the finding was FIRST recorded, and
                        # time_to_first_finding_s is computed from it - the
                        # upgrade used to rewrite it to the upgrade time
                        "upgraded_ts": round(time.time(), 3),
                    }
                    if cvss:
                        fields["cvss"] = cvss
                    if agent:
                        fields["agent"] = agent
                    existing.update(fields)
                    if description:
                        existing["description"] = str(description).strip()
                    if remediation:
                        existing["remediation"] = str(remediation).strip()
                    _atomic_write(
                        self.findings_path,
                        json.dumps(self.findings, indent=2, ensure_ascii=False))
                    return dict(existing)
                raise ValueError(
                    f"duplicate of {existing.get('id')} "
                    f"({vuln_class} on {url}, already {existing.get('grade', 'recorded')}); "
                    "same bug class + endpoint is one finding. Re-record only "
                    "with evidence that grades higher - otherwise put the extra "
                    "evidence in note()")
            finding = {
                "id": f"F{len(self.findings) + 1:02d}",
                "title": str(title or "").strip(),
                "severity": severity,
                "category": str(category or "").strip(),
                "url": _redact_url(url),
                "evidence_ids": evidence_ids,
                "evidence_excerpt": excerpt[:2000],
                "vuln_class": vuln_class,
                "grade": verdict.grade,
                "proof": verdict.to_dict(),
                "description": str(description or "").strip(),
                "remediation": str(remediation or "").strip(),
                "ts": round(time.time(), 3),
            }
            if agent:
                finding["agent"] = str(agent)
            if cvss:
                finding["cvss"] = cvss
            cwe = _cwe_of(vuln_class) or _cwe_of(category)
            if cwe:
                finding["cwe"] = cwe
                owasp = _owasp_of(cwe)
                if owasp:
                    finding["owasp"] = owasp
            # Write first, commit second. Appending before the write left a
            # finding in memory that never reached findings.json if the write
            # failed, so `stats()` and summary.json counted a finding the file
            # did not have.
            pending = [*self.findings, finding]
            _atomic_write(
                self.findings_path,
                json.dumps(pending, indent=2, ensure_ascii=False))
            self.findings = pending
        return finding

    def note(self, text: str, agent: str = "") -> None:
        text = str(text or "")[:20_000]
        stamp = time.strftime("%H:%M:%S")
        prefix = f"- **[{stamp} {agent}]** " if agent else \
            f"- **[{stamp}]** " if not text.startswith(
                ("#", ">", "-", "*")) else ""
        with self._lock:
            try:
                with self.notes_path.open(
                        "a", encoding="utf-8", newline="") as fh:
                    fh.write(prefix + _redact_obj(
                        text.rstrip(), self.secret_values) + "\n\n")
            except OSError as exc:
                # notes.md swapped for a directory or unwritable must not
                # kill a run mid-engagement - the transcript still carries
                # evidence; warn once so the gap is operator-visible
                if not getattr(self, "_notes_warned", False):
                    self._notes_warned = True
                    print(f"[argus] notes.md unwritable: {exc}",
                          file=sys.stderr)

    def stats(self) -> dict:
        return {
            "requests": self._seq,
            "findings": len(self.findings),
            "elapsed_s": round(time.time() - self.started, 1),
        }
