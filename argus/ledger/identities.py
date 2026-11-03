"""The identity store: who this engagement can act as.

An engagement is not one caller. `idor`, `csrf` and `auth-bypass` are claims
about *two* callers, and a tester holding one set of cookies cannot make them: a
`200` on `id=2` means nothing without the identity that should not have been
able to read it and the identity that should. Before this module, credentials
were passed per tool call, which made the second identity something the model
had to carry in its context — and a model that is remembering a cookie has
stopped reading the ledger.

So identities live on disk beside the evidence they make provable. One identity
is a name, how it authenticates, the material it authenticates with, when that
material was obtained, and the recipe for obtaining it again.

**This is the one file in argus that holds a real secret.** Everything else is
redacted on the write path — `argus.util.redact` runs inside
`State.add_evidence`, because a credential that reaches the ledger reaches the
report. A credential store cannot redact what it stores and still be useful, so
it carries three restrictions instead:

* it is the only file that holds the value, and it is written `0600`;
* nothing it hands to a model or to an evidence record contains the value.
  `describe()` returns the shape — scheme, field, length, last four — and
  `digest()` takes no argument at all, so there is nothing to opt into;
* the tools in `argus/broker/servers/session.py` strip the material out of the
  request record before the ledger sees it, because
  `httpkit.HttpResponse.to_evidence()` keeps the request headers verbatim and
  `redact()` cannot tell an opaque session cookie from a session id.

The restriction easiest to lose is the second. `describe()` is a separate method
rather than a flag on `to_json()` because a flag has a default, and a default
that leaks leaks quietly.

What this module will not do: it does not crack, spray, reuse or escalate a
credential. It records one the operator already has, or one a login endpoint
hands back when it is given one. A store that could *obtain* credentials it was
not given would be a credential-attack tool, which this repository does not
help with.
"""
from __future__ import annotations

import base64
import calendar
import dataclasses
import os
import time
from dataclasses import dataclass
from pathlib import Path

from .. import config
from ..util import check_slug, now_iso, read_json, write_json
from .lock import engagement_lock

FILENAME = "identities.json"

# The control identity. Every authorization claim needs the request that carried
# no credential at all, so this name is reserved and always resolvable: an
# engagement that forgot to create it would silently lose the one record that
# makes the asymmetry mean anything. It is also the *only* identity that may
# carry nothing, in both directions: a credential under this name would make
# every later "control" carry a cookie, and a credential-less identity under any
# other name would put a borrowed `actor` on an anonymous request.
UNAUTHENTICATED = "unauthenticated"

SCHEMES = ("cookie", "bearer", "basic", "header", "query", "none")

# Four characters of a long opaque token identify it without reconstructing it.
# Four characters of a short one are most of it, so a short value shows none.
TAIL_FLOOR = 12

FILE_NOTE = ("This file holds real credential material for one engagement. It is the only file in "
             "argus that does. It is written 0600, it lives under engagements/ which is never "
             "committed, and no value in it may be copied into evidence, a digest or a report — "
             "use identities.describe() for anything a model or a reader sees.")


# --- time --------------------------------------------------------------------

def iso_in(seconds: float) -> str:
    """An absolute stamp `seconds` from now, in the format the ledger uses."""
    return now_iso(time.time() + float(seconds))


