"""ScopeGuard: the boundary every request passes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.scope import ScopeError, ScopeGuard


def test_in_scope_host_ok():
    g = ScopeGuard("https://target.example/app", allow_private=False)
    g.check("https://target.example/login?next=/x")


def test_out_of_scope_host_denied():
    g = ScopeGuard("https://target.example", allow_private=False)
    with pytest.raises(ScopeError):
        g.check("https://evil.example/")


def test_subdomain_allowed_by_default():
    g = ScopeGuard("https://target.example", allow_private=False)
    g.check("https://api.target.example/")


def test_scheme_restricted():
    g = ScopeGuard("https://target.example")
    for bad in ("file:///etc/passwd", "gopher://x/", "ftp://target.example/"):
        with pytest.raises(ScopeError):
            g.check(bad)


def test_extra_hosts():
    g = ScopeGuard("https://a.example", extra_hosts=["b.example"],
                   allow_private=False)
    g.check("https://b.example/api")


def test_excluded_path_denied():
    g = ScopeGuard("https://target.example", exclude_paths=["/logout", "/admin"],
                   allow_private=False)
    with pytest.raises(ScopeError):
        g.check("https://target.example/logout")
    with pytest.raises(ScopeError):
        g.check("https://target.example/admin/reset")
    g.check("https://target.example/administer")  # prefix boundary


def test_private_refused_by_default():
    g = ScopeGuard("https://target.example", extra_hosts=["internal.example"],
                   allow_private=False)
    g._private_cache["internal.example"] = True
    with pytest.raises(ScopeError):
        g.check("http://internal.example/")


def test_private_target_autoallows():
    g = ScopeGuard("http://127.0.0.1:8777")
    assert g.allow_private
    g.check("http://127.0.0.1:8777/")
