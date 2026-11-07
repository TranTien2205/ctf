"""Session store: transcript, findings, notes - the evidence layer.

Everything the agent observes is written to disk under sessions/<id>/ so a
run is auditable and resumable. Findings are only accepted when their evidence
excerpt is a verbatim substring of a recorded response - the quote is checked,
not trusted.
"""
from __future__ import annotations

import json
import re
import threading
import time
import urllib.parse
from pathlib import Path

SEVERITIES = ("critical", "high", "medium", "low", "info")


def _slug(host: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.-]+", "_", host)[:60]


def _finding_key(category: str, url: str) -> tuple:
    """Dedup key: same bug class on the same endpoint+params is one finding."""
    cat = re.sub(r"[^a-z0-9]", "", (category or "").lower())
    p = urllib.parse.urlparse(url if "://" in url else "http://" + url)
    params = tuple(sorted(k for k, _ in urllib.parse.parse_qsl(p.query)))
    return (cat, p.netloc.lower(), p.path or "/", params)


class Session:
    def __init__(self, base_dir: Path, target: str, meta: dict):
        host = urllib.parse.urlparse(target).hostname or "target"
        self.id = time.strftime("%Y%m%d-%H%M%S") + "-" + _slug(host)
        self.dir = Path(base_dir) / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.started = time.time()
        self._seq = 0
        self._transcript: dict[str, dict] = {}
        self.findings: list[dict] = []
        self._lock = threading.Lock()
        (self.dir / "meta.json").write_text(
            json.dumps({"id": self.id, "target": target, "started": self.started, **meta},
                       indent=2, ensure_ascii=False)
        )
        (self.dir / "notes.md").write_text(f"# Working notes - {target}\n\n")

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
            self._transcript[rid] = entry
            with self.transcript_path.open("a", encoding="utf-8") as fh:
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
            self._transcript[rid] = entry
            with self.transcript_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return rid

    def get_exchange(self, rid: str) -> dict | None:
        return self._transcript.get(rid)

    def response_body(self, rid: str) -> str:
        entry = self._transcript.get(rid)
        if not entry:
            return ""
        resp = entry.get("response") or {}
        return resp.get("body", "") or ""

    def evidence_text(self, rid: str) -> str:
        """Verbatim bytes a finding may quote: response body or event output."""
        entry = self._transcript.get(rid)
        if not entry:
            return ""
        resp = entry.get("response") or {}
        body = resp.get("body", "") or ""
        if body:
            return body
        return entry.get("output", "") or ""

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
    ) -> dict:
        severity = severity.lower()
        if severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        if not evidence_ids:
            raise ValueError("a finding needs at least one evidence request id")
        unknown = [r for r in evidence_ids if r not in self._transcript]
        if unknown:
            raise ValueError(f"unknown evidence request ids: {unknown}")
        excerpt = (evidence_excerpt or "").strip()
        if not excerpt:
            raise ValueError("evidence_excerpt must quote the proving bytes")
        if not any(excerpt in self.evidence_text(r) for r in evidence_ids):
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
            self.findings.append(finding)
            self.findings_path.write_text(
                json.dumps(self.findings, indent=2, ensure_ascii=False)
            )
        return finding

    def note(self, text: str) -> None:
        with self._lock:
            with self.notes_path.open("a", encoding="utf-8") as fh:
                fh.write(text.rstrip() + "\n\n")

    def stats(self) -> dict:
        return {
            "requests": self._seq,
            "findings": len(self.findings),
            "elapsed_s": round(time.time() - self.started, 1),
        }