def _epoch(stamp: str | None) -> float | None:
    if not stamp:
        return None
    try:
        return calendar.timegm(time.strptime(str(stamp), "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None


# --- one identity ------------------------------------------------------------

@dataclass
class Identity:
    """One caller. `value` and `renew` are the secret halves and are kept out of
    `repr`, so an identity that lands in a traceback or a log line does not take
    the credential with it."""

    name: str
    scheme: str = "none"
    field: str = ""
    value: str = dataclasses.field(default="", repr=False)
    note: str = ""
    obtained: str = ""
    expires: str | None = None
    entitled_to: tuple[str, ...] = ()
    not_entitled_to: tuple[str, ...] = ()
    # How to obtain this credential again: the login request, the success marker
    # and the capture rule. It contains the login body, so it is as secret as the
    # value and is excluded from describe() for the same reason.
    renew: dict | None = dataclasses.field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.name = check_slug(self.name, "identity name")
        self.scheme = (self.scheme or "none").strip().lower()
        if self.scheme not in SCHEMES:
            raise ValueError(f"unknown scheme {self.scheme!r}; one of {list(SCHEMES)}")
        if self.scheme in ("header", "query") and not self.field:
            raise ValueError(f"scheme {self.scheme!r} needs `field`: the name of the "
                             f"{'header' if self.scheme == 'header' else 'query parameter'} "
                             f"that carries the credential")
        if self.scheme != "none" and not self.value:
            raise ValueError(f"identity {self.name!r} claims scheme {self.scheme!r} but carries no "
                             f"value; use scheme 'none' for the unauthenticated control")
        if self.name == UNAUTHENTICATED and self.scheme != "none":
            # Overwriting the control with a credentialled identity destroys the
            # one record an authorization proof cannot be assembled without, and
            # the failure is silent: every subsequent "control" carries a cookie.
            raise ValueError(f"{UNAUTHENTICATED!r} is the reserved control identity and must carry "
                             f"no credential; name a credentialled identity something else")
        if self.scheme == "none" and self.name != UNAUTHENTICATED:
            # The mirror of the check above, and the one that is easier to trip.
            # An identity named `alice` that carries nothing issues anonymous
            # requests while `actor: alice` goes into every record, and two of
            # them satisfy "two distinct actors" on two identical anonymous
            # requests — a differential proof of nothing, assembled without a
            # single credential. `session.login` could produce one too, by being
            # passed scheme='none' for a capture that did find a value.
            raise ValueError(f"identity {self.name!r} would carry no credential, and only "
                             f"{UNAUTHENTICATED!r} may do that: requests issued as it are "
                             f"anonymous, while the evidence record says the actor was "
                             f"{self.name!r}. Give it a value and a scheme, or use "
                             f"{UNAUTHENTICATED!r}, which always exists, as the control")
        self.entitled_to = tuple(str(s) for s in (self.entitled_to or ()))
        self.not_entitled_to = tuple(str(s) for s in (self.not_entitled_to or ()))
        self.obtained = self.obtained or now_iso()

    # --- the safe view -------------------------------------------------------

    def describe(self) -> dict:
        """The only representation of an identity that may leave this module.

        Shape, never material: the scheme and field, so a reviewer can tell a
        cookie identity from a bearer one; the length and last four characters,
        so a record can be tied back to the credential that produced it; the
        entitlements, so an authorization claim can say *why* the actor should
        not have succeeded. No argument widens this, by construction.
        """
        return {
            "name": self.name,
            "scheme": self.scheme,
            "field": self.field,
            "value_length": len(self.value),
            "last4": self.value[-4:] if len(self.value) >= TAIL_FLOOR else "",
            "obtained": self.obtained,
            "age_seconds": self.age_seconds(),
            "expires": self.expires,
            "stale": self.stale(),
            "renewable": bool(self.renew),
            # The login endpoint, not the login body. The URL is not credential
            # material and `session.refresh` needs it restated so the broker can
            # scope-check the target before the request is built.
            "renew_url": (self.renew or {}).get("url"),
            "entitled_to": list(self.entitled_to),
            "not_entitled_to": list(self.not_entitled_to),
            "note": self.note,
        }

    def line(self) -> str:
        """One line for a model to read. describe() with no punctuation budget."""
        shape = self.describe()
        where = f"{self.scheme}" + (f":{self.field}" if self.field else "")
        material = ("no credential" if not self.value else
                    f"{shape['value_length']}ch …{shape['last4']}" if shape["last4"] else
                    f"{shape['value_length']}ch")
        flags = [f for f in ("stale" if self.stale() else "",
                             "renewable" if self.renew else "") if f]
        return (f"{self.name:<16} {where:<22} {material:<14} obtained {self.obtained}"
                + (f" [{', '.join(flags)}]" if flags else "")
                + (f" not-entitled-to {', '.join(self.not_entitled_to)}"
                   if self.not_entitled_to else ""))

    # --- expiry --------------------------------------------------------------

    def age_seconds(self) -> int | None:
        obtained = _epoch(self.obtained)
        return None if obtained is None else max(0, int(time.time() - obtained))

    def stale(self) -> bool:
        """True only when an expiry was *observed* and has passed.

        An identity with no `expires` is never reported stale. The server's
        session timeout is not knowable from here, and inventing a default TTL
        would make the store assert something it never measured — exactly the
        failure the rest of this system exists to prevent. What is knowable is
        how long ago the credential was obtained, which `describe()` reports, and
        what the target says when it is used, which `session.probe_as` records: a
        401 or a login redirect is the observation that establishes expiry.
        """
        expires = _epoch(self.expires)
        return expires is not None and expires <= time.time()

    # --- use -----------------------------------------------------------------

    def request_kwargs(self) -> dict:
        """What `argus.broker.httpkit.request` needs to issue a request as this
        identity. A tool never builds an auth header itself: one place that knows
        `Authorization: Bearer` from `Cookie:` is one place to get it wrong."""
        if self.scheme == "none" or not self.value:
            return {}
        if self.scheme == "cookie":
            return {"cookies": f"{self.field or 'session'}={self.value}"}
        if self.scheme == "bearer":
            name = self.field or "Authorization"
            return {"headers": {name: f"Bearer {self.value}"
                                if name.lower() == "authorization" else self.value}}
        if self.scheme == "basic":
            # `value` is `user:password`; it is encoded here rather than stored
            # encoded so the store holds one canonical form of the material.
            return {"headers": {self.field or "Authorization":
                                "Basic " + base64.b64encode(self.value.encode()).decode()}}
        if self.scheme == "header":
            return {"headers": {self.field: self.value}}
        if self.scheme == "query":
            # Not an authentication scheme. Some applications take the caller's
            # name in a query parameter and trust it, which is the vulnerability
            # rather than the credential; expressing it here is what lets the
            # authorization tools probe such an application without pretending it
            # issued a token.
            return {"params": {self.field: self.value}}
        raise ValueError(f"unknown scheme {self.scheme!r}")

    def material(self) -> tuple[str, ...]:
        """Every string a tool must strip out of a request record before the
        ledger sees it. Longest first, so the fuller form is withheld first."""
        if not self.value:
            return ()
        forms = {self.value}
        if self.scheme == "basic":
            forms.add(base64.b64encode(self.value.encode()).decode())
        return tuple(sorted(forms, key=len, reverse=True))

    def entitlement(self, subject: str) -> str:
        """`entitled`, `not-entitled`, or `undeclared`. The third is honest: an
        authorization finding whose entitlement was never declared rests on the
        tester's assumption about who owns what, and the report should say so."""
        subject = str(subject or "")
        if subject in self.not_entitled_to:
            return "not-entitled"
        if subject in self.entitled_to:
            return "entitled"
        return "undeclared"

    # --- disk ----------------------------------------------------------------

    def to_json(self) -> dict:
        return {"name": self.name, "scheme": self.scheme, "field": self.field,
                "value": self.value, "note": self.note, "obtained": self.obtained,
                "expires": self.expires, "entitled_to": list(self.entitled_to),
                "not_entitled_to": list(self.not_entitled_to), "renew": self.renew}

    @classmethod
    def from_json(cls, data: dict) -> "Identity":
        return cls(name=data.get("name", ""), scheme=data.get("scheme", "none"),
                   field=data.get("field", "") or "", value=data.get("value", "") or "",
                   note=data.get("note", "") or "", obtained=data.get("obtained", "") or "",
                   expires=data.get("expires"), entitled_to=tuple(data.get("entitled_to") or ()),
                   not_entitled_to=tuple(data.get("not_entitled_to") or ()),
                   renew=data.get("renew"))


def unauthenticated() -> Identity:
    """The control. Synthesised rather than stored, so it cannot be missing."""
    return Identity(name=UNAUTHENTICATED, scheme="none",
                    note="the control: the same request carrying no credential at all")


# --- the store ---------------------------------------------------------------

def store_path(engagement: str) -> Path:
    paths = config.Paths(engagement)
    # `Paths` is meant to be the only place that knows an engagement's filenames.
    # Until `identities` is a field there, read it if present and fall back, so
    # adding the field needs no change here.
    return Path(getattr(paths, "identities", paths.dir / FILENAME))


@dataclass
class IdentityStore:
    """A read-only view of one engagement's identities. Mutation goes through the
    module-level verbs below, which re-read under the engagement lock: several
    agents share one engagement, and load-mutate-save without the lock loses
    whichever write finished first."""

    engagement: str
    path: Path
    identities: dict[str, Identity] = dataclasses.field(default_factory=dict)

    @classmethod
    def load(cls, engagement: str) -> "IdentityStore":
        path = store_path(engagement)
        data = read_json(path, {}) or {}
        found: dict[str, Identity] = {}
        for entry in data.get("identities") or []:
            try:
                identity = Identity.from_json(entry)
            except (ValueError, TypeError, AttributeError):
                # A hand-edited file should not take the whole store down: skip
                # the entry, and `session.list` will simply not show it. The two
                # extra exceptions are what a hand edit actually produces — a
                # numeric name reaches `check_slug` as an int and a mistyped
                # list reaches `from_json` as a string — and catching only
                # ValueError left every session tool in the engagement failing
                # on a file the operator could not see was wrong.
                continue
            found[identity.name] = identity
        return cls(engagement=engagement, path=path, identities=found)

    # --- reading -------------------------------------------------------------

    def get(self, name: str) -> Identity | None:
        name = (name or "").strip().lower()
        if name == UNAUTHENTICATED and name not in self.identities:
            return unauthenticated()
        return self.identities.get(name)

    def names(self) -> list[str]:
        return sorted({*self.identities, UNAUTHENTICATED})

    def all(self) -> list[Identity]:
        return [self.get(name) for name in self.names()]

    def describe_all(self) -> list[dict]:
        return [identity.describe() for identity in self.all()]

    def digest(self) -> dict:
        """The identity plane as the model sees it. No parameters: there is no
        argument that could ask this for a credential value."""
        described = self.describe_all()
        return {"count": len(described),
                "identities": described,
                "stale": [d["name"] for d in described if d["stale"]],
                "schemes": sorted({d["scheme"] for d in described})}

    def as_request_kwargs(self, name: str) -> dict:
        identity = self.get(name)
        if identity is None:
            raise KeyError(f"no identity {name!r} in engagement {self.engagement!r}; "
                           f"have {self.names()}")
        return identity.request_kwargs()

    # --- writing -------------------------------------------------------------

    def write(self) -> None:
        payload = {"version": 1, "note": FILE_NOTE, "engagement": self.engagement,
                   "updated": now_iso(),
                   "identities": [i.to_json() for i in self.identities.values()]}
        write_json(self.path, payload)
        # write_json replaces a NamedTemporaryFile, which is already 0600, so this
        # is belt and braces — and a statement of intent that survives someone
        # changing how write_json makes its temporary file.
        os.chmod(self.path, 0o600)


def put(engagement: str, identity: Identity) -> Identity:
    """Record or replace one identity, under the engagement lock."""
    with engagement_lock(config.Paths(engagement).dir):
        store = IdentityStore.load(engagement)
        store.identities[identity.name] = identity
        store.write()
    return identity


def update(engagement: str, name: str, **changes) -> Identity:
    """Replace the mutable fields of a stored identity. Used by `session.refresh`
    to swap in new material without losing the entitlements or the login recipe."""
    with engagement_lock(config.Paths(engagement).dir):
        store = IdentityStore.load(engagement)
        current = store.identities.get((name or "").strip().lower())
        if current is None:
            raise KeyError(f"no identity {name!r} to update; have {store.names()}")
        updated = dataclasses.replace(current, **changes)
        store.identities[updated.name] = updated
        store.write()
    return updated


def get(engagement: str, name: str) -> Identity | None:
    return IdentityStore.load(engagement).get(name)


def request_kwargs(engagement: str, name: str) -> dict:
    return IdentityStore.load(engagement).as_request_kwargs(name)


def digest(engagement: str) -> dict:
    return IdentityStore.load(engagement).digest()
