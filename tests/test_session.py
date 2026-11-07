"""Evidence gating: findings only accept verbatim recorded bytes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.session import Session


def _sess(tmp_path):
    return Session(tmp_path, "http://t.local", meta={})


def test_finding_requires_verbatim_evidence(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {"method": "GET", "url": "http://t/x"},
                            {"status": 200, "body": "root:x:0:0 root"})
    s.add_finding("lfi", "high", "file-read", "http://t/x", [rid],
                  "root:x:0:0", "desc", "fix")
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "http://t/x", [rid],
                      "invented excerpt not in body", "d", "r")


def test_finding_requires_known_ids(tmp_path):
    s = _sess(tmp_path)
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "u", ["r99"], "x", "d", "r")


def test_finding_requires_some_evidence(tmp_path):
    s = _sess(tmp_path)
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "u", [], "x", "d", "r")


def test_severity_enum(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    with pytest.raises(ValueError):
        s.add_finding("bad", "superultra", "x", "u", [rid], "proof", "d", "r")


def test_finding_dedup_same_class_endpoint(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    s.add_finding("sqli on /item", "high", "SQLi", "http://t/item?id=1",
                  [rid], "proof", "d", "r")
    # same bug class + same endpoint+params = duplicate, even with new evidence
    with pytest.raises(ValueError, match="duplicate of F01"):
        s.add_finding("sqli again", "medium", "sqli",
                      "http://t/item?id=2", [rid], "proof", "d", "r")
    # a different parameter IS a distinct finding
    f = s.add_finding("sqli on q", "high", "sqli", "http://t/item?q=x",
                      [rid], "proof", "d", "r")
    assert f["id"] == "F02"


def test_finding_records_agent(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    f = s.add_finding("x", "low", "c", "http://t/a", [rid], "proof", "d", "r",
                      agent="exploit-2")
    assert f["agent"] == "exploit-2"
