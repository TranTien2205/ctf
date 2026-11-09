#!/usr/bin/env python3
"""browser_hist.py -- read Chrome/Firefox history artifacts (stdlib).

Usage:
  python3 tools/forensics/browser_hist.py History
  python3 tools/forensics/browser_hist.py places.sqlite
  python3 tools/forensics/browser_hist.py --selftest

Chrome History: urls + visits joined on url id; timestamps are
WebKit epoch (microseconds since 1601). Firefox places.sqlite:
moz_places + moz_historyvisits; timestamps are unix microseconds.
Downloads: Chrome downloads/downloads_url_chains, Firefox
moz_annos (file destination). Cookies: cookies/moz_cookies.
Schema is detected by table names; unknown schemas report tables.
"""
import argparse
import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

WEBKIT = datetime(1601, 1, 1)
UNIX = datetime(1970, 1, 1)


def _wkit(us):
    return (WEBKIT + timedelta(microseconds=us)).isoformat() if us else None


def _unix(us):
    return (UNIX + timedelta(microseconds=us)).isoformat() if us else None


def _q(db, sql):
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error:
        return []


def read(path):
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    tables = {r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    out = {}
    if "urls" in tables and "visits" in tables:      # Chrome
        out["kind"] = "chrome"
        out["visits"] = [{"url": u, "time": _wkit(t),
                          "title": ti}
                         for u, t, ti in _q(db,
                            "SELECT urls.url, visits.visit_time,"
                            " urls.title FROM visits JOIN urls ON"
                            " urls.id = visits.url ORDER BY"
                            " visits.visit_time DESC LIMIT 500")]
        out["downloads"] = [{"url": c, "path": d,
                             "start": _wkit(s)}
                            for c, d, s in _q(db,
                               "SELECT chains.url, d.target_path,"
                               " d.start_time FROM"
                               " downloads_url_chains chains JOIN"
                               " downloads d ON d.id = chains.id")]
        out["cookies"] = [{"host": h, "name": n,
                           "expires": _wkit(e)}
                          for h, n, e in _q(db,
                             "SELECT host_key, name,"
                             " expires_utc FROM cookies LIMIT 300")]
    elif "moz_places" in tables:                     # Firefox
        out["kind"] = "firefox"
        out["visits"] = [{"url": u, "time": _unix(t),
                          "title": ti}
                         for u, t, ti in _q(db,
                            "SELECT p.url, v.visit_date, p.title"
                            " FROM moz_historyvisits v JOIN"
                            " moz_places p ON p.id = v.place_id"
                            " ORDER BY v.visit_date DESC LIMIT 500")]
        out["downloads"] = [{"url": u, "path": a}
                            for u, a in _q(db,
                               "SELECT p.url, a.content FROM"
                               " moz_annos a JOIN moz_places p ON"
                               " p.id = a.place_id WHERE"
                               " a.anno_attribute_id = (SELECT id"
                               " FROM moz_anno_attributes WHERE"
                               " name='downloads/destinationFileURI')"
                               )]
        out["cookies"] = [{"host": h, "name": n,
                           "expires": e}
                          for h, n, e in _q(db,
                             "SELECT host, name, expiry FROM"
                             " moz_cookies LIMIT 300")]
    else:
        out["kind"] = "unknown"
        out["tables"] = sorted(tables)
    db.close()
    return out


def _selftest():
    d = Path(tempfile.mkdtemp()) / "History"
    db = sqlite3.connect(d)
    db.executescript(
        "CREATE TABLE urls(id INTEGER PRIMARY KEY, url TEXT,"
        " title TEXT);"
        "CREATE TABLE visits(id INTEGER PRIMARY KEY, url INTEGER,"
        " visit_time INTEGER);"
        "CREATE TABLE downloads(id INTEGER PRIMARY KEY,"
        " target_path TEXT, start_time INTEGER);"
        "CREATE TABLE downloads_url_chains(id INTEGER, url TEXT);"
        "CREATE TABLE cookies(host_key TEXT, name TEXT,"
        " expires_utc INTEGER);"
        "INSERT INTO urls VALUES(1,'https://x/flag{hist}','t');"
        "INSERT INTO visits VALUES(1,1,13300000000000000);"
        "INSERT INTO downloads VALUES(1,'c:\\f.bin',13300e12);"
        "INSERT INTO downloads_url_chains VALUES(1,'https://x/f');"
        "INSERT INTO cookies VALUES('.x','sess',13400e12);")
    db.close()
    out = read(d)
    assert out["kind"] == "chrome", out
    assert "flag{hist}" in out["visits"][0]["url"], out
    assert out["visits"][0]["time"].startswith("2022-"), out
    assert out["downloads"] and out["cookies"], out
    print("browser_hist selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="read Chrome/Firefox history artifacts")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    print(json.dumps(read(a.file), indent=1, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
