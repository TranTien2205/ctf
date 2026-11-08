"""Session store: transcript, findings, notes - the evidence layer.

Everything the agent observes is written to disk under sessions/<id>/ so a
run is auditable and resumable. Findings are only accepted when their evidence
excerpt is a verbatim substring of a recorded response - the quote is checked,
not trusted.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import urllib.parse
from pathlib import Path

SEVERITIES = ("critical", "high", "medium", "low", "info")
_CVSS_RE = re.compile(
    r"^CVSS:3\.[01]/AV:[NALP]/AC:[LH]/PR:[NLH]/UI:[NR]/S:[UC]"
    r"/C:[NLH]/I:[NLH]/A:[NLH]$")


def _slug(host: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.-]+", "_", host)[:60]


def _atomic_write(path: Path, text: str) -> None:
    """Write-rename so a crash mid-write cannot leave a truncated artifact
    (findings.json / summary.json are the deliverable, not scratch data)."""
    tmp = path.with_name(path.name + ".tmp")
    # newline="": artifact bytes must be platform-stable - a digest
    # computed on Windows must verify on Linux, so writes pin LF
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    tmp.replace(path)  # os.replace: atomic on POSIX and Windows alike


def _chain(prev: str, entry: dict) -> str:
    """Hash-chain link: sha256(prev_link + canonical entry). Makes silent
    edits, insertions and mid-deletions in transcript.jsonl detectable."""
    payload = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((prev + payload).encode("utf-8")).hexdigest()


def verify_transcript(sdir: Path) -> dict:
    """Recompute the hash chain over transcript.jsonl. Detects edited,
    inserted or mid-deleted entries, and tail truncation when
    summary.json still anchors the recorded chain head."""
    tpath = Path(sdir) / "transcript.jsonl"
    out = {"entries": 0, "bad_lines": [], "chained": False}
    if not tpath.exists():
        out["error"] = "no transcript.jsonl"
        return out
    prev = ""
    entries: dict[str, dict] = {}
    for i, line in enumerate(
            tpath.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            out["bad_lines"].append(i)
            continue
        stored = entry.pop("chain", None)
        if stored is None:
            if out["chained"]:
                # unchained line inside a chained run = insertion/corruption
                out["bad_lines"].append(i)
            continue  # legacy pre-chain prefix: excluded from verification
        out["chained"] = True
        expect = _chain(prev, entry)
        if expect != stored:
            out["bad_lines"].append(i)
        prev = stored
        out["entries"] += 1
        entries[entry.get("id", "")] = entry
    # summary.json anchors the last link - if present, a tail-truncated
    # transcript no longer reaches the recorded head
    spath = Path(sdir) / "summary.json"
    if spath.exists() and out["chained"]:
        try:
            head = json.loads(spath.read_text(
                encoding="utf-8")).get("transcript_chain_head")
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
        out["findings_checked"] = len(stored_findings)
        bad = findings_bad(entries, stored_findings)
        if bad:
            out["findings_bad"] = bad
    # a run sealed with artifacts_digest anchors every un-chained file:
    # meta.json, findings.json and summary.json (minus the mutable head/
    # duration fields). Any post-run edit surfaces as a digest mismatch.
    dig = next((e for e in reversed(list(entries.values()))
                if e.get("kind") == "artifacts_digest"), None)
    if dig and out["chained"]:
        out["sealed"] = sorted((dig.get("files") or {}).keys())
        mismatched = []
        for name, want in (dig.get("files") or {}).items():
            p = Path(sdir) / name
            if not p.exists():
                mismatched.append(name)
                continue
            if name == "summary.json":
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    for k in ("transcript_chain_head", "duration_s"):
                        data.pop(k, None)
                    got = hashlib.sha256(json.dumps(
                        data, sort_keys=True, ensure_ascii=False
                    ).encode()).hexdigest()
                except (ValueError, OSError):
                    mismatched.append(name)
                    continue
            else:
                got = hashlib.sha256(p.read_bytes()).hexdigest()
            if got != want:
                mismatched.append(name)
        if mismatched:
            out["artifact_mismatch"] = mismatched
    return out


def findings_bad(entries: dict, findings: list) -> list[str]:
    """Finding ids whose evidence no longer verifies against the transcript:
    invented request ids, empty excerpts, or a quote that is not a verbatim
    substring of any cited response/event. Used by `argus verify` and by
    `argus report` (a re-render must not silently carry tampered claims)."""
    bad = []
    for f in findings:
        excerpt = (f.get("evidence_excerpt") or "").strip()
        ids = f.get("evidence_ids") or []
        cited = [entries.get(r) for r in ids]
        if not excerpt or not cited or None in cited or \
                not any(excerpt in _evidence_text_of_entry(e)
                        for e in cited):
            bad.append(f.get("id", "?"))
    return bad


def _evidence_text_of_entry(entry: dict | None) -> str:
    if not entry:
        return ""
    resp = entry.get("response") or {}
    return (resp.get("body") or "") or (entry.get("output") or "")


def _finding_key(category: str, url: str) -> tuple:
    """Dedup key: same bug class on the same endpoint+params is one finding."""
    cat = re.sub(r"[^a-z0-9]", "", (category or "").lower())
    p = urllib.parse.urlparse(url if "://" in url else "http://" + url)
    params = tuple(sorted(k for k, _ in urllib.parse.parse_qsl(p.query)))
    return (cat, p.netloc.lower(), p.path or "/", params)


# Audit-grade reports carry standard identifiers; the category the model
# names maps to the canonical CWE automatically (normalized: strip
# non-alphanumerics, so "info-disclosure" == "infodisclosure").
_CWE = {
    "sqli": "CWE-89", "nosqli": "CWE-943", "ssti": "CWE-1336",
    "time": "CWE-78", "cmdinjection": "CWE-78", "lfi": "CWE-22",
    "rfi": "CWE-98", "xss": "CWE-79", "reflection": "CWE-79",
    "idor": "CWE-639", "enum": "CWE-204", "enumeration": "CWE-204",
    "lockout": "CWE-307", "massassign": "CWE-915",
    "massassignment": "CWE-915", "ssrf": "CWE-918", "xxe": "CWE-611",
    "csrf": "CWE-352", "xfh": "CWE-444", "upload": "CWE-434",
    "race": "CWE-362", "deserialize": "CWE-502",
    "deserialization": "CWE-502", "cache": "CWE-525",
    "cachepoisoning": "CWE-525", "ppoll": "CWE-1321",
    "prototypepollution": "CWE-1321", "smuggle": "CWE-444",
    "requestsmuggling": "CWE-444", "disclosure": "CWE-200",
    "infodisclosure": "CWE-200", "websocket": "CWE-1385",
    "crlf": "CWE-113", "redirect": "CWE-601", "openredirect": "CWE-601",
    "cors": "CWE-942", "jwt": "CWE-347", "method": "CWE-749",
}


def _cwe_of(category: str) -> str:
    return _CWE.get(re.sub(r"[^a-z0-9]", "", (category or "").lower()), "")


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
}


def _owasp_of(cwe: str) -> str:
    return _OWASP.get(cwe or "", "")


class Session:
    def __init__(self, base_dir: Path, target: str, meta: dict,
                 resume: Path | None = None):
        self._lock = threading.Lock()
        if resume is not None:
            self._resume(Path(resume), target, meta)
            return
        host = urllib.parse.urlparse(target).hostname or "target"
        self.id = time.strftime("%Y%m%d-%H%M%S") + "-" + _slug(host)
        self.dir = Path(base_dir) / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.started = time.time()
        self._seq = 0
        self._transcript: dict[str, dict] = {}
        self.findings: list[dict] = []
        self.resumed = False
        self._last_chain = ""
        _atomic_write(
            self.dir / "meta.json",
            json.dumps({"id": self.id, "target": target,
                        "started": self.started, **meta},
                       indent=2, ensure_ascii=False))
        with (self.dir / "notes.md").open("w", encoding="utf-8",
                                          newline="") as fh:
            fh.write(f"# Working notes - {target}\n\n")

    def _resume(self, sdir: Path, target: str, meta: dict) -> None:
        """Continue an existing session dir: transcript, findings and request
        ids all carry over, so the evidence chain and dedup stay intact."""
        if not sdir.is_dir():
            raise FileNotFoundError(f"cannot resume: {sdir} is not a session dir")
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
            self.started = float(old.get("started") or self.started)
            old_target = old.get("target")
            # resuming against a different target would conflate two
            # engagements' evidence and findings - refuse loudly
            if old_target and old_target != target:
                raise ValueError(
                    f"cannot resume {sdir.name}: session target "
                    f"{old_target!r} != current target {target!r}")
        tpath = sdir / "transcript.jsonl"
        if tpath.exists():
            for line in tpath.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                self._transcript[entry["id"]] = entry
                if entry.get("chain"):
                    self._last_chain = entry["chain"]
                suffix = entry["id"][1:]
                if suffix.isdigit():
                    self._seq = max(self._seq, int(suffix))
        fpath = sdir / "findings.json"
        if fpath.exists():
            try:
                self.findings = json.loads(fpath.read_text(encoding="utf-8"))
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
            entry = {
                "id": rid,
                "ts": round(time.time(), 3),
                "tool": tool,
                "request": request,
                "response": response,
            }
            if agent:
                entry["agent"] = agent
            if note:
                entry["note"] = note
            entry["chain"] = _chain(self._last_chain, entry)
            self._last_chain = entry["chain"]
            self._transcript[rid] = entry
            with self.transcript_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return rid

    def record_event(self, kind: str, detail: dict, agent: str = "") -> str:
        """Record a non-HTTP event (external tool run, error). Returns r<n>."""
        with self._lock:
            self._seq += 1
            rid = f"r{self._seq}"
            entry = {"id": rid, "ts": round(time.time(), 3), "kind": kind, **detail}
            if agent:
                entry["agent"] = agent
            entry["chain"] = _chain(self._last_chain, entry)
            self._last_chain = entry["chain"]
            self._transcript[rid] = entry
            with self.transcript_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
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
            entry["chain"] = _chain(self._last_chain, entry)
            self._last_chain = entry["chain"]
            self._transcript["seal"] = entry
            with self.transcript_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        rid = "seal"
        if sp.exists():
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
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
        if not entry:
            return ""
        resp = entry.get("response") or {}
        body = resp.get("body", "") or ""
        if body:
            return body
        return entry.get("output", "") or ""

    def evidence_text(self, rid: str) -> str:
        """Verbatim bytes a finding may quote: response body or event output."""
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
        severity = severity.lower()
        if severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        cvss = (cvss or "").strip()
        if cvss and not _CVSS_RE.match(cvss):
            raise ValueError(
                "cvss must be a base vector like "
                "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        excerpt = (evidence_excerpt or "").strip()
        if not excerpt:
            raise ValueError("evidence_excerpt must quote the proving bytes")
        with self._lock:  # snapshot: other workers keep appending mid-check
            transcript_snapshot = dict(self._transcript)
        if not evidence_ids:
            # Resolve the proving exchange from the excerpt itself - the
            # verbatim gate is unchanged: the quote must exist in a recorded
            # response/event. Cite the first entry that contains it.
            evidence_ids = [r for r in transcript_snapshot
                            if excerpt in self._evidence_text_of(
                                transcript_snapshot.get(r))][:1]
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
        key = _finding_key(category, url)
        with self._lock:
            for existing in self.findings:
                if _finding_key(existing["category"], existing["url"]) == key:
                    raise ValueError(
                        f"duplicate of {existing['id']} ({category} on {url}); "
                        "same bug class + endpoint is one finding - put extra "
                        "evidence in note() instead")
            finding = {
                "id": f"F{len(self.findings) + 1:02d}",
                "title": title.strip(),
                "severity": severity,
                "category": category.strip(),
                "url": url,
                "evidence_ids": evidence_ids,
                "evidence_excerpt": excerpt[:2000],
                "description": description.strip(),
                "remediation": remediation.strip(),
                "ts": round(time.time(), 3),
            }
            if agent:
                finding["agent"] = agent
            if cvss:
                finding["cvss"] = cvss
            cwe = _cwe_of(category)
            if cwe:
                finding["cwe"] = cwe
                owasp = _owasp_of(cwe)
                if owasp:
                    finding["owasp"] = owasp
            self.findings.append(finding)
            _atomic_write(
                self.findings_path,
                json.dumps(self.findings, indent=2, ensure_ascii=False))
        return finding

    def note(self, text: str, agent: str = "") -> None:
        stamp = time.strftime("%H:%M:%S")
        prefix = f"- **[{stamp} {agent}]** " if agent else \
            f"- **[{stamp}]** " if not text.startswith(
                ("#", ">", "-", "*")) else ""
        with self._lock:
            with self.notes_path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(prefix + text.rstrip() + "\n\n")

    def stats(self) -> dict:
        return {
            "requests": self._seq,
            "findings": len(self.findings),
            "elapsed_s": round(time.time() - self.started, 1),
        }
