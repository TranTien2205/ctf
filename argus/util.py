"""Small shared helpers. No third-party imports anywhere in this file."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

SLUG_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,99}\Z")

# Patterns redacted from anything written to disk or shown to a model. Secrets
# reach this system through tool output (JS bundles, dumps, config files), not
# only through configuration, so redaction happens on the write path.
_SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"), "sk-ant-REDACTED"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "sk-REDACTED"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AKIA-REDACTED"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "ghp-REDACTED"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "AIza-REDACTED"),
    (re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}"), "xox-REDACTED"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "jwt-REDACTED"),
]


def now() -> float:
    return time.time()


def now_iso(stamp: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stamp if stamp is not None else time.time()))


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def check_slug(value: str, what: str = "name") -> str:
    """A name that becomes a directory. ASCII, lowercase, no traversal."""
    low = (value or "").strip().lower()
    if not SLUG_RE.match(low):
        raise ValueError(
            f"{what} must be 1-100 chars of a-z 0-9 . _ - and start alphanumeric: {value!r}"
        )
    return low


def redact(text: str) -> str:
    out = text
    for pattern, replacement in _SECRET_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def bound(text: str, limit: int, tail: int = 0) -> str:
    """Keep a bounded span of text. Truncation is always announced in-band."""
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    cut = len(text) - limit
    if tail and limit > tail:
        head = limit - tail
        return f"{text[:head]}\n... [{cut} chars elided] ...\n{text[-tail:]}"
    return f"{text[:limit]}\n... [{cut} chars elided]"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def sha256_file(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: str | os.PathLike[str], data: Any) -> None:
    """Atomic, fsynced, same-directory replace. Readers never see a half file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=target.parent, delete=False
        ) as handle:
            temporary = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False, sort_keys=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: str | os.PathLike[str], default: Any = None) -> Any:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def append_jsonl(path: str | os.PathLike[str], record: dict) -> None:
    """Append one event. O_APPEND on a line under the pipe buffer is atomic
    enough for several concurrent agents, which is the whole point of the bus."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # `default=str` rather than a raised TypeError: an append-only log exists to
    # record what happened, and losing a run because one payload field was an
    # object is the wrong trade.
    line = json.dumps(record, ensure_ascii=False, allow_nan=False, default=str) + "\n"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def read_jsonl(path: str | os.PathLike[str], limit: int | None = None) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        return []
    if limit is not None:
        lines = lines[-limit:]
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
